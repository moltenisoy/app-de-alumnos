"""
Módulo de Comunicación para Aplicación Hija (Alumno)
Implementa comunicación robusta con manejo de conectividad offline
"""

import requests
import json
from typing import Dict, Optional, List
from datetime import datetime
import time
import queue
import threading

from config.settings import config
from shared.logger import obtener_logger

# Configurar logger
logger = obtener_logger(__name__)


class GestorConectividad:
    """Gestor de estado de conectividad de red"""
    
    def __init__(self):
        self.conectado = False
        self.ultima_verificacion = None
        self.intentos_fallidos = 0
        self.max_intentos = 5
    
    def verificar_conectividad(self) -> bool:
        """Verificar si hay conectividad con el servidor"""
        try:
            respuesta = requests.get(
                f"{config.MADRE_BASE_URL}/health",
                timeout=5
            )
            
            if respuesta.status_code == 200:
                self.conectado = True
                self.intentos_fallidos = 0
                self.ultima_verificacion = datetime.now()
                logger.info("✅ Conectividad verificada exitosamente")
                return True
        
        except requests.exceptions.RequestException as e:
            self.conectado = False
            self.intentos_fallidos += 1
            logger.warning(f"❌ Sin conectividad con servidor: {e}")
        
        return False
    
    def esta_conectado(self) -> bool:
        """Obtener estado actual de conectividad"""
        # Verificar si necesitamos actualizar el estado
        if self.ultima_verificacion:
            segundos_desde_verificacion = (datetime.now() - self.ultima_verificacion).total_seconds()
            if segundos_desde_verificacion > 60:  # Verificar cada minuto
                return self.verificar_conectividad()
        else:
            return self.verificar_conectividad()
        
        return self.conectado


class ColaOperacionesOffline:
    """Cola de operaciones pendientes para cuando no hay conexión"""
    
    def __init__(self):
        self.cola = queue.Queue()
        self.operaciones_pendientes = []
        self._cargar_operaciones_persistidas()
    
    def agregar_operacion(self, operacion: Dict):
        """Agregar operación a la cola"""
        operacion['timestamp'] = datetime.now().isoformat()
        operacion['intentos'] = 0
        
        self.cola.put(operacion)
        self.operaciones_pendientes.append(operacion)
        self._persistir_operaciones()
        
        logger.info(f"Operación agregada a cola offline: {operacion.get('tipo', 'desconocida')}")
    
    def obtener_operacion(self) -> Optional[Dict]:
        """Obtener siguiente operación de la cola"""
        try:
            return self.cola.get_nowait()
        except queue.Empty:
            return None
    
    def marcar_completada(self, operacion: Dict):
        """Marcar operación como completada"""
        if operacion in self.operaciones_pendientes:
            self.operaciones_pendientes.remove(operacion)
            self._persistir_operaciones()
            logger.info(f"Operación completada: {operacion.get('tipo', 'desconocida')}")
    
    def marcar_fallida(self, operacion: Dict):
        """Marcar operación como fallida y reintentar"""
        operacion['intentos'] += 1
        
        if operacion['intentos'] < 3:
            # Reintentar
            self.cola.put(operacion)
            logger.warning(f"Reintentando operación (intento {operacion['intentos']})")
        else:
            # Demasiados intentos, remover
            if operacion in self.operaciones_pendientes:
                self.operaciones_pendientes.remove(operacion)
            logger.error(f"Operación fallida después de 3 intentos: {operacion}")
        
        self._persistir_operaciones()
    
    def _persistir_operaciones(self):
        """Guardar operaciones pendientes en archivo"""
        try:
            with open('data/operaciones_offline.json', 'w') as f:
                json.dump(self.operaciones_pendientes, f, indent=2)
        except Exception as e:
            logger.error(f"Error persistiendo operaciones: {e}")
    
    def _cargar_operaciones_persistidas(self):
        """Cargar operaciones pendientes desde archivo"""
        try:
            with open('data/operaciones_offline.json', 'r') as f:
                self.operaciones_pendientes = json.load(f)
                
                # Recargar en cola
                for op in self.operaciones_pendientes:
                    self.cola.put(op)
                
                logger.info(f"Cargadas {len(self.operaciones_pendientes)} operaciones pendientes")
        
        except FileNotFoundError:
            self.operaciones_pendientes = []
        except Exception as e:
            logger.error(f"Error cargando operaciones: {e}")
            self.operaciones_pendientes = []


class ClienteAPI:
    """Cliente para comunicación con API del servidor"""
    
    def __init__(self):
        self.base_url = config.MADRE_BASE_URL
        self.token_jwt = None
        self.gestor_conectividad = GestorConectividad()
        self.cola_offline = ColaOperacionesOffline()
        self.timeout = 30
        
        # Iniciar procesador de cola offline
        self.procesador_thread = threading.Thread(
            target=self._procesar_cola_offline,
            daemon=True
        )
        self.procesador_thread.start()
    
    def _hacer_request(self, metodo: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """Hacer request HTTP con manejo robusto de errores"""
        url = f"{self.base_url}{endpoint}"
        
        # Agregar timeout por defecto
        kwargs.setdefault('timeout', self.timeout)
        
        # Agregar headers con token si existe
        headers = kwargs.get('headers', {})
        if self.token_jwt:
            headers['Authorization'] = f"Bearer {self.token_jwt}"
        kwargs['headers'] = headers
        
        # Intentar con backoff exponencial
        max_intentos = 3
        for intento in range(max_intentos):
            try:
                respuesta = requests.request(metodo, url, **kwargs)
                
                # Verificar código de respuesta
                if respuesta.status_code < 300:
                    logger.info(f"✅ {metodo} {endpoint} - Status: {respuesta.status_code}")
                    return respuesta.json() if respuesta.content else {}
                elif respuesta.status_code == 401:
                    logger.warning("Token JWT expirado o inválido")
                    self.token_jwt = None
                    return None
                else:
                    logger.warning(f"⚠️ {metodo} {endpoint} - Status: {respuesta.status_code}")
                    return None
            
            except requests.exceptions.Timeout:
                logger.warning(f"⏱️ Timeout en intento {intento + 1} de {max_intentos}")
                if intento < max_intentos - 1:
                    time.sleep(2 ** intento)  # Backoff exponencial: 1s, 2s, 4s
            
            except requests.exceptions.ConnectionError as e:
                logger.error(f"❌ Error de conexión: {e}")
                self.gestor_conectividad.conectado = False
                return None
            
            except Exception as e:
                logger.error(f"❌ Error inesperado: {e}", exc_info=True)
                return None
        
        # Todos los intentos fallaron
        logger.error(f"❌ Todos los intentos fallaron para {metodo} {endpoint}")
        return None
    
    def login(self, email: str, password: str) -> Optional[Dict]:
        """Autenticar usuario y obtener token JWT"""
        datos = {
            "email": email,
            "password": password
        }
        
        respuesta = self._hacer_request('POST', '/api/auth/login', json=datos)
        
        if respuesta and respuesta.get('exito'):
            self.token_jwt = respuesta.get('token')
            logger.info(f"Login exitoso para {email}")
            return respuesta.get('usuario')
        
        return None
    
    def obtener_rutinas_usuario(self, usuario_id: int) -> List[Dict]:
        """Obtener rutinas asignadas al usuario"""
        if not self.gestor_conectividad.esta_conectado():
            logger.warning("Sin conexión - usando datos en caché")
            return self._cargar_rutinas_cache(usuario_id)
        
        # Intentar obtener del servidor
        respuesta = self._hacer_request('GET', f'/api/usuarios/{usuario_id}/rutinas')
        
        if respuesta:
            rutinas = respuesta.get('rutinas', [])
            self._guardar_rutinas_cache(usuario_id, rutinas)
            return rutinas
        
        # Fallback a caché
        return self._cargar_rutinas_cache(usuario_id)
    
    def registrar_progreso(self, usuario_id: int, datos_progreso: Dict):
        """Registrar progreso de entrenamiento"""
        if not self.gestor_conectividad.esta_conectado():
            # Agregar a cola offline
            self.cola_offline.agregar_operacion({
                'tipo': 'registrar_progreso',
                'usuario_id': usuario_id,
                'datos': datos_progreso
            })
            logger.info("Progreso guardado en cola offline")
            return True
        
        # Enviar al servidor
        respuesta = self._hacer_request(
            'POST',
            f'/api/usuarios/{usuario_id}/progreso',
            json=datos_progreso
        )
        
        return respuesta is not None
    
    def _procesar_cola_offline(self):
        """Procesar cola de operaciones offline en segundo plano"""
        while True:
            try:
                # Esperar a tener conexión
                if not self.gestor_conectividad.esta_conectado():
                    time.sleep(10)
                    continue
                
                # Procesar operaciones pendientes
                operacion = self.cola_offline.obtener_operacion()
                
                if operacion:
                    logger.info(f"Procesando operación offline: {operacion.get('tipo')}")
                    
                    # Ejecutar según tipo
                    if operacion['tipo'] == 'registrar_progreso':
                        respuesta = self._hacer_request(
                            'POST',
                            f"/api/usuarios/{operacion['usuario_id']}/progreso",
                            json=operacion['datos']
                        )
                        
                        if respuesta:
                            self.cola_offline.marcar_completada(operacion)
                        else:
                            self.cola_offline.marcar_fallida(operacion)
                
                else:
                    # No hay operaciones, esperar
                    time.sleep(5)
            
            except Exception as e:
                logger.error(f"Error procesando cola offline: {e}", exc_info=True)
                time.sleep(5)
    
    def _guardar_rutinas_cache(self, usuario_id: int, rutinas: List[Dict]):
        """Guardar rutinas en caché local"""
        try:
            cache_file = f'data/cache_rutinas_{usuario_id}.json'
            with open(cache_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'rutinas': rutinas
                }, f, indent=2)
            logger.debug(f"Rutinas guardadas en caché para usuario {usuario_id}")
        except Exception as e:
            logger.error(f"Error guardando caché: {e}")
    
    def _cargar_rutinas_cache(self, usuario_id: int) -> List[Dict]:
        """Cargar rutinas desde caché local"""
        try:
            cache_file = f'data/cache_rutinas_{usuario_id}.json'
            with open(cache_file, 'r') as f:
                cache = json.load(f)
                logger.info(f"Rutinas cargadas desde caché (guardado: {cache['timestamp']})")
                return cache.get('rutinas', [])
        except FileNotFoundError:
            logger.warning("No hay caché disponible")
            return []
        except Exception as e:
            logger.error(f"Error cargando caché: {e}")
            return []


# Instancia global del cliente
cliente_api = ClienteAPI()
