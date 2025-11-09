import customtkinter as ctk
from typing import List
from funcionalidades_avanzadas import gestor_funcionalidades, ProgressPhoto, Objetivo, Logro
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image


class PanelProgreso(ctk.CTkScrollableFrame):

    def __init__(self, master, user_id: int, **kwargs):
        super().__init__(master, **kwargs)
        self.user_id = user_id
        titulo = ctk.CTkLabel(self, text='📊 Mi Progreso', font=ctk.CTkFont(
            size=24, weight='bold'))
        titulo.pack(pady=(20, 10))
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill='both', expand=True, padx=20, pady=10)
        self.tabview.add('Fotos')
        self.tabview.add('Objetivos')
        self.tabview.add('Logros')
        self.tabview.add('Análisis')
        self._crear_tab_fotos()
        self._crear_tab_objetivos()
        self._crear_tab_logros()
        self._crear_tab_analisis()

    def _crear_tab_fotos(self):
        tab = self.tabview.tab('Fotos')
        btn_nueva = ctk.CTkButton(tab, text='📸 Nueva Foto de Progreso',
            command=self._mostrar_dialogo_nueva_foto, font=ctk.CTkFont(size
            =14, weight='bold'))
        btn_nueva.pack(pady=10)
        self.frame_timeline = ctk.CTkScrollableFrame(tab, height=400)
        self.frame_timeline.pack(fill='both', expand=True, padx=10, pady=10)
        self._cargar_fotos_progreso()

    def _cargar_fotos_progreso(self):
        for widget in self.frame_timeline.winfo_children():
            widget.destroy()
        fotos = gestor_funcionalidades.obtener_linea_tiempo_progreso(self.
            user_id, limite=20)
        if not fotos:
            lbl_vacio = ctk.CTkLabel(self.frame_timeline, text=
                """No hay fotos de progreso aún.
¡Sube tu primera foto!""",
                font=ctk.CTkFont(size=16))
            lbl_vacio.pack(pady=50)
            return
        for i, foto in enumerate(fotos):
            self._crear_tarjeta_foto(foto, i)

    def _crear_tarjeta_foto(self, foto: ProgressPhoto, index: int):
        card = ctk.CTkFrame(self.frame_timeline, corner_radius=10)
        card.pack(fill='x', padx=10, pady=10)
        fecha_obj = datetime.fromisoformat(foto.fecha)
        fecha_str = fecha_obj.strftime('%d/%m/%Y')
        lbl_fecha = ctk.CTkLabel(card, text=f'📅 {fecha_str}', font=ctk.
            CTkFont(size=14, weight='bold'))
        lbl_fecha.pack(pady=(10, 5), anchor='w', padx=10)
        info_frame = ctk.CTkFrame(card)
        info_frame.pack(fill='x', padx=10, pady=5)
        lbl_peso = ctk.CTkLabel(info_frame, text=
            f'⚖️ Peso: {foto.peso_kg} kg', font=ctk.CTkFont(size=12))
        lbl_peso.grid(row=0, column=0, padx=10, pady=5, sticky='w')
        if foto.medidas:
            medidas_str = ' | '.join([f'{k}: {v}' for k, v in foto.medidas.
                items()])
            lbl_medidas = ctk.CTkLabel(info_frame, text=f'📏 {medidas_str}',
                font=ctk.CTkFont(size=11))
            lbl_medidas.grid(row=1, column=0, padx=10, pady=5, sticky='w')
        if foto.notas:
            lbl_notas = ctk.CTkLabel(card, text=f'💭 {foto.notas}', font=ctk
                .CTkFont(size=11), wraplength=400)
            lbl_notas.pack(pady=5, padx=10, anchor='w')
        btn_ver = ctk.CTkButton(card, text='Ver Foto Completa', command=lambda
            f=foto: self._mostrar_foto_completa(f), width=150)
        btn_ver.pack(pady=10)

    def _mostrar_foto_completa(self, foto: ProgressPhoto):
        ventana = ctk.CTkToplevel(self)
        ventana.title('Foto de Progreso')
        ventana.geometry('600x700')
        try:
            imagen_bytes = base64.b64decode(foto.imagen_base64)
            imagen = Image.open(BytesIO(imagen_bytes))
            max_size = 550, 550
            imagen.thumbnail(max_size, Image.Resampling.LANCZOS)
            lbl_info = ctk.CTkLabel(ventana, text=
                f"""Foto del {datetime.fromisoformat(foto.fecha).strftime('%d/%m/%Y')}
Peso: {foto.peso_kg} kg"""
                , font=ctk.CTkFont(size=14))
            lbl_info.pack(pady=20)
        except Exception as e:
            lbl_error = ctk.CTkLabel(ventana, text=
                f'Error al cargar imagen: {e}', font=ctk.CTkFont(size=12))
            lbl_error.pack(pady=20)

    def _mostrar_dialogo_nueva_foto(self):
        dialogo = ctk.CTkToplevel(self)
        dialogo.title('Nueva Foto de Progreso')
        dialogo.geometry('500x600')
        lbl_titulo = ctk.CTkLabel(dialogo, text='📸 Nueva Foto de Progreso',
            font=ctk.CTkFont(size=20, weight='bold'))
        lbl_titulo.pack(pady=20)
        frame_campos = ctk.CTkFrame(dialogo)
        frame_campos.pack(fill='both', expand=True, padx=20, pady=10)
        lbl_peso = ctk.CTkLabel(frame_campos, text='Peso (kg):')
        lbl_peso.pack(pady=(10, 5))
        entry_peso = ctk.CTkEntry(frame_campos, placeholder_text='70.5')
        entry_peso.pack(pady=5)
        lbl_medidas = ctk.CTkLabel(frame_campos, text='Medidas (opcional):')
        lbl_medidas.pack(pady=(15, 5))
        medidas_frame = ctk.CTkFrame(frame_campos)
        medidas_frame.pack(fill='x', padx=10, pady=5)
        lbl_cintura = ctk.CTkLabel(medidas_frame, text='Cintura (cm):')
        lbl_cintura.grid(row=0, column=0, padx=5, pady=5)
        entry_cintura = ctk.CTkEntry(medidas_frame, width=100)
        entry_cintura.grid(row=0, column=1, padx=5, pady=5)
        lbl_pecho = ctk.CTkLabel(medidas_frame, text='Pecho (cm):')
        lbl_pecho.grid(row=1, column=0, padx=5, pady=5)
        entry_pecho = ctk.CTkEntry(medidas_frame, width=100)
        entry_pecho.grid(row=1, column=1, padx=5, pady=5)
        lbl_notas = ctk.CTkLabel(frame_campos, text='Notas:')
        lbl_notas.pack(pady=(15, 5))
        textbox_notas = ctk.CTkTextbox(frame_campos, height=100)
        textbox_notas.pack(fill='x', padx=10, pady=5)

        def guardar():
            try:
                float(entry_peso.get())
                medidas = {}
                if entry_cintura.get():
                    medidas['cintura'] = float(entry_cintura.get())
                if entry_pecho.get():
                    medidas['pecho'] = float(entry_pecho.get())
                textbox_notas.get('1.0', 'end-1c')
                dialogo.destroy()
                self._cargar_fotos_progreso()
            except ValueError:
                lbl_error = ctk.CTkLabel(dialogo, text=
                    '❌ Error: Valores inválidos', text_color='red')
                lbl_error.pack(pady=10)
        btn_guardar = ctk.CTkButton(dialogo, text='💾 Guardar', command=
            guardar, font=ctk.CTkFont(size=14, weight='bold'))
        btn_guardar.pack(pady=20)

    def _crear_tab_objetivos(self):
        tab = self.tabview.tab('Objetivos')
        btn_nuevo = ctk.CTkButton(tab, text='🎯 Nuevo Objetivo', command=
            self._mostrar_dialogo_nuevo_objetivo, font=ctk.CTkFont(size=14,
            weight='bold'))
        btn_nuevo.pack(pady=10)
        self.frame_objetivos = ctk.CTkScrollableFrame(tab, height=400)
        self.frame_objetivos.pack(fill='both', expand=True, padx=10, pady=10)
        self._cargar_objetivos()

    def _cargar_objetivos(self):
        for widget in self.frame_objetivos.winfo_children():
            widget.destroy()
        objetivos = gestor_funcionalidades.obtener_objetivos(self.user_id)
        if not objetivos:
            lbl_vacio = ctk.CTkLabel(self.frame_objetivos, text=
                """No hay objetivos definidos.
¡Crea tu primer objetivo!""",
                font=ctk.CTkFont(size=16))
            lbl_vacio.pack(pady=50)
            return
        for objetivo in objetivos:
            self._crear_tarjeta_objetivo(objetivo)

    def _crear_tarjeta_objetivo(self, objetivo: Objetivo):
        card = ctk.CTkFrame(self.frame_objetivos, corner_radius=10)
        card.pack(fill='x', padx=10, pady=10)
        lbl_nombre = ctk.CTkLabel(card, text=f'🎯 {objetivo.nombre}', font=
            ctk.CTkFont(size=16, weight='bold'))
        lbl_nombre.pack(pady=(15, 5), anchor='w', padx=15)
        if objetivo.descripcion:
            lbl_desc = ctk.CTkLabel(card, text=objetivo.descripcion, font=
                ctk.CTkFont(size=11), wraplength=400)
            lbl_desc.pack(pady=5, anchor='w', padx=15)
        progreso_frame = ctk.CTkFrame(card)
        progreso_frame.pack(fill='x', padx=15, pady=10)
        lbl_progreso = ctk.CTkLabel(progreso_frame, text=
            f'Progreso: {objetivo.progreso_pct:.1f}%', font=ctk.CTkFont(
            size=12, weight='bold'))
        lbl_progreso.pack(pady=5)
        barra = ctk.CTkProgressBar(progreso_frame, width=400)
        barra.set(objetivo.progreso_pct / 100)
        barra.pack(pady=5)
        lbl_valores = ctk.CTkLabel(progreso_frame, text=
            f'{objetivo.valor_actual} / {objetivo.valor_objetivo} {objetivo.unidad}'
            , font=ctk.CTkFont(size=11))
        lbl_valores.pack(pady=5)
        hitos_alcanzados = [h for h in objetivo.hitos if h['alcanzado']]
        if hitos_alcanzados:
            lbl_hitos = ctk.CTkLabel(card, text=
                f'✨ Hitos alcanzados: {len(hitos_alcanzados)}/{len(objetivo.hitos)}'
                , font=ctk.CTkFont(size=11))
            lbl_hitos.pack(pady=5, padx=15, anchor='w')
        if objetivo.completado:
            lbl_completado = ctk.CTkLabel(card, text=
                '✅ ¡OBJETIVO COMPLETADO!', font=ctk.CTkFont(size=13, weight
                ='bold'), text_color='green')
            lbl_completado.pack(pady=10)

    def _mostrar_dialogo_nuevo_objetivo(self):
        dialogo = ctk.CTkToplevel(self)
        dialogo.title('Nuevo Objetivo')
        dialogo.geometry('500x600')
        lbl_titulo = ctk.CTkLabel(dialogo, text='🎯 Crear Nuevo Objetivo',
            font=ctk.CTkFont(size=20, weight='bold'))
        lbl_titulo.pack(pady=20)
        frame = ctk.CTkFrame(dialogo)
        frame.pack(fill='both', expand=True, padx=20, pady=10)
        lbl_nombre = ctk.CTkLabel(frame, text='Nombre del Objetivo:')
        lbl_nombre.pack(pady=(10, 5))
        entry_nombre = ctk.CTkEntry(frame, placeholder_text='Ej: Perder 10kg')
        entry_nombre.pack(pady=5)
        lbl_tipo = ctk.CTkLabel(frame, text='Tipo:')
        lbl_tipo.pack(pady=(15, 5))
        combo_tipo = ctk.CTkComboBox(frame, values=['peso', 'fuerza',
            'resistencia', 'flexibilidad'])
        combo_tipo.pack(pady=5)
        lbl_objetivo = ctk.CTkLabel(frame, text='Valor Objetivo:')
        lbl_objetivo.pack(pady=(15, 5))
        entry_objetivo = ctk.CTkEntry(frame, placeholder_text='Ej: 70')
        entry_objetivo.pack(pady=5)
        lbl_unidad = ctk.CTkLabel(frame, text='Unidad:')
        lbl_unidad.pack(pady=(15, 5))
        entry_unidad = ctk.CTkEntry(frame, placeholder_text='Ej: kg')
        entry_unidad.pack(pady=5)
        lbl_desc = ctk.CTkLabel(frame, text='Descripción (opcional):')
        lbl_desc.pack(pady=(15, 5))
        textbox_desc = ctk.CTkTextbox(frame, height=80)
        textbox_desc.pack(fill='x', padx=10, pady=5)

        def crear():
            try:
                nombre = entry_nombre.get()
                tipo = combo_tipo.get()
                valor_objetivo = float(entry_objetivo.get())
                unidad = entry_unidad.get()
                descripcion = textbox_desc.get('1.0', 'end-1c')
                gestor_funcionalidades.crear_objetivo(self.user_id, nombre,
                    descripcion, tipo, valor_objetivo, unidad)
                dialogo.destroy()
                self._cargar_objetivos()
            except ValueError:
                lbl_error = ctk.CTkLabel(dialogo, text=
                    '❌ Error: Valores inválidos', text_color='red')
                lbl_error.pack(pady=10)
        btn_crear = ctk.CTkButton(dialogo, text='✨ Crear Objetivo', command
            =crear, font=ctk.CTkFont(size=14, weight='bold'))
        btn_crear.pack(pady=20)

    def _crear_tab_logros(self):
        tab = self.tabview.tab('Logros')
        lbl_titulo = ctk.CTkLabel(tab, text='🏆 Mis Logros', font=ctk.
            CTkFont(size=20, weight='bold'))
        lbl_titulo.pack(pady=20)
        self.frame_logros = ctk.CTkScrollableFrame(tab, height=500)
        self.frame_logros.pack(fill='both', expand=True, padx=10, pady=10)
        self._cargar_logros()

    def _cargar_logros(self):
        for widget in self.frame_logros.winfo_children():
            widget.destroy()
        logros = gestor_funcionalidades.obtener_logros(self.user_id)
        if not logros:
            lbl_vacio = ctk.CTkLabel(self.frame_logros, text=
                """No has obtenido logros aún.
¡Sigue entrenando para desbloquearlos!"""
                , font=ctk.CTkFont(size=16))
            lbl_vacio.pack(pady=50)
            return
        por_categoria = {}
        for logro in logros:
            if logro.categoria not in por_categoria:
                por_categoria[logro.categoria] = []
            por_categoria[logro.categoria].append(logro)
        for categoria, logros_cat in por_categoria.items():
            self._crear_seccion_categoria(categoria, logros_cat)

    def _crear_seccion_categoria(self, categoria: str, logros: List[Logro]):
        cat_frame = ctk.CTkFrame(self.frame_logros, corner_radius=10)
        cat_frame.pack(fill='x', padx=10, pady=15)
        lbl_cat = ctk.CTkLabel(cat_frame, text=f'📂 {categoria.upper()}',
            font=ctk.CTkFont(size=14, weight='bold'))
        lbl_cat.pack(pady=10, anchor='w', padx=15)
        grid_frame = ctk.CTkFrame(cat_frame)
        grid_frame.pack(fill='both', expand=True, padx=10, pady=10)
        for i, logro in enumerate(logros):
            row = i // 3
            col = i % 3
            self._crear_badge_logro(grid_frame, logro, row, col)

    def _crear_badge_logro(self, parent, logro: Logro, row: int, col: int):
        badge = ctk.CTkFrame(parent, corner_radius=8, width=140, height=140)
        badge.grid(row=row, column=col, padx=5, pady=5)
        badge.grid_propagate(False)
        lbl_icono = ctk.CTkLabel(badge, text=logro.icono, font=ctk.CTkFont(
            size=40))
        lbl_icono.pack(pady=(15, 5))
        lbl_nombre = ctk.CTkLabel(badge, text=logro.nombre, font=ctk.
            CTkFont(size=11, weight='bold'), wraplength=120)
        lbl_nombre.pack(pady=5)
        if logro.nivel > 1:
            lbl_nivel = ctk.CTkLabel(badge, text=f'Nivel {logro.nivel}',
                font=ctk.CTkFont(size=9), text_color='gold')
            lbl_nivel.pack(pady=2)

    def _crear_tab_analisis(self):
        tab = self.tabview.tab('Análisis')
        lbl_titulo = ctk.CTkLabel(tab, text='📈 Análisis de Rendimiento',
            font=ctk.CTkFont(size=20, weight='bold'))
        lbl_titulo.pack(pady=20)
        periodo_frame = ctk.CTkFrame(tab)
        periodo_frame.pack(pady=10)
        lbl_periodo = ctk.CTkLabel(periodo_frame, text='Período:', font=ctk
            .CTkFont(size=12))
        lbl_periodo.pack(side='left', padx=5)
        combo_periodo = ctk.CTkComboBox(periodo_frame, values=['7 días',
            '30 días', '90 días', '1 año'], command=lambda v: self.
            _actualizar_analisis(v))
        combo_periodo.pack(side='left', padx=5)
        combo_periodo.set('30 días')
        self.frame_analisis = ctk.CTkScrollableFrame(tab, height=400)
        self.frame_analisis.pack(fill='both', expand=True, padx=20, pady=10)
        self._actualizar_analisis('30 días')

    def _actualizar_analisis(self, periodo: str):
        for widget in self.frame_analisis.winfo_children():
            widget.destroy()
        dias = {'7 días': 7, '30 días': 30, '90 días': 90, '1 año': 365}.get(
            periodo, 30)
        analisis = gestor_funcionalidades.obtener_analisis_rendimiento(self
            .user_id, dias=dias)
        if not analisis['ejercicios']:
            lbl_vacio = ctk.CTkLabel(self.frame_analisis, text=
                'No hay datos de entrenamiento en este período.', font=ctk.
                CTkFont(size=14))
            lbl_vacio.pack(pady=50)
            return
        lbl_ejercicios = ctk.CTkLabel(self.frame_analisis, text=
            '💪 Ejercicios', font=ctk.CTkFont(size=16, weight='bold'))
        lbl_ejercicios.pack(pady=10, anchor='w')
        for ejercicio, datos in analisis['ejercicios'].items():
            self._crear_tarjeta_ejercicio(ejercicio, datos)
        if analisis['recuperacion']['calidad_sueno_promedio']:
            lbl_recuperacion = ctk.CTkLabel(self.frame_analisis, text=
                '😴 Recuperación', font=ctk.CTkFont(size=16, weight='bold'))
            lbl_recuperacion.pack(pady=(20, 10), anchor='w')
            self._crear_tarjeta_recuperacion(analisis['recuperacion'])

    def _crear_tarjeta_ejercicio(self, nombre: str, datos: dict):
        card = ctk.CTkFrame(self.frame_analisis, corner_radius=8)
        card.pack(fill='x', pady=5)
        lbl_nombre = ctk.CTkLabel(card, text=f'🏋️ {nombre}', font=ctk.
            CTkFont(size=14, weight='bold'))
        lbl_nombre.pack(pady=10, anchor='w', padx=15)
        info_grid = ctk.CTkFrame(card)
        info_grid.pack(fill='x', padx=15, pady=5)
        metricas = [('Peso Promedio', f"{datos['peso_promedio']:.1f} kg"),
            ('Reps Promedio', f"{datos['reps_promedio']:.0f}"), (
            'Total Sesiones', f"{datos['total_sesiones']}")]
        for i, (label, value) in enumerate(metricas):
            lbl = ctk.CTkLabel(info_grid, text=label + ':')
            lbl.grid(row=i, column=0, padx=5, pady=3, sticky='w')
            val = ctk.CTkLabel(info_grid, text=value, font=ctk.CTkFont(
                weight='bold'))
            val.grid(row=i, column=1, padx=5, pady=3, sticky='w')
        card.pack(fill='x', pady=5, padx=10)

    def _crear_tarjeta_recuperacion(self, datos: dict):
        card = ctk.CTkFrame(self.frame_analisis, corner_radius=8)
        card.pack(fill='x', pady=5, padx=10)
        metricas = [('Calidad Sueño',
            f"{datos['calidad_sueno_promedio']:.1f}/10"), ('Horas Sueño',
            f"{datos['horas_sueno_promedio']:.1f} hrs"), ('Nivel Estrés',
            f"{datos['nivel_estres_promedio']:.1f}/10")]
        info_grid = ctk.CTkFrame(card)
        info_grid.pack(fill='both', expand=True, padx=15, pady=15)
        for i, (label, value) in enumerate(metricas):
            lbl = ctk.CTkLabel(info_grid, text=label + ':')
            lbl.grid(row=i, column=0, padx=5, pady=5, sticky='w')
            val = ctk.CTkLabel(info_grid, text=value, font=ctk.CTkFont(
                weight='bold'))
            val.grid(row=i, column=1, padx=5, pady=5, sticky='w')

