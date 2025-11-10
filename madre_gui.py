"""
Interfaz Gráfica Administrativa para Entrenador Personal
Gestión completa de alumnos, rutinas, evaluaciones y estadísticas
TODOS LOS TEXTOS EN CASTELLANO
"""

import customtkinter as ctk
from typing import Optional, List
from datetime import datetime, timedelta
import threading

from madre_db import gestor_bd, Alumno
from config.settings import config
from shared.logger import obtener_logger

# Configurar logger
logger = obtener_logger(__name__)


class AplicacionMadre(ctk.CTk):
    """Aplicación principal administrativa del entrenador"""
    
    def __init__(self):
        super().__init__()
        
        # Configuración de ventana
        self.title("🏋️ Gestión de Gimnasio - Panel Entrenador")
        self.geometry("1400x900")
        
        # Variables de estado
        self.usuario_actual = None
        
        # Crear interfaz
        self._crear_interfaz()
        
        logger.info("Interfaz gráfica administrativa iniciada")
    
    def _crear_interfaz(self):
        """Crear la interfaz principal"""
        # Sidebar con navegación
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)
        
        # Logo y título
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="🏋️ Panel Entrenador",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Botones de navegación
        self.btn_dashboard = ctk.CTkButton(
            self.sidebar,
            text="📊 Tablero Principal",
            command=self.mostrar_dashboard,
            font=ctk.CTkFont(size=14)
        )
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.btn_alumnos = ctk.CTkButton(
            self.sidebar,
            text="👥 Gestión de Alumnos",
            command=self.mostrar_alumnos,
            font=ctk.CTkFont(size=14)
        )
        self.btn_alumnos.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.btn_rutinas = ctk.CTkButton(
            self.sidebar,
            text="💪 Rutinas de Entrenamiento",
            command=self.mostrar_rutinas,
            font=ctk.CTkFont(size=14)
        )
        self.btn_rutinas.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        self.btn_evaluaciones = ctk.CTkButton(
            self.sidebar,
            text="📋 Evaluaciones Corporales",
            command=self.mostrar_evaluaciones,
            font=ctk.CTkFont(size=14)
        )
        self.btn_evaluaciones.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        
        self.btn_pagos = ctk.CTkButton(
            self.sidebar,
            text="💰 Pagos y Membresías",
            command=self.mostrar_pagos,
            font=ctk.CTkFont(size=14)
        )
        self.btn_pagos.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
        
        self.btn_mensajes = ctk.CTkButton(
            self.sidebar,
            text="✉️ Mensajería",
            command=self.mostrar_mensajes,
            font=ctk.CTkFont(size=14)
        )
        self.btn_mensajes.grid(row=6, column=0, padx=20, pady=10, sticky="ew")
        
        self.btn_asistencia = ctk.CTkButton(
            self.sidebar,
            text="✅ Control de Asistencia",
            command=self.mostrar_asistencia,
            font=ctk.CTkFont(size=14)
        )
        self.btn_asistencia.grid(row=7, column=0, padx=20, pady=10, sticky="ew")
        
        # Tema
        self.theme_label = ctk.CTkLabel(
            self.sidebar,
            text="Tema de Interfaz:",
            font=ctk.CTkFont(size=12)
        )
        self.theme_label.grid(row=8, column=0, padx=20, pady=(30, 5))
        
        self.theme_switch = ctk.CTkSwitch(
            self.sidebar,
            text="Modo Oscuro",
            command=self.cambiar_tema,
            font=ctk.CTkFont(size=11)
        )
        self.theme_switch.grid(row=9, column=0, padx=20, pady=5)
        self.theme_switch.select()
        
        # Frame de contenido principal
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=10, pady=10)
        
        # Configurar grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Mostrar dashboard por defecto
        self.mostrar_dashboard()
    
    def cambiar_tema(self):
        """Cambiar entre tema claro y oscuro"""
        if self.theme_switch.get():
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
    
    def limpiar_main_frame(self):
        """Limpiar el frame principal"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def mostrar_dashboard(self):
        """Mostrar tablero principal con estadísticas"""
        self.limpiar_main_frame()
        
        # Título
        titulo = ctk.CTkLabel(
            self.main_frame,
            text="📊 Tablero Principal - Estadísticas del Gimnasio",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        titulo.pack(pady=30)
        
        # Obtener estadísticas
        try:
            stats = gestor_bd.obtener_estadisticas()
            
            # Frame de tarjetas de estadísticas
            stats_frame = ctk.CTkFrame(self.main_frame)
            stats_frame.pack(fill="both", expand=True, padx=40, pady=20)
            
            # Configurar grid
            stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
            
            # Tarjeta de alumnos activos
            self._crear_tarjeta_estadistica(
                stats_frame, 0, 0,
                "👥 Alumnos Activos",
                str(stats['alumnos_activos']),
                "Miembros actualmente inscritos"
            )
            
            # Tarjeta de asistencias
            self._crear_tarjeta_estadistica(
                stats_frame, 0, 1,
                "✅ Asistencias del Mes",
                str(stats['asistencias_mes']),
                "Check-ins registrados este mes"
            )
            
            # Tarjeta de ingresos
            self._crear_tarjeta_estadistica(
                stats_frame, 1, 0,
                "💰 Ingresos del Mes",
                f"${stats['ingresos_mes']:.2f}",
                "Total recaudado en el mes actual"
            )
            
            # Tarjeta de rutinas
            self._crear_tarjeta_estadistica(
                stats_frame, 1, 1,
                "💪 Rutinas Activas",
                str(stats['rutinas_activas']),
                "Programas de entrenamiento disponibles"
            )
            
            # Botón de actualizar
            btn_actualizar = ctk.CTkButton(
                self.main_frame,
                text="🔄 Actualizar Estadísticas",
                command=self.mostrar_dashboard,
                font=ctk.CTkFont(size=14),
                height=40
            )
            btn_actualizar.pack(pady=20)
            
        except Exception as e:
            logger.error(f"Error cargando estadísticas: {e}")
            error_label = ctk.CTkLabel(
                self.main_frame,
                text=f"❌ Error cargando estadísticas: {e}",
                font=ctk.CTkFont(size=14),
                text_color="red"
            )
            error_label.pack(pady=50)
    
    def _crear_tarjeta_estadistica(self, parent, row, col, titulo, valor, descripcion):
        """Crear tarjeta de estadística"""
        card = ctk.CTkFrame(parent, corner_radius=15)
        card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        
        titulo_label = ctk.CTkLabel(
            card,
            text=titulo,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        titulo_label.pack(pady=(20, 10))
        
        valor_label = ctk.CTkLabel(
            card,
            text=valor,
            font=ctk.CTkFont(size=40, weight="bold")
        )
        valor_label.pack(pady=10)
        
        desc_label = ctk.CTkLabel(
            card,
            text=descripcion,
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        desc_label.pack(pady=(0, 20))
    
    def mostrar_alumnos(self):
        """Mostrar gestión de alumnos"""
        self.limpiar_main_frame()
        
        # Título
        titulo = ctk.CTkLabel(
            self.main_frame,
            text="👥 Gestión de Alumnos",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        titulo.pack(pady=20)
        
        # Frame de botones de acción
        acciones_frame = ctk.CTkFrame(self.main_frame)
        acciones_frame.pack(fill="x", padx=40, pady=10)
        
        btn_nuevo = ctk.CTkButton(
            acciones_frame,
            text="➕ Nuevo Alumno",
            command=self.dialogo_nuevo_alumno,
            font=ctk.CTkFont(size=14),
            height=40
        )
        btn_nuevo.pack(side="left", padx=10)
        
        btn_actualizar = ctk.CTkButton(
            acciones_frame,
            text="🔄 Actualizar Lista",
            command=self.mostrar_alumnos,
            font=ctk.CTkFont(size=14),
            height=40
        )
        btn_actualizar.pack(side="left", padx=10)
        
        # Lista de alumnos
        try:
            alumnos = gestor_bd.obtener_alumnos(estado="activo", limite=50)
            
            if not alumnos:
                mensaje = ctk.CTkLabel(
                    self.main_frame,
                    text="No hay alumnos registrados. ¡Agrega el primero!",
                    font=ctk.CTkFont(size=16)
                )
                mensaje.pack(pady=50)
                return
            
            # Frame scrollable para lista
            lista_frame = ctk.CTkScrollableFrame(self.main_frame, height=500)
            lista_frame.pack(fill="both", expand=True, padx=40, pady=20)
            
            # Encabezados
            headers = ["Nombre", "Email", "Teléfono", "Nivel", "Equipo", "Estado"]
            header_frame = ctk.CTkFrame(lista_frame)
            header_frame.pack(fill="x", pady=(0, 10))
            
            for i, header in enumerate(headers):
                label = ctk.CTkLabel(
                    header_frame,
                    text=header,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    width=150
                )
                label.grid(row=0, column=i, padx=5, pady=5, sticky="w")
            
            # Filas de alumnos
            for alumno in alumnos:
                self._crear_fila_alumno(lista_frame, alumno)
        
        except Exception as e:
            logger.error(f"Error cargando alumnos: {e}")
            error_label = ctk.CTkLabel(
                self.main_frame,
                text=f"❌ Error cargando alumnos: {e}",
                font=ctk.CTkFont(size=14),
                text_color="red"
            )
            error_label.pack(pady=50)
    
    def _crear_fila_alumno(self, parent, alumno: Alumno):
        """Crear fila de alumno en la lista"""
        fila = ctk.CTkFrame(parent)
        fila.pack(fill="x", pady=2)
        
        datos = [
            alumno.nombre,
            alumno.email,
            alumno.telefono or "N/A",
            alumno.nivel or "N/A",
            alumno.equipo or "N/A",
            alumno.estado
        ]
        
        for i, dato in enumerate(datos):
            label = ctk.CTkLabel(
                fila,
                text=dato,
                font=ctk.CTkFont(size=11),
                width=150
            )
            label.grid(row=0, column=i, padx=5, pady=5, sticky="w")
    
    def dialogo_nuevo_alumno(self):
        """Mostrar diálogo para crear nuevo alumno"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Nuevo Alumno")
        dialog.geometry("500x600")
        dialog.grab_set()
        
        # Título
        titulo = ctk.CTkLabel(
            dialog,
            text="➕ Registrar Nuevo Alumno",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        titulo.pack(pady=20)
        
        # Frame de formulario
        form_frame = ctk.CTkFrame(dialog)
        form_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Campos
        campos = [
            ("Nombre Completo:", "entry_nombre"),
            ("Email:", "entry_email"),
            ("Contraseña:", "entry_password"),
            ("Teléfono:", "entry_telefono"),
            ("Equipo:", "entry_equipo"),
        ]
        
        entries = {}
        
        for i, (label_text, entry_name) in enumerate(campos):
            label = ctk.CTkLabel(form_frame, text=label_text, font=ctk.CTkFont(size=12))
            label.grid(row=i, column=0, padx=10, pady=10, sticky="w")
            
            if "password" in entry_name:
                entry = ctk.CTkEntry(form_frame, show="*", width=250)
            else:
                entry = ctk.CTkEntry(form_frame, width=250)
            entry.grid(row=i, column=1, padx=10, pady=10)
            entries[entry_name] = entry
        
        # Nivel
        label_nivel = ctk.CTkLabel(form_frame, text="Nivel:", font=ctk.CTkFont(size=12))
        label_nivel.grid(row=len(campos), column=0, padx=10, pady=10, sticky="w")
        
        combo_nivel = ctk.CTkComboBox(
            form_frame,
            values=["principiante", "intermedio", "avanzado"],
            width=250
        )
        combo_nivel.set("principiante")
        combo_nivel.grid(row=len(campos), column=1, padx=10, pady=10)
        
        # Función para guardar
        def guardar():
            try:
                gestor_bd.crear_usuario(
                    nombre=entries["entry_nombre"].get(),
                    email=entries["entry_email"].get(),
                    password=entries["entry_password"].get(),
                    telefono=entries["entry_telefono"].get(),
                    equipo=entries["entry_equipo"].get(),
                    nivel=combo_nivel.get()
                )
                
                dialog.destroy()
                self.mostrar_alumnos()
                
                # Mostrar mensaje de éxito
                self._mostrar_mensaje_exito("Alumno creado exitosamente")
            
            except Exception as e:
                error_label = ctk.CTkLabel(
                    dialog,
                    text=f"❌ Error: {str(e)}",
                    text_color="red",
                    font=ctk.CTkFont(size=11)
                )
                error_label.pack(pady=5)
        
        # Botones
        btn_frame = ctk.CTkFrame(dialog)
        btn_frame.pack(pady=20)
        
        btn_guardar = ctk.CTkButton(
            btn_frame,
            text="💾 Guardar",
            command=guardar,
            width=120
        )
        btn_guardar.pack(side="left", padx=10)
        
        btn_cancelar = ctk.CTkButton(
            btn_frame,
            text="❌ Cancelar",
            command=dialog.destroy,
            width=120
        )
        btn_cancelar.pack(side="left", padx=10)
    
    def _mostrar_mensaje_exito(self, mensaje):
        """Mostrar mensaje de éxito temporal"""
        msg_frame = ctk.CTkFrame(self.main_frame, fg_color="green")
        msg_frame.place(relx=0.5, rely=0.1, anchor="center")
        
        msg_label = ctk.CTkLabel(
            msg_frame,
            text=f"✅ {mensaje}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        msg_label.pack(padx=30, pady=15)
        
        # Auto-ocultar después de 3 segundos
        self.after(3000, msg_frame.destroy)
    
    def mostrar_rutinas(self):
        """Mostrar gestión de rutinas"""
        self.limpiar_main_frame()
        
        titulo = ctk.CTkLabel(
            self.main_frame,
            text="💪 Rutinas de Entrenamiento",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        titulo.pack(pady=30)
        
        mensaje = ctk.CTkLabel(
            self.main_frame,
            text="Funcionalidad en desarrollo...",
            font=ctk.CTkFont(size=16)
        )
        mensaje.pack(pady=50)
    
    def mostrar_evaluaciones(self):
        """Mostrar evaluaciones corporales"""
        self.limpiar_main_frame()
        
        titulo = ctk.CTkLabel(
            self.main_frame,
            text="📋 Evaluaciones Corporales",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        titulo.pack(pady=30)
        
        mensaje = ctk.CTkLabel(
            self.main_frame,
            text="Funcionalidad en desarrollo...",
            font=ctk.CTkFont(size=16)
        )
        mensaje.pack(pady=50)
    
    def mostrar_pagos(self):
        """Mostrar pagos y membresías"""
        self.limpiar_main_frame()
        
        titulo = ctk.CTkLabel(
            self.main_frame,
            text="💰 Pagos y Membresías",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        titulo.pack(pady=30)
        
        mensaje = ctk.CTkLabel(
            self.main_frame,
            text="Funcionalidad en desarrollo...",
            font=ctk.CTkFont(size=16)
        )
        mensaje.pack(pady=50)
    
    def mostrar_mensajes(self):
        """Mostrar sistema de mensajería"""
        self.limpiar_main_frame()
        
        titulo = ctk.CTkLabel(
            self.main_frame,
            text="✉️ Sistema de Mensajería",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        titulo.pack(pady=30)
        
        mensaje = ctk.CTkLabel(
            self.main_frame,
            text="Funcionalidad en desarrollo...",
            font=ctk.CTkFont(size=16)
        )
        mensaje.pack(pady=50)
    
    def mostrar_asistencia(self):
        """Mostrar control de asistencia"""
        self.limpiar_main_frame()
        
        titulo = ctk.CTkLabel(
            self.main_frame,
            text="✅ Control de Asistencia",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        titulo.pack(pady=30)
        
        mensaje = ctk.CTkLabel(
            self.main_frame,
            text="Funcionalidad en desarrollo...",
            font=ctk.CTkFont(size=16)
        )
        mensaje.pack(pady=50)


if __name__ == "__main__":
    app = AplicacionMadre()
    app.mainloop()
