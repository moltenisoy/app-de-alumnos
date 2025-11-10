"""
Aplicación Principal Madre (Entrenador Personal)
Punto de entrada que inicia servidor API y GUI administrativa
"""

import threading
import time
import sys
from pathlib import Path

# Agregar directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import config
from shared.logger import configurar_logging, obtener_logger

# Configurar logging
logger = configurar_logging(
    nombre_app='gym_madre',
    nivel=config.LOG_LEVEL,
    archivo_log=config.LOG_FILE
)


def iniciar_servidor():
    """Iniciar servidor API en thread separado"""
    try:
        import uvicorn
        from madre_server import app
        
        logger.info(f"Iniciando servidor API en {config.SERVER_HOST}:{config.SERVER_PORT}")
        
        uvicorn.run(
            app,
            host=config.SERVER_HOST,
            port=config.SERVER_PORT,
            log_level=config.LOG_LEVEL.lower(),
            access_log=True
        )
    except Exception as e:
        logger.error(f"Error iniciando servidor: {e}", exc_info=True)


def iniciar_gui():
    """Iniciar interfaz gráfica administrativa"""
    try:
        # Esperar a que el servidor esté listo
        time.sleep(2)
        
        logger.info("Iniciando interfaz gráfica administrativa")
        
        import customtkinter as ctk
        from madre_gui import AplicacionMadre
        
        # Configurar tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Crear y ejecutar aplicación
        app = AplicacionMadre()
        app.mainloop()
        
    except Exception as e:
        logger.error(f"Error iniciando GUI: {e}", exc_info=True)


def main():
    """Función principal"""
    print("\n" + "="*70)
    print("🏋️  SISTEMA DE GESTIÓN DE GIMNASIO - APLICACIÓN ENTRENADOR")
    print("="*70 + "\n")
    
    # Validar configuración
    if not config.validar_configuracion():
        print("❌ Error en configuración. Abortando...")
        return
    
    # Mostrar configuración
    config.mostrar_configuracion()
    
    print("\n📌 Componentes:")
    print(f"   • Servidor API: http://{config.SERVER_HOST}:{config.SERVER_PORT}")
    print(f"   • Documentación: http://{config.SERVER_HOST}:{config.SERVER_PORT}/docs")
    print(f"   • Interfaz Administrativa: Próximamente...")
    print("\n" + "="*70 + "\n")
    
    try:
        # Iniciar servidor en thread separado
        thread_servidor = threading.Thread(target=iniciar_servidor, daemon=True)
        thread_servidor.start()
        
        logger.info("Servidor API iniciado en segundo plano")
        
        # Iniciar GUI en thread principal
        iniciar_gui()
        
    except KeyboardInterrupt:
        logger.info("Aplicación interrumpida por usuario")
        print("\n\n👋 Cerrando aplicación...")
    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)
        print(f"\n❌ Error fatal: {e}")
    finally:
        print("\n✅ Aplicación cerrada\n")


if __name__ == "__main__":
    main()
