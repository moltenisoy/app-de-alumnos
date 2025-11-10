"""
Vistas de Interfaz Gráfica para Aplicación Hija (Alumno)
UI optimizada con todas las funcionalidades para alumnos
TODOS LOS TEXTOS EN CASTELLANO
"""

import customtkinter as ctk
from typing import Optional, Dict, List
from datetime import datetime

from hija_comms import cliente_api
from shared.logger import obtener_logger

# Configurar logger
logger = obtener_logger(__name__)


class AplicacionHija(ctk.CTk):
    """Aplicación principal para alumnos"""
    
    def __init__(self):
        super().__init__()
        
        # Configuración de ventana
        self.title("🏋️ Mi Entrenamiento Personal")
        self.geometry("1200x800")
        
        # Variables de estado
        self.usuario_actual = None
        self.rutinas = []
        
        # Crear interfaz de login
        self._crear_pantalla_login()
        
        logger.info("Aplicación de alumno iniciada")
    
    def _crear_pantalla_login(self):
        """Crear pantalla de inicio de sesión"""
        # Frame central
        login_frame = ctk.CTkFrame(self, corner_radius=20)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo y título
        titulo = ctk.CTkLabel(
            login_frame,
            text="🏋️ Mi Entrenamiento",
            font=ctk.CTkFont(size=36, weight="bold")
        )
        titulo.pack(pady=(40, 10))
        
        subtitulo = ctk.CTkLabel(
            login_frame,
            text="Acceso para Alumnos",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        subtitulo.pack(pady=(0, 40))
        
        # Campos de login
        self.entry_email = ctk.CTkEntry(
            login_frame,
            placeholder_text="📧 Correo electrónico",
            width=300,
            height=45,
            font=ctk.CTkFont(size=14)
        )
        self.entry_email.pack(pady=10, padx=40)
        
        self.entry_password = ctk.CTkEntry(
            login_frame,
            placeholder_text="🔒 Contraseña",
            show="*",
            width=300,
            height=45,
            font=ctk.CTkFont(size=14)
        )
        self.entry_password.pack(pady=10, padx=40)
        
        # Label para errores
        self.label_error = ctk.CTkLabel(
            login_frame,
            text="",
            text_color="red",
            font=ctk.CTkFont(size=12)
        )
        self.label_error.pack(pady=5)
        
        # Indicador de conectividad
        self.label_conectividad = ctk.CTkLabel(
            login_frame,
            text="",
            font=ctk.CTkFont(size=11)
        )
        self.label_conectividad.pack(pady=5)
        
        # Botón de login
        btn_login = ctk.CTkButton(
            login_frame,
            text="Iniciar Sesión",
            command=self._hacer_login,
            width=300,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        btn_login.pack(pady=20, padx=40)
        
        # Bind Enter key
        self.entry_password.bind('<Return>', lambda e: self._hacer_login())
        
        # Verificar conectividad inicial
        self._actualizar_estado_conectividad()
        
        # Link de ayuda
        help_label = ctk.CTkLabel(
            login_frame,
            text="¿Olvidaste tu contraseña? Contacta a tu entrenador",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        help_label.pack(pady=(10, 40))
    
    def _actualizar_estado_conectividad(self):
        """Actualizar indicador de conectividad"""
        if cliente_api.gestor_conectividad.esta_conectado():
            self.label_conectividad.configure(
                text="🟢 Conectado al servidor",
                text_color="green"
            )
        else:
            self.label_conectividad.configure(
                text="🔴 Sin conexión - Modo offline disponible",
                text_color="orange"
            )
        
        # Actualizar cada 10 segundos
        self.after(10000, self._actualizar_estado_conectividad)
    
    def _hacer_login(self):
        """Procesar inicio de sesión"""
        email = self.entry_email.get()
        password = self.entry_password.get()
        
        # Validar campos
        if not email or not password:
            self.label_error.configure(text="Por favor completa todos los campos")
            return
        
        # Limpiar error
        self.label_error.configure(text="")
        
        # Intentar login
        logger.info(f"Intentando login para {email}")
        
        usuario = cliente_api.login(email, password)
        
        if usuario:
            self.usuario_actual = usuario
            logger.info(f"Login exitoso: {usuario['nombre']}")
            
            # Cambiar a pantalla principal
            self._crear_pantalla_principal()
        else:
            self.label_error.configure(
                text="❌ Credenciales inválidas o sin conexión"
            )
            logger.warning(f"Login fallido para {email}")
    
    def _crear_pantalla_principal(self):
        """Crear pantalla principal de la aplicación"""
        # Limpiar ventana
        for widget in self.winfo_children():
            widget.destroy()
        
        # Sidebar
        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        sidebar.grid(row=0, column=0, rowspan=4, sticky="nsew")
        sidebar.grid_rowconfigure(10, weight=1)
        
        # Info del usuario
        user_frame = ctk.CTkFrame(sidebar)
        user_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        user_icon = ctk.CTkLabel(
            user_frame,
            text="👤",
            font=ctk.CTkFont(size=40)
        )
        user_icon.pack(pady=5)
        
        user_name = ctk.CTkLabel(
            user_frame,
            text=self.usuario_actual['nombre'],
            font=ctk.CTkFont(size=14, weight="bold"),
            wraplength=180
        )
        user_name.pack(pady=5)
        
        # Botones de navegación
        botones = [
            ("🏠 Inicio", self.mostrar_inicio),
            ("💪 Mis Rutinas", self.mostrar_rutinas),
            ("📊 Mi Progreso", self.mostrar_progreso),
            ("📅 Calendario", self.mostrar_calendario),
            ("✉️ Mensajes", self.mostrar_mensajes),
            ("⚙️ Configuración", self.mostrar_configuracion),
        ]
        
        for i, (texto, comando) in enumerate(botones, start=1):
            btn = ctk.CTkButton(
                sidebar,
                text=texto,
                command=comando,
                font=ctk.CTkFont(size=13),
                height=40
            )
            btn.grid(row=i, column=0, padx=15, pady=5, sticky="ew")
        
        # Botón de cerrar sesión
        btn_logout = ctk.CTkButton(
            sidebar,
            text="🚪 Cerrar Sesión",
            command=self._cerrar_sesion,
            font=ctk.CTkFont(size=12),
            fg_color="red",
            hover_color="darkred"
        )
        btn_logout.grid(row=11, column=0, padx=15, pady=20, sticky="ew")
        
        # Frame de contenido
        self.content_frame = ctk.CTkFrame(self, corner_radius=0)
        self.content_frame.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=10, pady=10)
        
        # Configurar grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Mostrar inicio por defecto
        self.mostrar_inicio()
    
    def _limpiar_contenido(self):
        """Limpiar el frame de contenido"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def mostrar_inicio(self):
        """Mostrar pantalla de inicio con resumen"""
        self._limpiar_contenido()
        
        # Título
        titulo = ctk.CTkLabel(
            self.content_frame,
            text=f"¡Hola, {self.usuario_actual['nombre']}! 👋",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        titulo.pack(pady=30)
        
        # Resumen del día
        resumen_frame = ctk.CTkFrame(self.content_frame)
        resumen_frame.pack(fill="both", expand=True, padx=40, pady=20)
        
        resumen_titulo = ctk.CTkLabel(
            resumen_frame,
            text="📅 Tu Día de Hoy",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        resumen_titulo.pack(pady=20)
        
        # Cards de resumen
        cards_frame = ctk.CTkFrame(resumen_frame)
        cards_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Card de rutina del día
        self._crear_card_resumen(
            cards_frame, 0, 0,
            "💪 Entrenamiento de Hoy",
            "Rutina de Fuerza",
            "45 minutos - 8 ejercicios"
        )
        
        # Card de progreso
        self._crear_card_resumen(
            cards_frame, 0, 1,
            "🏆 Progreso Semanal",
            "5/7 días",
            "¡Excelente trabajo!"
        )
        
        # Card de mensajes
        self._crear_card_resumen(
            cards_frame, 0, 2,
            "✉️ Mensajes Nuevos",
            "2 mensajes",
            "De tu entrenador"
        )
        
        # Botón de acción rápida
        btn_entrenar = ctk.CTkButton(
            resumen_frame,
            text="🚀 Comenzar Entrenamiento",
            command=self.mostrar_rutinas,
            font=ctk.CTkFont(size=18, weight="bold"),
            height=60
        )
        btn_entrenar.pack(pady=30)
    
    def _crear_card_resumen(self, parent, row, col, titulo, valor, descripcion):
        """Crear card de resumen"""
        card = ctk.CTkFrame(parent, corner_radius=15)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        titulo_label = ctk.CTkLabel(
            card,
            text=titulo,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        titulo_label.pack(pady=(20, 10))
        
        valor_label = ctk.CTkLabel(
            card,
            text=valor,
            font=ctk.CTkFont(size=28, weight="bold")
        )
        valor_label.pack(pady=10)
        
        desc_label = ctk.CTkLabel(
            card,
            text=descripcion,
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        desc_label.pack(pady=(0, 20))
    
    def mostrar_rutinas(self):
        """Mostrar rutinas de entrenamiento"""
        self._limpiar_contenido()
        
        titulo = ctk.CTkLabel(
            self.content_frame,
            text="💪 Mis Rutinas de Entrenamiento",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        titulo.pack(pady=30)
        
        # Botón de sincronizar
        btn_sync = ctk.CTkButton(
            self.content_frame,
            text="🔄 Sincronizar con Servidor",
            command=self._sincronizar_rutinas,
            font=ctk.CTkFont(size=14)
        )
        btn_sync.pack(pady=10)
        
        # Lista de rutinas
        rutinas_frame = ctk.CTkScrollableFrame(self.content_frame, height=500)
        rutinas_frame.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Simular rutinas (en producción vendría del servidor)
        rutinas_ejemplo = [
            {
                "nombre": "Rutina de Fuerza - Día A",
                "descripcion": "Enfoque en pecho, hombros y tríceps",
                "duracion": "45 minutos",
                "ejercicios": 8
            },
            {
                "nombre": "Rutina de Piernas",
                "descripcion": "Entrenamiento completo de tren inferior",
                "duracion": "60 minutos",
                "ejercicios": 10
            },
            {
                "nombre": "Cardio y Resistencia",
                "descripcion": "Mejora tu capacidad cardiovascular",
                "duracion": "30 minutos",
                "ejercicios": 5
            }
        ]
        
        for rutina in rutinas_ejemplo:
            self._crear_card_rutina(rutinas_frame, rutina)
    
    def _crear_card_rutina(self, parent, rutina: Dict):
        """Crear card de rutina"""
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.pack(fill="x", pady=10, padx=10)
        
        # Nombre
        nombre_label = ctk.CTkLabel(
            card,
            text=rutina["nombre"],
            font=ctk.CTkFont(size=18, weight="bold")
        )
        nombre_label.pack(pady=(15, 5), padx=15, anchor="w")
        
        # Descripción
        desc_label = ctk.CTkLabel(
            card,
            text=rutina["descripcion"],
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        desc_label.pack(pady=5, padx=15, anchor="w")
        
        # Info
        info_frame = ctk.CTkFrame(card)
        info_frame.pack(fill="x", padx=15, pady=10)
        
        duracion_label = ctk.CTkLabel(
            info_frame,
            text=f"⏱️ {rutina['duracion']}",
            font=ctk.CTkFont(size=11)
        )
        duracion_label.pack(side="left", padx=10)
        
        ejercicios_label = ctk.CTkLabel(
            info_frame,
            text=f"💪 {rutina['ejercicios']} ejercicios",
            font=ctk.CTkFont(size=11)
        )
        ejercicios_label.pack(side="left", padx=10)
        
        # Botón
        btn_ver = ctk.CTkButton(
            card,
            text="Ver Detalles",
            command=lambda: self._ver_detalle_rutina(rutina),
            width=150
        )
        btn_ver.pack(pady=15)
    
    def _ver_detalle_rutina(self, rutina: Dict):
        """Mostrar detalle de rutina"""
        logger.info(f"Ver detalle de rutina: {rutina['nombre']}")
        # TODO: Implementar vista de detalle
    
    def _sincronizar_rutinas(self):
        """Sincronizar rutinas con el servidor"""
        logger.info("Sincronizando rutinas...")
        # TODO: Implementar sincronización real
        self.mostrar_rutinas()
    
    def mostrar_progreso(self):
        """Mostrar progreso del alumno"""
        self._limpiar_contenido()
        
        titulo = ctk.CTkLabel(
            self.content_frame,
            text="📊 Mi Progreso",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        titulo.pack(pady=30)
        
        mensaje = ctk.CTkLabel(
            self.content_frame,
            text="Funcionalidad en desarrollo...",
            font=ctk.CTkFont(size=16)
        )
        mensaje.pack(pady=50)
    
    def mostrar_calendario(self):
        """Mostrar calendario de entrenamientos"""
        self._limpiar_contenido()
        
        titulo = ctk.CTkLabel(
            self.content_frame,
            text="📅 Mi Calendario",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        titulo.pack(pady=30)
        
        mensaje = ctk.CTkLabel(
            self.content_frame,
            text="Funcionalidad en desarrollo...",
            font=ctk.CTkFont(size=16)
        )
        mensaje.pack(pady=50)
    
    def mostrar_mensajes(self):
        """Mostrar mensajes del entrenador"""
        self._limpiar_contenido()
        
        titulo = ctk.CTkLabel(
            self.content_frame,
            text="✉️ Mensajes de tu Entrenador",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        titulo.pack(pady=30)
        
        mensaje = ctk.CTkLabel(
            self.content_frame,
            text="Funcionalidad en desarrollo...",
            font=ctk.CTkFont(size=16)
        )
        mensaje.pack(pady=50)
    
    def mostrar_configuracion(self):
        """Mostrar configuración de la app"""
        self._limpiar_contenido()
        
        titulo = ctk.CTkLabel(
            self.content_frame,
            text="⚙️ Configuración",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        titulo.pack(pady=30)
        
        mensaje = ctk.CTkLabel(
            self.content_frame,
            text="Funcionalidad en desarrollo...",
            font=ctk.CTkFont(size=16)
        )
        mensaje.pack(pady=50)
    
    def _cerrar_sesion(self):
        """Cerrar sesión del usuario"""
        self.usuario_actual = None
        cliente_api.token_jwt = None
        
        # Volver a pantalla de login
        for widget in self.winfo_children():
            widget.destroy()
        
        self._crear_pantalla_login()
        
        logger.info("Sesión cerrada")


if __name__ == "__main__":
    app = AplicacionHija()
    app.mainloop()
