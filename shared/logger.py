"""
Sistema de Logging Estructurado con Rotación Automática
Implementa mejores prácticas de logging profesional
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional


class FormateadorPersonalizado(logging.Formatter):
    """Formateador personalizado con colores y estructura mejorada"""
    
    # Colores ANSI para terminal
    COLORES = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Verde
        'WARNING': '\033[33m',   # Amarillo
        'ERROR': '\033[31m',     # Rojo
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        """Formatear registro de log con estructura clara"""
        # Obtener color según nivel
        color = self.COLORES.get(record.levelname, self.COLORES['RESET'])
        reset = self.COLORES['RESET']
        
        # Formato: [TIMESTAMP] [NIVEL] [MODULO:FUNCION] Mensaje
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        nivel = f"{color}{record.levelname:8s}{reset}"
        ubicacion = f"{record.filename}:{record.funcName}"
        
        # Construir mensaje formateado
        mensaje_base = f"[{timestamp}] [{nivel}] [{ubicacion}] {record.getMessage()}"
        
        # Agregar información de excepción si existe
        if record.exc_info:
            mensaje_base += f"\n{self.formatException(record.exc_info)}"
        
        return mensaje_base


def configurar_logging(nombre_app: str = 'gym_app', 
                       nivel: str = 'INFO',
                       archivo_log: str = 'logs/app.log',
                       max_bytes: int = 10 * 1024 * 1024,  # 10MB
                       backup_count: int = 5) -> logging.Logger:
    """
    Configurar sistema de logging con rotación automática
    
    Args:
        nombre_app: Nombre de la aplicación para el logger
        nivel: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        archivo_log: Ruta al archivo de log
        max_bytes: Tamaño máximo del archivo antes de rotar (bytes)
        backup_count: Número de archivos de respaldo a mantener
    
    Returns:
        Logger configurado
    """
    # Crear logger
    logger = logging.getLogger(nombre_app)
    logger.setLevel(getattr(logging, nivel.upper()))
    
    # Evitar duplicar handlers si ya está configurado
    if logger.handlers:
        return logger
    
    # Asegurar que existe el directorio de logs
    Path(archivo_log).parent.mkdir(parents=True, exist_ok=True)
    
    # Handler para archivo con rotación
    file_handler = RotatingFileHandler(
        archivo_log,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Formato para archivo (más detallado, sin colores)
    formato_archivo = logging.Formatter(
        '[%(asctime)s] [%(levelname)-8s] [%(name)s:%(funcName)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formato_archivo)
    
    # Handler para consola con colores
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, nivel.upper()))
    console_handler.setFormatter(FormateadorPersonalizado())
    
    # Agregar handlers al logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Log inicial
    logger.info(f"Sistema de logging inicializado - Nivel: {nivel}")
    logger.info(f"Archivo de log: {archivo_log}")
    logger.info(f"Rotación configurada: {max_bytes/1024/1024:.1f}MB, {backup_count} respaldos")
    
    return logger


def obtener_logger(nombre: str) -> logging.Logger:
    """
    Obtener logger para un módulo específico
    
    Args:
        nombre: Nombre del módulo (típicamente __name__)
    
    Returns:
        Logger configurado para el módulo
    """
    return logging.getLogger(f"gym_app.{nombre}")


# Función auxiliar para logging de contexto de usuario
def log_con_contexto(logger: logging.Logger, nivel: str, mensaje: str, 
                    usuario_id: Optional[int] = None, 
                    contexto: Optional[dict] = None):
    """
    Loggear con contexto adicional de usuario y datos
    
    Args:
        logger: Logger a usar
        nivel: Nivel de log (debug, info, warning, error, critical)
        mensaje: Mensaje principal
        usuario_id: ID de usuario asociado (opcional)
        contexto: Diccionario con contexto adicional (opcional)
    """
    # Construir mensaje con contexto
    partes_mensaje = [mensaje]
    
    if usuario_id:
        partes_mensaje.append(f"[Usuario: {usuario_id}]")
    
    if contexto:
        contexto_str = " ".join([f"{k}={v}" for k, v in contexto.items()])
        partes_mensaje.append(f"[{contexto_str}]")
    
    mensaje_completo = " ".join(partes_mensaje)
    
    # Loggear según nivel
    getattr(logger, nivel.lower())(mensaje_completo)


# Logger por defecto para la aplicación
app_logger = configurar_logging()
