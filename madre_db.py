"""
Sistema de Base de Datos para Aplicación Madre (Entrenador Personal)
Gestión completa de alumnos, rutinas, evaluaciones y administración del gimnasio
"""

import sqlite3
import hashlib
import bcrypt
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from contextlib import contextmanager
from dataclasses import dataclass
import json

# Configurar logging estructurado
logger = logging.getLogger(__name__)


@dataclass
class Alumno:
    """Modelo de datos para un alumno del gimnasio"""
    id: int
    nombre: str
    email: str
    telefono: str
    fecha_registro: str
    estado: str
    equipo: str
    nivel: str
    foto_perfil: Optional[str] = None


@dataclass
class Rutina:
    """Modelo de datos para una rutina de entrenamiento"""
    id: int
    nombre: str
    descripcion: str
    nivel_dificultad: str
    duracion_minutos: int
    ejercicios: List[Dict]


class GestorBaseDatos:
    """
    Gestor de base de datos con arquitectura en capas y mejores prácticas
    Implementa patrón Repository para acceso a datos
    """
    
    def __init__(self, db_path: str = 'data/gym_database.db'):
        self.db_path = db_path
        self._asegurar_directorio()
        self._inicializar_base_datos()
        logger.info(f"Base de datos inicializada: {db_path}")
    
    def _asegurar_directorio(self):
        """Crear directorio de datos si no existe"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    @contextmanager
    def _obtener_conexion(self):
        """Context manager para conexiones seguras a BD"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error en transacción BD: {e}")
            raise
        finally:
            conn.close()
    
    def _inicializar_base_datos(self):
        """Crear todas las tablas necesarias con índices optimizados"""
        with self._obtener_conexion() as conn:
            cursor = conn.cursor()
            
            # Tabla de usuarios/alumnos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    telefono TEXT,
                    password_hash TEXT NOT NULL,
                    fecha_registro TEXT NOT NULL,
                    estado TEXT DEFAULT 'activo',
                    equipo TEXT,
                    nivel TEXT,
                    foto_perfil TEXT,
                    intentos_fallidos INTEGER DEFAULT 0,
                    ultimo_acceso TEXT,
                    CONSTRAINT check_estado CHECK (estado IN ('activo', 'inactivo', 'suspendido'))
                )
            """)
            
            # Tabla de rutinas de entrenamiento
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rutinas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    descripcion TEXT,
                    nivel_dificultad TEXT,
                    duracion_minutos INTEGER,
                    ejercicios_json TEXT,
                    creador_id INTEGER,
                    fecha_creacion TEXT NOT NULL,
                    activa INTEGER DEFAULT 1,
                    FOREIGN KEY (creador_id) REFERENCES usuarios(id)
                )
            """)
            
            # Tabla de asignaciones de rutinas a alumnos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS asignaciones_rutinas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alumno_id INTEGER NOT NULL,
                    rutina_id INTEGER NOT NULL,
                    fecha_asignacion TEXT NOT NULL,
                    fecha_inicio TEXT,
                    fecha_fin TEXT,
                    completada INTEGER DEFAULT 0,
                    progreso_porcentaje REAL DEFAULT 0,
                    FOREIGN KEY (alumno_id) REFERENCES usuarios(id),
                    FOREIGN KEY (rutina_id) REFERENCES rutinas(id)
                )
            """)
            
            # Tabla de evaluaciones corporales
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evaluaciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alumno_id INTEGER NOT NULL,
                    fecha TEXT NOT NULL,
                    peso_kg REAL,
                    altura_cm REAL,
                    imc REAL,
                    porcentaje_grasa REAL,
                    masa_muscular_kg REAL,
                    medidas_json TEXT,
                    notas TEXT,
                    evaluador_id INTEGER,
                    FOREIGN KEY (alumno_id) REFERENCES usuarios(id),
                    FOREIGN KEY (evaluador_id) REFERENCES usuarios(id)
                )
            """)
            
            # Tabla de pagos y membresías
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pagos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alumno_id INTEGER NOT NULL,
                    monto REAL NOT NULL,
                    fecha_pago TEXT NOT NULL,
                    tipo_membresia TEXT NOT NULL,
                    periodo_inicio TEXT NOT NULL,
                    periodo_fin TEXT NOT NULL,
                    metodo_pago TEXT,
                    estado TEXT DEFAULT 'completado',
                    factura_numero TEXT,
                    FOREIGN KEY (alumno_id) REFERENCES usuarios(id)
                )
            """)
            
            # Tabla de mensajes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mensajes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    remitente_id INTEGER NOT NULL,
                    destinatario_id INTEGER NOT NULL,
                    asunto TEXT,
                    contenido TEXT NOT NULL,
                    fecha_envio TEXT NOT NULL,
                    leido INTEGER DEFAULT 0,
                    tipo TEXT DEFAULT 'personal',
                    FOREIGN KEY (remitente_id) REFERENCES usuarios(id),
                    FOREIGN KEY (destinatario_id) REFERENCES usuarios(id)
                )
            """)
            
            # Tabla de asistencia
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS asistencia (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alumno_id INTEGER NOT NULL,
                    fecha TEXT NOT NULL,
                    hora_entrada TEXT NOT NULL,
                    hora_salida TEXT,
                    tipo_sesion TEXT,
                    FOREIGN KEY (alumno_id) REFERENCES usuarios(id)
                )
            """)
            
            # Crear índices para optimización de consultas
            indices = [
                "CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email)",
                "CREATE INDEX IF NOT EXISTS idx_usuarios_estado ON usuarios(estado)",
                "CREATE INDEX IF NOT EXISTS idx_rutinas_activa ON rutinas(activa)",
                "CREATE INDEX IF NOT EXISTS idx_asignaciones_alumno ON asignaciones_rutinas(alumno_id)",
                "CREATE INDEX IF NOT EXISTS idx_asignaciones_rutina ON asignaciones_rutinas(rutina_id)",
                "CREATE INDEX IF NOT EXISTS idx_evaluaciones_alumno ON evaluaciones(alumno_id)",
                "CREATE INDEX IF NOT EXISTS idx_evaluaciones_fecha ON evaluaciones(fecha)",
                "CREATE INDEX IF NOT EXISTS idx_pagos_alumno ON pagos(alumno_id)",
                "CREATE INDEX IF NOT EXISTS idx_pagos_fecha ON pagos(fecha_pago)",
                "CREATE INDEX IF NOT EXISTS idx_mensajes_dest ON mensajes(destinatario_id)",
                "CREATE INDEX IF NOT EXISTS idx_asistencia_alumno ON asistencia(alumno_id)",
                "CREATE INDEX IF NOT EXISTS idx_asistencia_fecha ON asistencia(fecha)",
            ]
            
            for indice in indices:
                cursor.execute(indice)
            
            logger.info("Tablas e índices creados exitosamente")
    
    def crear_usuario(self, nombre: str, email: str, password: str, 
                     telefono: str = "", equipo: str = "", nivel: str = "principiante") -> int:
        """
        Crear nuevo usuario con hash seguro de contraseña (bcrypt)
        """
        try:
            # Validar complejidad de contraseña
            if len(password) < 8:
                raise ValueError("La contraseña debe tener al menos 8 caracteres")
            
            # Hash seguro con bcrypt
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            fecha_registro = datetime.now().isoformat()
            
            with self._obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO usuarios 
                    (nombre, email, password_hash, telefono, fecha_registro, equipo, nivel)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (nombre, email, password_hash, telefono, fecha_registro, equipo, nivel))
                
                usuario_id = cursor.lastrowid
                logger.info(f"Usuario creado: {email} (ID: {usuario_id})")
                return usuario_id
        
        except sqlite3.IntegrityError:
            logger.warning(f"Email duplicado: {email}")
            raise ValueError(f"El email {email} ya está registrado")
        except Exception as e:
            logger.error(f"Error creando usuario: {e}")
            raise
    
    def verificar_credenciales(self, email: str, password: str) -> Optional[Dict]:
        """
        Verificar credenciales con límite de intentos fallidos
        """
        with self._obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nombre, email, password_hash, estado, intentos_fallidos
                FROM usuarios WHERE email = ?
            """, (email,))
            
            usuario = cursor.fetchone()
            
            if not usuario:
                logger.warning(f"Intento de login con email inexistente: {email}")
                return None
            
            # Verificar si cuenta está bloqueada
            if usuario['intentos_fallidos'] >= 5:
                logger.warning(f"Cuenta bloqueada por intentos fallidos: {email}")
                return None
            
            # Verificar contraseña con bcrypt
            if bcrypt.checkpw(password.encode('utf-8'), usuario['password_hash']):
                # Login exitoso - resetear intentos fallidos
                cursor.execute("""
                    UPDATE usuarios 
                    SET intentos_fallidos = 0, ultimo_acceso = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), usuario['id']))
                
                logger.info(f"Login exitoso: {email}")
                return {
                    'id': usuario['id'],
                    'nombre': usuario['nombre'],
                    'email': usuario['email'],
                    'estado': usuario['estado']
                }
            else:
                # Contraseña incorrecta - incrementar contador
                cursor.execute("""
                    UPDATE usuarios 
                    SET intentos_fallidos = intentos_fallidos + 1
                    WHERE id = ?
                """, (usuario['id'],))
                
                logger.warning(f"Contraseña incorrecta para: {email}")
                return None
    
    def obtener_alumnos(self, estado: Optional[str] = None, 
                        limite: int = 100, offset: int = 0) -> List[Alumno]:
        """
        Obtener lista de alumnos con paginación
        """
        with self._obtener_conexion() as conn:
            cursor = conn.cursor()
            
            if estado:
                cursor.execute("""
                    SELECT id, nombre, email, telefono, fecha_registro, 
                           estado, equipo, nivel, foto_perfil
                    FROM usuarios
                    WHERE estado = ?
                    ORDER BY nombre
                    LIMIT ? OFFSET ?
                """, (estado, limite, offset))
            else:
                cursor.execute("""
                    SELECT id, nombre, email, telefono, fecha_registro,
                           estado, equipo, nivel, foto_perfil
                    FROM usuarios
                    ORDER BY nombre
                    LIMIT ? OFFSET ?
                """, (limite, offset))
            
            alumnos = []
            for row in cursor.fetchall():
                alumno = Alumno(
                    id=row['id'],
                    nombre=row['nombre'],
                    email=row['email'],
                    telefono=row['telefono'],
                    fecha_registro=row['fecha_registro'],
                    estado=row['estado'],
                    equipo=row['equipo'],
                    nivel=row['nivel'],
                    foto_perfil=row['foto_perfil']
                )
                alumnos.append(alumno)
            
            return alumnos
    
    def crear_rutina(self, nombre: str, descripcion: str, nivel_dificultad: str,
                     duracion_minutos: int, ejercicios: List[Dict], 
                     creador_id: int) -> int:
        """
        Crear nueva rutina de entrenamiento
        """
        try:
            ejercicios_json = json.dumps(ejercicios)
            fecha_creacion = datetime.now().isoformat()
            
            with self._obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO rutinas
                    (nombre, descripcion, nivel_dificultad, duracion_minutos, 
                     ejercicios_json, creador_id, fecha_creacion)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (nombre, descripcion, nivel_dificultad, duracion_minutos,
                      ejercicios_json, creador_id, fecha_creacion))
                
                rutina_id = cursor.lastrowid
                logger.info(f"Rutina creada: {nombre} (ID: {rutina_id})")
                return rutina_id
        
        except Exception as e:
            logger.error(f"Error creando rutina: {e}")
            raise
    
    def asignar_rutina(self, alumno_id: int, rutina_id: int, 
                      fecha_inicio: str, fecha_fin: str) -> int:
        """
        Asignar rutina a un alumno
        """
        try:
            fecha_asignacion = datetime.now().isoformat()
            
            with self._obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO asignaciones_rutinas
                    (alumno_id, rutina_id, fecha_asignacion, fecha_inicio, fecha_fin)
                    VALUES (?, ?, ?, ?, ?)
                """, (alumno_id, rutina_id, fecha_asignacion, fecha_inicio, fecha_fin))
                
                asignacion_id = cursor.lastrowid
                logger.info(f"Rutina {rutina_id} asignada a alumno {alumno_id}")
                return asignacion_id
        
        except Exception as e:
            logger.error(f"Error asignando rutina: {e}")
            raise
    
    def registrar_evaluacion(self, alumno_id: int, peso_kg: float, 
                           altura_cm: float, porcentaje_grasa: Optional[float] = None,
                           masa_muscular_kg: Optional[float] = None,
                           medidas: Optional[Dict] = None, 
                           notas: str = "", evaluador_id: Optional[int] = None) -> int:
        """
        Registrar evaluación corporal de un alumno
        """
        try:
            fecha = datetime.now().isoformat()
            
            # Calcular IMC
            altura_m = altura_cm / 100
            imc = peso_kg / (altura_m ** 2)
            
            medidas_json = json.dumps(medidas) if medidas else None
            
            with self._obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO evaluaciones
                    (alumno_id, fecha, peso_kg, altura_cm, imc, 
                     porcentaje_grasa, masa_muscular_kg, medidas_json, notas, evaluador_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (alumno_id, fecha, peso_kg, altura_cm, imc,
                      porcentaje_grasa, masa_muscular_kg, medidas_json, notas, evaluador_id))
                
                evaluacion_id = cursor.lastrowid
                logger.info(f"Evaluación registrada para alumno {alumno_id}")
                return evaluacion_id
        
        except Exception as e:
            logger.error(f"Error registrando evaluación: {e}")
            raise
    
    def registrar_pago(self, alumno_id: int, monto: float, tipo_membresia: str,
                      periodo_inicio: str, periodo_fin: str, 
                      metodo_pago: str = "efectivo") -> int:
        """
        Registrar pago de membresía
        """
        try:
            fecha_pago = datetime.now().isoformat()
            
            with self._obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO pagos
                    (alumno_id, monto, fecha_pago, tipo_membresia, 
                     periodo_inicio, periodo_fin, metodo_pago)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (alumno_id, monto, fecha_pago, tipo_membresia,
                      periodo_inicio, periodo_fin, metodo_pago))
                
                pago_id = cursor.lastrowid
                logger.info(f"Pago registrado: ${monto} - Alumno {alumno_id}")
                return pago_id
        
        except Exception as e:
            logger.error(f"Error registrando pago: {e}")
            raise
    
    def enviar_mensaje(self, remitente_id: int, destinatario_id: int,
                      asunto: str, contenido: str, tipo: str = "personal") -> int:
        """
        Enviar mensaje a un alumno
        """
        try:
            fecha_envio = datetime.now().isoformat()
            
            with self._obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO mensajes
                    (remitente_id, destinatario_id, asunto, contenido, fecha_envio, tipo)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (remitente_id, destinatario_id, asunto, contenido, fecha_envio, tipo))
                
                mensaje_id = cursor.lastrowid
                logger.info(f"Mensaje enviado: {remitente_id} -> {destinatario_id}")
                return mensaje_id
        
        except Exception as e:
            logger.error(f"Error enviando mensaje: {e}")
            raise
    
    def registrar_asistencia(self, alumno_id: int, tipo_sesion: str = "general") -> int:
        """
        Registrar asistencia de alumno al gimnasio
        """
        try:
            fecha = datetime.now().date().isoformat()
            hora_entrada = datetime.now().time().isoformat()
            
            with self._obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO asistencia
                    (alumno_id, fecha, hora_entrada, tipo_sesion)
                    VALUES (?, ?, ?, ?)
                """, (alumno_id, fecha, hora_entrada, tipo_sesion))
                
                asistencia_id = cursor.lastrowid
                logger.info(f"Asistencia registrada: Alumno {alumno_id}")
                return asistencia_id
        
        except Exception as e:
            logger.error(f"Error registrando asistencia: {e}")
            raise
    
    def obtener_estadisticas(self) -> Dict:
        """
        Obtener estadísticas generales del gimnasio
        """
        with self._obtener_conexion() as conn:
            cursor = conn.cursor()
            
            # Total de alumnos activos
            cursor.execute("SELECT COUNT(*) as total FROM usuarios WHERE estado = 'activo'")
            alumnos_activos = cursor.fetchone()['total']
            
            # Asistencias del mes actual
            mes_actual = datetime.now().strftime('%Y-%m')
            cursor.execute("""
                SELECT COUNT(*) as total 
                FROM asistencia 
                WHERE fecha LIKE ?
            """, (f"{mes_actual}%",))
            asistencias_mes = cursor.fetchone()['total']
            
            # Ingresos del mes
            cursor.execute("""
                SELECT SUM(monto) as total 
                FROM pagos 
                WHERE fecha_pago LIKE ?
            """, (f"{mes_actual}%",))
            ingresos_mes = cursor.fetchone()['total'] or 0
            
            # Rutinas activas
            cursor.execute("SELECT COUNT(*) as total FROM rutinas WHERE activa = 1")
            rutinas_activas = cursor.fetchone()['total']
            
            return {
                'alumnos_activos': alumnos_activos,
                'asistencias_mes': asistencias_mes,
                'ingresos_mes': ingresos_mes,
                'rutinas_activas': rutinas_activas
            }


# Instancia global del gestor
gestor_bd = GestorBaseDatos()
