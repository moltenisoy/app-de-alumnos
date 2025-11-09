# -*- coding: utf-8 -*-
"""
Extensión de GUI Avanzada para Aplicación Hija
Implementa interfaces profesionales para funcionalidades avanzadas.
"""

import customtkinter as ctk
from typing import Optional, Callable, List
from funcionalidades_avanzadas import (
    gestor_funcionalidades,
    ProgressPhoto,
    Objetivo,
    Logro
)
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image


class PanelProgreso(ctk.CTkScrollableFrame):
    """Panel interactivo para visualización de progreso."""
    
    def __init__(self, master, user_id: int, **kwargs):
        super().__init__(master, **kwargs)
        self.user_id = user_id
        
        # Título
        titulo = ctk.CTkLabel(
            self,
            text="📊 Mi Progreso",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        titulo.pack(pady=(20, 10))
        
        # Tabs para diferentes vistas
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Tabs
        self.tabview.add("Fotos")
        self.tabview.add("Objetivos")
        self.tabview.add("Logros")
        self.tabview.add("Análisis")
        
        self._crear_tab_fotos()
        self._crear_tab_objetivos()
        self._crear_tab_logros()
        self._crear_tab_analisis()
    
    def _crear_tab_fotos(self):
        """Crea tab de línea de tiempo de fotos."""
        tab = self.tabview.tab("Fotos")
        
        # Botón para nueva foto
        btn_nueva = ctk.CTkButton(
            tab,
            text="📸 Nueva Foto de Progreso",
            command=self._mostrar_dialogo_nueva_foto,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        btn_nueva.pack(pady=10)
        
        # Frame para timeline
        self.frame_timeline = ctk.CTkScrollableFrame(tab, height=400)
        self.frame_timeline.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._cargar_fotos_progreso()
    
    def _cargar_fotos_progreso(self):
        """Carga y muestra fotos de progreso."""
        # Limpiar frame
        for widget in self.frame_timeline.winfo_children():
            widget.destroy()
        
        # Obtener fotos
        fotos = gestor_funcionalidades.obtener_linea_tiempo_progreso(
            self.user_id, limite=20
        )
        
        if not fotos:
            lbl_vacio = ctk.CTkLabel(
                self.frame_timeline,
                text="No hay fotos de progreso aún.\n¡Sube tu primera foto!",
                font=ctk.CTkFont(size=16)
            )
            lbl_vacio.pack(pady=50)
            return
        
        # Mostrar cada foto
        for i, foto in enumerate(fotos):
            self._crear_tarjeta_foto(foto, i)
    
    def _crear_tarjeta_foto(self, foto: ProgressPhoto, index: int):
        """Crea una tarjeta para mostrar foto de progreso."""
        # Frame de tarjeta
        card = ctk.CTkFrame(self.frame_timeline, corner_radius=10)
        card.pack(fill="x", padx=10, pady=10)
        
        # Fecha
        fecha_obj = datetime.fromisoformat(foto.fecha)
        fecha_str = fecha_obj.strftime("%d/%m/%Y")
        
        lbl_fecha = ctk.CTkLabel(
            card,
            text=f"📅 {fecha_str}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        lbl_fecha.pack(pady=(10, 5), anchor="w", padx=10)
        
        # Información
        info_frame = ctk.CTkFrame(card)
        info_frame.pack(fill="x", padx=10, pady=5)
        
        lbl_peso = ctk.CTkLabel(
            info_frame,
            text=f"⚖️ Peso: {foto.peso_kg} kg",
            font=ctk.CTkFont(size=12)
        )
        lbl_peso.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Medidas
        if foto.medidas:
            medidas_str = " | ".join([f"{k}: {v}" for k, v in foto.medidas.items()])
            lbl_medidas = ctk.CTkLabel(
                info_frame,
                text=f"📏 {medidas_str}",
                font=ctk.CTkFont(size=11)
            )
            lbl_medidas.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        # Notas
        if foto.notas:
            lbl_notas = ctk.CTkLabel(
                card,
                text=f"💭 {foto.notas}",
                font=ctk.CTkFont(size=11),
                wraplength=400
            )
            lbl_notas.pack(pady=5, padx=10, anchor="w")
        
        # Botón para ver imagen completa
        btn_ver = ctk.CTkButton(
            card,
            text="Ver Foto Completa",
            command=lambda f=foto: self._mostrar_foto_completa(f),
            width=150
        )
        btn_ver.pack(pady=10)
    
    def _mostrar_foto_completa(self, foto: ProgressPhoto):
        """Muestra foto en ventana emergente."""
        ventana = ctk.CTkToplevel(self)
        ventana.title("Foto de Progreso")
        ventana.geometry("600x700")
        
        try:
            # Decodificar imagen
            imagen_bytes = base64.b64decode(foto.imagen_base64)
            imagen = Image.open(BytesIO(imagen_bytes))
            
            # Redimensionar si es muy grande
            max_size = (550, 550)
            imagen.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Mostrar (nota: CTk no tiene soporte directo para PIL, 
            # en producción usar CTkImage)
            lbl_info = ctk.CTkLabel(
                ventana,
                text=f"Foto del {datetime.fromisoformat(foto.fecha).strftime('%d/%m/%Y')}\n"
                     f"Peso: {foto.peso_kg} kg",
                font=ctk.CTkFont(size=14)
            )
            lbl_info.pack(pady=20)
            
        except Exception as e:
            lbl_error = ctk.CTkLabel(
                ventana,
                text=f"Error al cargar imagen: {e}",
                font=ctk.CTkFont(size=12)
            )
            lbl_error.pack(pady=20)
    
    def _mostrar_dialogo_nueva_foto(self):
        """Muestra diálogo para subir nueva foto."""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Nueva Foto de Progreso")
        dialogo.geometry("500x600")
        
        # Título
        lbl_titulo = ctk.CTkLabel(
            dialogo,
            text="📸 Nueva Foto de Progreso",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        lbl_titulo.pack(pady=20)
        
        # Campos
        frame_campos = ctk.CTkFrame(dialogo)
        frame_campos.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Peso
        lbl_peso = ctk.CTkLabel(frame_campos, text="Peso (kg):")
        lbl_peso.pack(pady=(10, 5))
        entry_peso = ctk.CTkEntry(frame_campos, placeholder_text="70.5")
        entry_peso.pack(pady=5)
        
        # Medidas
        lbl_medidas = ctk.CTkLabel(frame_campos, text="Medidas (opcional):")
        lbl_medidas.pack(pady=(15, 5))
        
        medidas_frame = ctk.CTkFrame(frame_campos)
        medidas_frame.pack(fill="x", padx=10, pady=5)
        
        # Cintura
        lbl_cintura = ctk.CTkLabel(medidas_frame, text="Cintura (cm):")
        lbl_cintura.grid(row=0, column=0, padx=5, pady=5)
        entry_cintura = ctk.CTkEntry(medidas_frame, width=100)
        entry_cintura.grid(row=0, column=1, padx=5, pady=5)
        
        # Pecho
        lbl_pecho = ctk.CTkLabel(medidas_frame, text="Pecho (cm):")
        lbl_pecho.grid(row=1, column=0, padx=5, pady=5)
        entry_pecho = ctk.CTkEntry(medidas_frame, width=100)
        entry_pecho.grid(row=1, column=1, padx=5, pady=5)
        
        # Notas
        lbl_notas = ctk.CTkLabel(frame_campos, text="Notas:")
        lbl_notas.pack(pady=(15, 5))
        textbox_notas = ctk.CTkTextbox(frame_campos, height=100)
        textbox_notas.pack(fill="x", padx=10, pady=5)
        
        # Botón guardar
        def guardar():
            try:
                peso = float(entry_peso.get())
                medidas = {}
                
                if entry_cintura.get():
                    medidas['cintura'] = float(entry_cintura.get())
                if entry_pecho.get():
                    medidas['pecho'] = float(entry_pecho.get())
                
                notas = textbox_notas.get("1.0", "end-1c")
                
                # Nota: En producción, aquí se seleccionaría archivo de imagen
                # Por ahora creamos placeholder
                
                dialogo.destroy()
                self._cargar_fotos_progreso()
                
            except ValueError:
                lbl_error = ctk.CTkLabel(
                    dialogo,
                    text="❌ Error: Valores inválidos",
                    text_color="red"
                )
                lbl_error.pack(pady=10)
        
        btn_guardar = ctk.CTkButton(
            dialogo,
            text="💾 Guardar",
            command=guardar,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        btn_guardar.pack(pady=20)
    
    def _crear_tab_objetivos(self):
        """Crea tab de gestión de objetivos."""
        tab = self.tabview.tab("Objetivos")
        
        # Botón para nuevo objetivo
        btn_nuevo = ctk.CTkButton(
            tab,
            text="🎯 Nuevo Objetivo",
            command=self._mostrar_dialogo_nuevo_objetivo,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        btn_nuevo.pack(pady=10)
        
        # Frame para objetivos
        self.frame_objetivos = ctk.CTkScrollableFrame(tab, height=400)
        self.frame_objetivos.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._cargar_objetivos()
    
    def _cargar_objetivos(self):
        """Carga y muestra objetivos."""
        # Limpiar frame
        for widget in self.frame_objetivos.winfo_children():
            widget.destroy()
        
        # Obtener objetivos
        objetivos = gestor_funcionalidades.obtener_objetivos(self.user_id)
        
        if not objetivos:
            lbl_vacio = ctk.CTkLabel(
                self.frame_objetivos,
                text="No hay objetivos definidos.\n¡Crea tu primer objetivo!",
                font=ctk.CTkFont(size=16)
            )
            lbl_vacio.pack(pady=50)
            return
        
        # Mostrar cada objetivo
        for objetivo in objetivos:
            self._crear_tarjeta_objetivo(objetivo)
    
    def _crear_tarjeta_objetivo(self, objetivo: Objetivo):
        """Crea tarjeta de visualización de objetivo."""
        # Frame de tarjeta
        card = ctk.CTkFrame(self.frame_objetivos, corner_radius=10)
        card.pack(fill="x", padx=10, pady=10)
        
        # Nombre
        lbl_nombre = ctk.CTkLabel(
            card,
            text=f"🎯 {objetivo.nombre}",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        lbl_nombre.pack(pady=(15, 5), anchor="w", padx=15)
        
        # Descripción
        if objetivo.descripcion:
            lbl_desc = ctk.CTkLabel(
                card,
                text=objetivo.descripcion,
                font=ctk.CTkFont(size=11),
                wraplength=400
            )
            lbl_desc.pack(pady=5, anchor="w", padx=15)
        
        # Barra de progreso
        progreso_frame = ctk.CTkFrame(card)
        progreso_frame.pack(fill="x", padx=15, pady=10)
        
        # Etiqueta de progreso
        lbl_progreso = ctk.CTkLabel(
            progreso_frame,
            text=f"Progreso: {objetivo.progreso_pct:.1f}%",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        lbl_progreso.pack(pady=5)
        
        # Barra
        barra = ctk.CTkProgressBar(progreso_frame, width=400)
        barra.set(objetivo.progreso_pct / 100)
        barra.pack(pady=5)
        
        # Valores
        lbl_valores = ctk.CTkLabel(
            progreso_frame,
            text=f"{objetivo.valor_actual} / {objetivo.valor_objetivo} {objetivo.unidad}",
            font=ctk.CTkFont(size=11)
        )
        lbl_valores.pack(pady=5)
        
        # Hitos alcanzados
        hitos_alcanzados = [h for h in objetivo.hitos if h['alcanzado']]
        if hitos_alcanzados:
            lbl_hitos = ctk.CTkLabel(
                card,
                text=f"✨ Hitos alcanzados: {len(hitos_alcanzados)}/{len(objetivo.hitos)}",
                font=ctk.CTkFont(size=11)
            )
            lbl_hitos.pack(pady=5, padx=15, anchor="w")
        
        # Estado
        if objetivo.completado:
            lbl_completado = ctk.CTkLabel(
                card,
                text="✅ ¡OBJETIVO COMPLETADO!",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="green"
            )
            lbl_completado.pack(pady=10)
    
    def _mostrar_dialogo_nuevo_objetivo(self):
        """Muestra diálogo para crear nuevo objetivo."""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Nuevo Objetivo")
        dialogo.geometry("500x600")
        
        # Título
        lbl_titulo = ctk.CTkLabel(
            dialogo,
            text="🎯 Crear Nuevo Objetivo",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        lbl_titulo.pack(pady=20)
        
        # Frame de campos
        frame = ctk.CTkFrame(dialogo)
        frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Nombre
        lbl_nombre = ctk.CTkLabel(frame, text="Nombre del Objetivo:")
        lbl_nombre.pack(pady=(10, 5))
        entry_nombre = ctk.CTkEntry(frame, placeholder_text="Ej: Perder 10kg")
        entry_nombre.pack(pady=5)
        
        # Tipo
        lbl_tipo = ctk.CTkLabel(frame, text="Tipo:")
        lbl_tipo.pack(pady=(15, 5))
        combo_tipo = ctk.CTkComboBox(
            frame,
            values=["peso", "fuerza", "resistencia", "flexibilidad"]
        )
        combo_tipo.pack(pady=5)
        
        # Valor objetivo
        lbl_objetivo = ctk.CTkLabel(frame, text="Valor Objetivo:")
        lbl_objetivo.pack(pady=(15, 5))
        entry_objetivo = ctk.CTkEntry(frame, placeholder_text="Ej: 70")
        entry_objetivo.pack(pady=5)
        
        # Unidad
        lbl_unidad = ctk.CTkLabel(frame, text="Unidad:")
        lbl_unidad.pack(pady=(15, 5))
        entry_unidad = ctk.CTkEntry(frame, placeholder_text="Ej: kg")
        entry_unidad.pack(pady=5)
        
        # Descripción
        lbl_desc = ctk.CTkLabel(frame, text="Descripción (opcional):")
        lbl_desc.pack(pady=(15, 5))
        textbox_desc = ctk.CTkTextbox(frame, height=80)
        textbox_desc.pack(fill="x", padx=10, pady=5)
        
        # Botón crear
        def crear():
            try:
                nombre = entry_nombre.get()
                tipo = combo_tipo.get()
                valor_objetivo = float(entry_objetivo.get())
                unidad = entry_unidad.get()
                descripcion = textbox_desc.get("1.0", "end-1c")
                
                gestor_funcionalidades.crear_objetivo(
                    self.user_id,
                    nombre,
                    descripcion,
                    tipo,
                    valor_objetivo,
                    unidad
                )
                
                dialogo.destroy()
                self._cargar_objetivos()
                
            except ValueError:
                lbl_error = ctk.CTkLabel(
                    dialogo,
                    text="❌ Error: Valores inválidos",
                    text_color="red"
                )
                lbl_error.pack(pady=10)
        
        btn_crear = ctk.CTkButton(
            dialogo,
            text="✨ Crear Objetivo",
            command=crear,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        btn_crear.pack(pady=20)
    
    def _crear_tab_logros(self):
        """Crea tab de logros y achievements."""
        tab = self.tabview.tab("Logros")
        
        # Título
        lbl_titulo = ctk.CTkLabel(
            tab,
            text="🏆 Mis Logros",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        lbl_titulo.pack(pady=20)
        
        # Frame para logros
        self.frame_logros = ctk.CTkScrollableFrame(tab, height=500)
        self.frame_logros.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._cargar_logros()
    
    def _cargar_logros(self):
        """Carga y muestra logros."""
        # Limpiar frame
        for widget in self.frame_logros.winfo_children():
            widget.destroy()
        
        # Obtener logros
        logros = gestor_funcionalidades.obtener_logros(self.user_id)
        
        if not logros:
            lbl_vacio = ctk.CTkLabel(
                self.frame_logros,
                text="No has obtenido logros aún.\n¡Sigue entrenando para desbloquearlos!",
                font=ctk.CTkFont(size=16)
            )
            lbl_vacio.pack(pady=50)
            return
        
        # Agrupar por categoría
        por_categoria = {}
        for logro in logros:
            if logro.categoria not in por_categoria:
                por_categoria[logro.categoria] = []
            por_categoria[logro.categoria].append(logro)
        
        # Mostrar por categoría
        for categoria, logros_cat in por_categoria.items():
            self._crear_seccion_categoria(categoria, logros_cat)
    
    def _crear_seccion_categoria(self, categoria: str, logros: List[Logro]):
        """Crea sección de logros por categoría."""
        # Frame de categoría
        cat_frame = ctk.CTkFrame(self.frame_logros, corner_radius=10)
        cat_frame.pack(fill="x", padx=10, pady=15)
        
        # Título de categoría
        lbl_cat = ctk.CTkLabel(
            cat_frame,
            text=f"📂 {categoria.upper()}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        lbl_cat.pack(pady=10, anchor="w", padx=15)
        
        # Grid de logros
        grid_frame = ctk.CTkFrame(cat_frame)
        grid_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        for i, logro in enumerate(logros):
            row = i // 3
            col = i % 3
            self._crear_badge_logro(grid_frame, logro, row, col)
    
    def _crear_badge_logro(self, parent, logro: Logro, row: int, col: int):
        """Crea badge individual de logro."""
        badge = ctk.CTkFrame(parent, corner_radius=8, width=140, height=140)
        badge.grid(row=row, column=col, padx=5, pady=5)
        badge.grid_propagate(False)
        
        # Icono
        lbl_icono = ctk.CTkLabel(
            badge,
            text=logro.icono,
            font=ctk.CTkFont(size=40)
        )
        lbl_icono.pack(pady=(15, 5))
        
        # Nombre
        lbl_nombre = ctk.CTkLabel(
            badge,
            text=logro.nombre,
            font=ctk.CTkFont(size=11, weight="bold"),
            wraplength=120
        )
        lbl_nombre.pack(pady=5)
        
        # Nivel
        if logro.nivel > 1:
            lbl_nivel = ctk.CTkLabel(
                badge,
                text=f"Nivel {logro.nivel}",
                font=ctk.CTkFont(size=9),
                text_color="gold"
            )
            lbl_nivel.pack(pady=2)
    
    def _crear_tab_analisis(self):
        """Crea tab de análisis de rendimiento."""
        tab = self.tabview.tab("Análisis")
        
        # Título
        lbl_titulo = ctk.CTkLabel(
            tab,
            text="📈 Análisis de Rendimiento",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        lbl_titulo.pack(pady=20)
        
        # Selector de período
        periodo_frame = ctk.CTkFrame(tab)
        periodo_frame.pack(pady=10)
        
        lbl_periodo = ctk.CTkLabel(
            periodo_frame,
            text="Período:",
            font=ctk.CTkFont(size=12)
        )
        lbl_periodo.pack(side="left", padx=5)
        
        combo_periodo = ctk.CTkComboBox(
            periodo_frame,
            values=["7 días", "30 días", "90 días", "1 año"],
            command=lambda v: self._actualizar_analisis(v)
        )
        combo_periodo.pack(side="left", padx=5)
        combo_periodo.set("30 días")
        
        # Frame para análisis
        self.frame_analisis = ctk.CTkScrollableFrame(tab, height=400)
        self.frame_analisis.pack(fill="both", expand=True, padx=20, pady=10)
        
        self._actualizar_analisis("30 días")
    
    def _actualizar_analisis(self, periodo: str):
        """Actualiza análisis según período."""
        # Limpiar frame
        for widget in self.frame_analisis.winfo_children():
            widget.destroy()
        
        # Convertir período a días
        dias = {
            "7 días": 7,
            "30 días": 30,
            "90 días": 90,
            "1 año": 365
        }.get(periodo, 30)
        
        # Obtener análisis
        analisis = gestor_funcionalidades.obtener_analisis_rendimiento(
            self.user_id, dias=dias
        )
        
        if not analisis['ejercicios']:
            lbl_vacio = ctk.CTkLabel(
                self.frame_analisis,
                text="No hay datos de entrenamiento en este período.",
                font=ctk.CTkFont(size=14)
            )
            lbl_vacio.pack(pady=50)
            return
        
        # Mostrar métricas de ejercicios
        lbl_ejercicios = ctk.CTkLabel(
            self.frame_analisis,
            text="💪 Ejercicios",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        lbl_ejercicios.pack(pady=10, anchor="w")
        
        for ejercicio, datos in analisis['ejercicios'].items():
            self._crear_tarjeta_ejercicio(ejercicio, datos)
        
        # Mostrar métricas de recuperación
        if analisis['recuperacion']['calidad_sueno_promedio']:
            lbl_recuperacion = ctk.CTkLabel(
                self.frame_analisis,
                text="😴 Recuperación",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            lbl_recuperacion.pack(pady=(20, 10), anchor="w")
            
            self._crear_tarjeta_recuperacion(analisis['recuperacion'])
    
    def _crear_tarjeta_ejercicio(self, nombre: str, datos: dict):
        """Crea tarjeta de análisis de ejercicio."""
        card = ctk.CTkFrame(self.frame_analisis, corner_radius=8)
        card.pack(fill="x", pady=5)
        
        lbl_nombre = ctk.CTkLabel(
            card,
            text=f"🏋️ {nombre}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        lbl_nombre.pack(pady=10, anchor="w", padx=15)
        
        info_grid = ctk.CTkFrame(card)
        info_grid.pack(fill="x", padx=15, pady=5)
        
        metricas = [
            ("Peso Promedio", f"{datos['peso_promedio']:.1f} kg"),
            ("Reps Promedio", f"{datos['reps_promedio']:.0f}"),
            ("Total Sesiones", f"{datos['total_sesiones']}")
        ]
        
        for i, (label, value) in enumerate(metricas):
            lbl = ctk.CTkLabel(info_grid, text=label + ":")
            lbl.grid(row=i, column=0, padx=5, pady=3, sticky="w")
            
            val = ctk.CTkLabel(info_grid, text=value, font=ctk.CTkFont(weight="bold"))
            val.grid(row=i, column=1, padx=5, pady=3, sticky="w")
        
        card.pack(fill="x", pady=5, padx=10)
    
    def _crear_tarjeta_recuperacion(self, datos: dict):
        """Crea tarjeta de análisis de recuperación."""
        card = ctk.CTkFrame(self.frame_analisis, corner_radius=8)
        card.pack(fill="x", pady=5, padx=10)
        
        metricas = [
            ("Calidad Sueño", f"{datos['calidad_sueno_promedio']:.1f}/10"),
            ("Horas Sueño", f"{datos['horas_sueno_promedio']:.1f} hrs"),
            ("Nivel Estrés", f"{datos['nivel_estres_promedio']:.1f}/10")
        ]
        
        info_grid = ctk.CTkFrame(card)
        info_grid.pack(fill="both", expand=True, padx=15, pady=15)
        
        for i, (label, value) in enumerate(metricas):
            lbl = ctk.CTkLabel(info_grid, text=label + ":")
            lbl.grid(row=i, column=0, padx=5, pady=5, sticky="w")
            
            val = ctk.CTkLabel(info_grid, text=value, font=ctk.CTkFont(weight="bold"))
            val.grid(row=i, column=1, padx=5, pady=5, sticky="w")
