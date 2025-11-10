"""
Configuración centralizada del sistema con variables de entorno
Implementa mejores prácticas de separación de configuración por ambiente
"""

import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
load_dotenv()


class Configuracion:
    """Configuración central de la aplicación"""
    
    # Configuración de Base de Datos
    DB_PATH: str = os.getenv('DB_PATH', 'data/gym_database.db')
    
    # Configuración de Servidor
    SERVER_HOST: str = os.getenv('SERVER_HOST', '0.0.0.0')
    SERVER_PORT: int = int(os.getenv('SERVER_PORT', '8000'))
    SERVER_WORKERS: int = int(os.getenv('SERVER_WORKERS', '4'))
    
    # Configuración de Seguridad
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'cambiar-en-produccion-clave-super-secreta')
    JWT_ALGORITHM: str = 'HS256'
    JWT_EXPIRATION_HOURS: int = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))
    MAX_LOGIN_ATTEMPTS: int = int(os.getenv('MAX_LOGIN_ATTEMPTS', '5'))
    
    # Configuración de Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', 'logs/app.log')
    LOG_MAX_SIZE_MB: int = int(os.getenv('LOG_MAX_SIZE_MB', '10'))
    LOG_BACKUP_COUNT: int = int(os.getenv('LOG_BACKUP_COUNT', '5'))
    
    # Configuración de Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
    
    # Configuración de Aplicación Cliente
    MADRE_BASE_URL: str = os.getenv('MADRE_BASE_URL', 'http://localhost:8000')
    SYNC_INTERVAL_SECONDS: int = int(os.getenv('SYNC_INTERVAL_SECONDS', '300'))
    
    # Configuración de Caché
    CACHE_ENABLED: bool = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
    CACHE_TTL_SECONDS: int = int(os.getenv('CACHE_TTL_SECONDS', '3600'))
    
    # Validación de membresía
    MEMBERSHIP_CHECK_HOURS: int = int(os.getenv('MEMBERSHIP_CHECK_HOURS', '72'))
    
    # Entorno
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'development')
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    
    @classmethod
    def validar_configuracion(cls) -> bool:
        """Validar que la configuración sea correcta al inicio"""
        errores = []
        
        # Validar que exista directorio de datos
        db_dir = Path(cls.DB_PATH).parent
        if not db_dir.exists():
            try:
                db_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errores.append(f"No se puede crear directorio de BD: {e}")
        
        # Validar que exista directorio de logs
        log_dir = Path(cls.LOG_FILE).parent
        if not log_dir.exists():
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errores.append(f"No se puede crear directorio de logs: {e}")
        
        # Validar secret key en producción
        if cls.ENVIRONMENT == 'production' and cls.SECRET_KEY == 'cambiar-en-produccion-clave-super-secreta':
            errores.append("⚠️ ADVERTENCIA: Usando SECRET_KEY por defecto en producción")
        
        if errores:
            for error in errores:
                print(f"❌ Error de configuración: {error}")
            return False
        
        print("✅ Configuración validada correctamente")
        return True
    
    @classmethod
    def mostrar_configuracion(cls):
        """Mostrar configuración actual (sin mostrar secretos)"""
        print("\n" + "="*60)
        print("⚙️  CONFIGURACIÓN DEL SISTEMA")
        print("="*60)
        print(f"Entorno: {cls.ENVIRONMENT}")
        print(f"Debug: {cls.DEBUG}")
        print(f"Base de Datos: {cls.DB_PATH}")
        print(f"Servidor: {cls.SERVER_HOST}:{cls.SERVER_PORT}")
        print(f"Nivel de Log: {cls.LOG_LEVEL}")
        print(f"Archivo de Log: {cls.LOG_FILE}")
        print(f"Rate Limiting: {'Activado' if cls.RATE_LIMIT_ENABLED else 'Desactivado'}")
        print(f"Caché: {'Activado' if cls.CACHE_ENABLED else 'Desactivado'}")
        print("="*60 + "\n")


# Configuraciones específicas por ambiente
class ConfiguracionDesarrollo(Configuracion):
    """Configuración para ambiente de desarrollo"""
    ENVIRONMENT = 'development'
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ConfiguracionProduccion(Configuracion):
    """Configuración para ambiente de producción"""
    ENVIRONMENT = 'production'
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    RATE_LIMIT_ENABLED = True


# Seleccionar configuración según ambiente
def obtener_configuracion() -> Configuracion:
    """Obtener configuración según el ambiente"""
    env = os.getenv('ENVIRONMENT', 'development')
    
    if env == 'production':
        return ConfiguracionProduccion()
    else:
        return ConfiguracionDesarrollo()


# Instancia global de configuración
config = obtener_configuracion()
