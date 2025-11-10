"""
Aplicación Principal Hija (Alumno)
Punto de entrada para la aplicación del alumno
"""

import sys
from pathlib import Path

# Agregar directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

import customtkinter as ctk
from config.settings import config
from shared.logger import configurar_logging, obtener_logger
from hija_views import AplicacionHija

# Configurar logging
logger = configurar_logging(
    nombre_app='gym_hija',
    nivel=config.LOG_LEVEL,
    archivo_log='logs/hija.log'
)


def main():
    """Función principal"""
    print("\n" + "="*70)
    print("🏋️  MI ENTRENAMIENTO PERSONAL - APLICACIÓN ALUMNO")
    print("="*70 + "\n")
    
    logger.info("Iniciando aplicación de alumno")
    
    try:
        # Configurar tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Crear y ejecutar aplicación
        app = AplicacionHija()
        app.mainloop()
        
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
