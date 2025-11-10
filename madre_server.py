"""
Servidor API REST para Aplicación Madre (Entrenador Personal)
Implementa FastAPI con validación Pydantic, rate limiting, autenticación JWT
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import jwt
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from madre_db import gestor_bd, Alumno, Rutina
from config.settings import config
from shared.logger import obtener_logger

# Configurar logger
logger = obtener_logger(__name__)

# Configurar rate limiter
limiter = Limiter(key_func=get_remote_address)

# Crear aplicación FastAPI
app = FastAPI(
    title="API Gestión de Gimnasio - Entrenador Personal",
    description="API REST para gestión completa de gimnasio y entrenamiento personalizado",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Agregar middleware de rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# MODELOS PYDANTIC PARA VALIDACIÓN
# ============================================================================

class UsuarioLogin(BaseModel):
    """Modelo para login de usuario"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Contraseña mínimo 8 caracteres")


class UsuarioCrear(BaseModel):
    """Modelo para crear nuevo usuario"""
    nombre: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    telefono: str = Field(default="", max_length=20)
    equipo: str = Field(default="", max_length=50)
    nivel: str = Field(default="principiante", pattern="^(principiante|intermedio|avanzado)$")
    
    @validator('nombre')
    def validar_nombre(cls, v):
        if not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip()


class RutinaCrear(BaseModel):
    """Modelo para crear rutina de entrenamiento"""
    nombre: str = Field(..., min_length=3, max_length=100)
    descripcion: str = Field(default="")
    nivel_dificultad: str = Field(..., pattern="^(principiante|intermedio|avanzado)$")
    duracion_minutos: int = Field(..., gt=0, le=300, description="Duración entre 1 y 300 minutos")
    ejercicios: List[Dict] = Field(default_factory=list)
    creador_id: int = Field(..., gt=0)


class EvaluacionCrear(BaseModel):
    """Modelo para registrar evaluación corporal"""
    alumno_id: int = Field(..., gt=0)
    peso_kg: float = Field(..., gt=0, le=300)
    altura_cm: float = Field(..., gt=50, le=250)
    porcentaje_grasa: Optional[float] = Field(None, ge=0, le=100)
    masa_muscular_kg: Optional[float] = Field(None, gt=0, le=200)
    medidas: Optional[Dict] = None
    notas: str = Field(default="")
    evaluador_id: Optional[int] = None


class PagoCrear(BaseModel):
    """Modelo para registrar pago"""
    alumno_id: int = Field(..., gt=0)
    monto: float = Field(..., gt=0)
    tipo_membresia: str = Field(..., min_length=3)
    periodo_inicio: str = Field(..., description="Fecha en formato ISO")
    periodo_fin: str = Field(..., description="Fecha en formato ISO")
    metodo_pago: str = Field(default="efectivo", pattern="^(efectivo|tarjeta|transferencia)$")


class MensajeCrear(BaseModel):
    """Modelo para enviar mensaje"""
    remitente_id: int = Field(..., gt=0)
    destinatario_id: int = Field(..., gt=0)
    asunto: str = Field(..., min_length=1, max_length=200)
    contenido: str = Field(..., min_length=1)
    tipo: str = Field(default="personal", pattern="^(personal|grupal|anuncio)$")


class RespuestaBase(BaseModel):
    """Modelo base para respuestas exitosas"""
    exito: bool = True
    mensaje: str
    datos: Optional[Dict] = None


class RespuestaError(BaseModel):
    """Modelo para respuestas de error"""
    exito: bool = False
    error: str
    codigo: str
    detalles: Optional[Dict] = None


# ============================================================================
# UTILIDADES Y MIDDLEWARE
# ============================================================================

def crear_token_jwt(usuario_id: int, email: str) -> str:
    """Crear token JWT para autenticación"""
    expiracion = datetime.utcnow() + timedelta(hours=config.JWT_EXPIRATION_HOURS)
    payload = {
        'usuario_id': usuario_id,
        'email': email,
        'exp': expiracion,
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, config.SECRET_KEY, algorithm=config.JWT_ALGORITHM)
    return token


def verificar_token_jwt(token: str) -> Dict:
    """Verificar y decodificar token JWT"""
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )


@app.middleware("http")
async def middleware_logging(request: Request, call_next):
    """Middleware para logging de requests"""
    inicio = datetime.now()
    
    # Procesar request
    response = await call_next(request)
    
    # Calcular duración
    duracion = (datetime.now() - inicio).total_seconds()
    
    # Log del request
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duración: {duracion:.3f}s"
    )
    
    return response


@app.exception_handler(Exception)
async def manejador_excepciones_global(request: Request, exc: Exception):
    """Manejador global de excepciones"""
    logger.error(f"Error no manejado: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "exito": False,
            "error": "Error interno del servidor",
            "codigo": "INTERNAL_ERROR",
            "mensaje": str(exc) if config.DEBUG else "Ocurrió un error inesperado"
        }
    )


# ============================================================================
# ENDPOINTS DE LA API
# ============================================================================

@app.get("/", response_model=Dict, tags=["General"])
async def raiz():
    """Endpoint raíz - información básica de la API"""
    return {
        "nombre": "API Gestión de Gimnasio",
        "version": "2.0.0",
        "estado": "operativo",
        "documentacion": "/docs"
    }


@app.get("/health", response_model=Dict, tags=["General"])
@limiter.limit("30/minute")
async def health_check(request: Request):
    """
    Health check comprehensivo del sistema
    Verifica estado de BD, configuración, etc.
    """
    try:
        # Verificar conexión a BD
        estadisticas = gestor_bd.obtener_estadisticas()
        
        return {
            "estado": "saludable",
            "timestamp": datetime.now().isoformat(),
            "base_datos": "conectada",
            "estadisticas": estadisticas,
            "version": "2.0.0"
        }
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio no disponible"
        )


@app.post("/api/auth/login", response_model=Dict, tags=["Autenticación"])
@limiter.limit("10/minute")
async def login(request: Request, credenciales: UsuarioLogin):
    """
    Autenticación de usuario con JWT
    Incluye rate limiting para prevenir ataques de fuerza bruta
    """
    try:
        # Verificar credenciales
        usuario = gestor_bd.verificar_credenciales(
            credenciales.email,
            credenciales.password
        )
        
        if not usuario:
            logger.warning(f"Intento de login fallido: {credenciales.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )
        
        # Generar token JWT
        token = crear_token_jwt(usuario['id'], usuario['email'])
        
        logger.info(f"Login exitoso: {credenciales.email}")
        
        return {
            "exito": True,
            "mensaje": "Login exitoso",
            "token": token,
            "usuario": usuario
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error en autenticación"
        )


@app.post("/api/usuarios", response_model=RespuestaBase, tags=["Usuarios"], status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def crear_usuario(request: Request, usuario: UsuarioCrear):
    """
    Crear nuevo usuario/alumno
    Valida complejidad de contraseña y unicidad de email
    """
    try:
        usuario_id = gestor_bd.crear_usuario(
            nombre=usuario.nombre,
            email=usuario.email,
            password=usuario.password,
            telefono=usuario.telefono,
            equipo=usuario.equipo,
            nivel=usuario.nivel
        )
        
        logger.info(f"Usuario creado: {usuario.email} (ID: {usuario_id})")
        
        return RespuestaBase(
            mensaje="Usuario creado exitosamente",
            datos={"usuario_id": usuario_id}
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creando usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creando usuario"
        )


@app.get("/api/usuarios", response_model=Dict, tags=["Usuarios"])
@limiter.limit("30/minute")
async def obtener_usuarios(
    request: Request,
    estado: Optional[str] = None,
    limite: int = Field(100, ge=1, le=1000),
    offset: int = Field(0, ge=0)
):
    """
    Obtener lista de usuarios/alumnos con paginación
    """
    try:
        alumnos = gestor_bd.obtener_alumnos(
            estado=estado,
            limite=limite,
            offset=offset
        )
        
        # Convertir a diccionarios
        alumnos_dict = [
            {
                'id': a.id,
                'nombre': a.nombre,
                'email': a.email,
                'telefono': a.telefono,
                'fecha_registro': a.fecha_registro,
                'estado': a.estado,
                'equipo': a.equipo,
                'nivel': a.nivel
            }
            for a in alumnos
        ]
        
        return {
            "exito": True,
            "total": len(alumnos_dict),
            "limite": limite,
            "offset": offset,
            "alumnos": alumnos_dict
        }
    
    except Exception as e:
        logger.error(f"Error obteniendo usuarios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error obteniendo usuarios"
        )


@app.post("/api/rutinas", response_model=RespuestaBase, tags=["Rutinas"], status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def crear_rutina(request: Request, rutina: RutinaCrear):
    """Crear nueva rutina de entrenamiento"""
    try:
        rutina_id = gestor_bd.crear_rutina(
            nombre=rutina.nombre,
            descripcion=rutina.descripcion,
            nivel_dificultad=rutina.nivel_dificultad,
            duracion_minutos=rutina.duracion_minutos,
            ejercicios=rutina.ejercicios,
            creador_id=rutina.creador_id
        )
        
        logger.info(f"Rutina creada: {rutina.nombre} (ID: {rutina_id})")
        
        return RespuestaBase(
            mensaje="Rutina creada exitosamente",
            datos={"rutina_id": rutina_id}
        )
    
    except Exception as e:
        logger.error(f"Error creando rutina: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creando rutina"
        )


@app.post("/api/evaluaciones", response_model=RespuestaBase, tags=["Evaluaciones"], status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def registrar_evaluacion(request: Request, evaluacion: EvaluacionCrear):
    """Registrar evaluación corporal de un alumno"""
    try:
        evaluacion_id = gestor_bd.registrar_evaluacion(
            alumno_id=evaluacion.alumno_id,
            peso_kg=evaluacion.peso_kg,
            altura_cm=evaluacion.altura_cm,
            porcentaje_grasa=evaluacion.porcentaje_grasa,
            masa_muscular_kg=evaluacion.masa_muscular_kg,
            medidas=evaluacion.medidas,
            notas=evaluacion.notas,
            evaluador_id=evaluacion.evaluador_id
        )
        
        logger.info(f"Evaluación registrada para alumno {evaluacion.alumno_id}")
        
        return RespuestaBase(
            mensaje="Evaluación registrada exitosamente",
            datos={"evaluacion_id": evaluacion_id}
        )
    
    except Exception as e:
        logger.error(f"Error registrando evaluación: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error registrando evaluación"
        )


@app.post("/api/pagos", response_model=RespuestaBase, tags=["Pagos"], status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def registrar_pago(request: Request, pago: PagoCrear):
    """Registrar pago de membresía"""
    try:
        pago_id = gestor_bd.registrar_pago(
            alumno_id=pago.alumno_id,
            monto=pago.monto,
            tipo_membresia=pago.tipo_membresia,
            periodo_inicio=pago.periodo_inicio,
            periodo_fin=pago.periodo_fin,
            metodo_pago=pago.metodo_pago
        )
        
        logger.info(f"Pago registrado: ${pago.monto} - Alumno {pago.alumno_id}")
        
        return RespuestaBase(
            mensaje="Pago registrado exitosamente",
            datos={"pago_id": pago_id}
        )
    
    except Exception as e:
        logger.error(f"Error registrando pago: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error registrando pago"
        )


@app.post("/api/mensajes", response_model=RespuestaBase, tags=["Mensajería"], status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def enviar_mensaje(request: Request, mensaje: MensajeCrear):
    """Enviar mensaje a un alumno"""
    try:
        mensaje_id = gestor_bd.enviar_mensaje(
            remitente_id=mensaje.remitente_id,
            destinatario_id=mensaje.destinatario_id,
            asunto=mensaje.asunto,
            contenido=mensaje.contenido,
            tipo=mensaje.tipo
        )
        
        logger.info(f"Mensaje enviado: {mensaje.remitente_id} -> {mensaje.destinatario_id}")
        
        return RespuestaBase(
            mensaje="Mensaje enviado exitosamente",
            datos={"mensaje_id": mensaje_id}
        )
    
    except Exception as e:
        logger.error(f"Error enviando mensaje: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error enviando mensaje"
        )


@app.post("/api/asistencia/{alumno_id}", response_model=RespuestaBase, tags=["Asistencia"])
@limiter.limit("60/minute")
async def registrar_asistencia(request: Request, alumno_id: int, tipo_sesion: str = "general"):
    """Registrar asistencia de alumno al gimnasio"""
    try:
        asistencia_id = gestor_bd.registrar_asistencia(
            alumno_id=alumno_id,
            tipo_sesion=tipo_sesion
        )
        
        logger.info(f"Asistencia registrada: Alumno {alumno_id}")
        
        return RespuestaBase(
            mensaje="Asistencia registrada exitosamente",
            datos={"asistencia_id": asistencia_id}
        )
    
    except Exception as e:
        logger.error(f"Error registrando asistencia: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error registrando asistencia"
        )


@app.get("/api/estadisticas", response_model=Dict, tags=["Estadísticas"])
@limiter.limit("20/minute")
async def obtener_estadisticas(request: Request):
    """Obtener estadísticas generales del gimnasio"""
    try:
        stats = gestor_bd.obtener_estadisticas()
        
        return {
            "exito": True,
            "timestamp": datetime.now().isoformat(),
            "estadisticas": stats
        }
    
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error obteniendo estadísticas"
        )


# ============================================================================
# INICIALIZACIÓN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Evento de inicialización de la aplicación"""
    logger.info("="*60)
    logger.info("Iniciando servidor API de Gestión de Gimnasio")
    logger.info("="*60)
    
    # Validar configuración
    config.validar_configuracion()
    config.mostrar_configuracion()
    
    logger.info("✅ Servidor iniciado correctamente")
    logger.info(f"📚 Documentación disponible en: http://{config.SERVER_HOST}:{config.SERVER_PORT}/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre de la aplicación"""
    logger.info("Cerrando servidor API...")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "madre_server:app",
        host=config.SERVER_HOST,
        port=config.SERVER_PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower()
    )
