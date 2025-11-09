# -*- coding: utf-8 -*-
"""
Módulo de Funcionalidades Avanzadas
Implementa características profesionales complejas del SUGERENCIAS_MEJORA.md
"""

import json
import sqlite3
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
import threading
import queue


@dataclass
class ProgressPhoto:
    """Foto de progreso con metadatos."""
    id: int
    user_id: int
    fecha: str
    imagen_base64: str
    peso_kg: float
    notas: str
    medidas: Dict[str, float]  # cintura, pecho, caderas, brazos, piernas


@dataclass
class Objetivo:
    """Objetivo de entrenamiento con seguimiento."""
    id: int
    user_id: int
    nombre: str
    descripcion: str
    tipo: str  # peso, fuerza, resistencia, flexibilidad
    valor_actual: float
    valor_objetivo: float
    unidad: str
    fecha_inicio: str
    fecha_objetivo: str
    progreso_pct: float
    completado: bool
    hitos: List[Dict]


@dataclass
class Logro:
    """Sistema de logros y badges."""
    id: int
    user_id: int
    nombre: str
    descripcion: str
    icono: str
    categoria: str  # consistencia, fuerza, resistencia, general
    fecha_obtenido: str
    nivel: int


@dataclass
class MensajeEnriquecido:
    """Mensaje con soporte multimedia."""
    id: int
    remitente_id: int
    destinatario_id: int
    tipo: str  # texto, voz, video, imagen, documento
    contenido: str
    archivo_base64: Optional[str]
    nombre_archivo: Optional[str]
    leido: bool
    fecha: str


class GestorFuncionalidadesAvanzadas:
    """Gestor de funcionalidades avanzadas del sistema."""
    
    def __init__(self, db_path: str = "data/gym_database.db"):
        self.db_path = db_path
        self._inicializar_tablas()
        
        # Cola de procesamiento asíncrono
        self.processing_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._procesar_cola, daemon=True)
        self.worker_thread.start()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Obtiene conexión a base de datos."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _inicializar_tablas(self):
        """Crea tablas para funcionalidades avanzadas."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Tabla de fotos de progreso
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fotos_progreso (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                imagen_base64 TEXT NOT NULL,
                peso_kg REAL,
                notas TEXT,
                medidas_json TEXT,
                FOREIGN KEY (user_id) REFERENCES usuarios(id)
            )
        """)
        
        # Tabla de objetivos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS objetivos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                tipo TEXT NOT NULL,
                valor_actual REAL,
                valor_objetivo REAL NOT NULL,
                unidad TEXT NOT NULL,
                fecha_inicio TEXT NOT NULL,
                fecha_objetivo TEXT,
                progreso_pct REAL DEFAULT 0,
                completado INTEGER DEFAULT 0,
                hitos_json TEXT,
                FOREIGN KEY (user_id) REFERENCES usuarios(id)
            )
        """)
        
        # Tabla de logros
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                icono TEXT,
                categoria TEXT,
                fecha_obtenido TEXT NOT NULL,
                nivel INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES usuarios(id)
            )
        """)
        
        # Tabla de mensajes enriquecidos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mensajes_enriquecidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                remitente_id INTEGER NOT NULL,
                destinatario_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                contenido TEXT,
                archivo_base64 TEXT,
                nombre_archivo TEXT,
                leido INTEGER DEFAULT 0,
                fecha TEXT NOT NULL,
                FOREIGN KEY (remitente_id) REFERENCES usuarios(id),
                FOREIGN KEY (destinatario_id) REFERENCES usuarios(id)
            )
        """)
        
        # Tabla de análisis de rendimiento
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analisis_rendimiento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                tipo_ejercicio TEXT NOT NULL,
                repeticiones INTEGER,
                peso_kg REAL,
                duracion_seg INTEGER,
                frecuencia_cardiaca_promedio INTEGER,
                calorias_quemadas REAL,
                calidad_forma INTEGER,
                notas TEXT,
                FOREIGN KEY (user_id) REFERENCES usuarios(id)
            )
        """)
        
        # Tabla de métricas de recuperación
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metricas_recuperacion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                calidad_sueno INTEGER,
                horas_sueno REAL,
                nivel_estres INTEGER,
                dolor_muscular INTEGER,
                frecuencia_cardiaca_reposo INTEGER,
                variabilidad_fc INTEGER,
                hidratacion_ml INTEGER,
                FOREIGN KEY (user_id) REFERENCES usuarios(id)
            )
        """)
        
        # Índices para rendimiento
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_fotos_user ON fotos_progreso(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_objetivos_user ON objetivos(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_logros_user ON logros(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mensajes_dest ON mensajes_enriquecidos(destinatario_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analisis_user ON analisis_rendimiento(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_recuperacion_user ON metricas_recuperacion(user_id)")
        
        conn.commit()
        conn.close()
    
    # ==================== FOTOS DE PROGRESO ====================
    
    def agregar_foto_progreso(self, user_id: int, imagen_path: str, 
                              peso_kg: float, notas: str = "",
                              medidas: Optional[Dict[str, float]] = None) -> int:
        """Agrega una foto de progreso con metadatos."""
        # Leer y codificar imagen
        with open(imagen_path, 'rb') as f:
            imagen_bytes = f.read()
            imagen_base64 = base64.b64encode(imagen_bytes).decode('utf-8')
        
        medidas = medidas or {}
        medidas_json = json.dumps(medidas)
        fecha = datetime.now().isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO fotos_progreso 
            (user_id, fecha, imagen_base64, peso_kg, notas, medidas_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, fecha, imagen_base64, peso_kg, notas, medidas_json))
        
        foto_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Verificar logros automáticamente
        self._verificar_logros_progreso(user_id)
        
        return foto_id
    
    def obtener_linea_tiempo_progreso(self, user_id: int, 
                                       limite: int = 50) -> List[ProgressPhoto]:
        """Obtiene línea de tiempo de fotos de progreso."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM fotos_progreso
            WHERE user_id = ?
            ORDER BY fecha DESC
            LIMIT ?
        """, (user_id, limite))
        
        fotos = []
        for row in cursor.fetchall():
            medidas = json.loads(row['medidas_json']) if row['medidas_json'] else {}
            foto = ProgressPhoto(
                id=row['id'],
                user_id=row['user_id'],
                fecha=row['fecha'],
                imagen_base64=row['imagen_base64'],
                peso_kg=row['peso_kg'],
                notas=row['notas'],
                medidas=medidas
            )
            fotos.append(foto)
        
        conn.close()
        return fotos
    
    def comparar_fotos_progreso(self, user_id: int, 
                                foto1_id: int, foto2_id: int) -> Dict:
        """Compara dos fotos de progreso y genera análisis."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM fotos_progreso WHERE id = ?", (foto1_id,))
        foto1 = cursor.fetchone()
        
        cursor.execute("SELECT * FROM fotos_progreso WHERE id = ?", (foto2_id,))
        foto2 = cursor.fetchone()
        
        conn.close()
        
        if not foto1 or not foto2:
            return {}
        
        medidas1 = json.loads(foto1['medidas_json']) if foto1['medidas_json'] else {}
        medidas2 = json.loads(foto2['medidas_json']) if foto2['medidas_json'] else {}
        
        cambios = {
            'peso_kg': foto2['peso_kg'] - foto1['peso_kg'],
            'dias_transcurridos': (datetime.fromisoformat(foto2['fecha']) - 
                                  datetime.fromisoformat(foto1['fecha'])).days,
            'cambios_medidas': {}
        }
        
        for medida in set(medidas1.keys()) | set(medidas2.keys()):
            val1 = medidas1.get(medida, 0)
            val2 = medidas2.get(medida, 0)
            cambios['cambios_medidas'][medida] = val2 - val1
        
        return cambios
    
    # ==================== OBJETIVOS Y HITOS ====================
    
    def crear_objetivo(self, user_id: int, nombre: str, descripcion: str,
                       tipo: str, valor_objetivo: float, unidad: str,
                       fecha_objetivo: Optional[str] = None,
                       valor_actual: float = 0) -> int:
        """Crea un nuevo objetivo de entrenamiento."""
        fecha_inicio = datetime.now().isoformat()
        hitos = []
        
        # Generar hitos automáticos (25%, 50%, 75%, 100%)
        for pct in [25, 50, 75, 100]:
            hitos.append({
                'porcentaje': pct,
                'valor': valor_actual + (valor_objetivo - valor_actual) * (pct / 100),
                'alcanzado': False,
                'fecha_alcanzado': None
            })
        
        hitos_json = json.dumps(hitos)
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO objetivos
            (user_id, nombre, descripcion, tipo, valor_actual, valor_objetivo,
             unidad, fecha_inicio, fecha_objetivo, hitos_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, nombre, descripcion, tipo, valor_actual, valor_objetivo,
              unidad, fecha_inicio, fecha_objetivo, hitos_json))
        
        objetivo_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return objetivo_id
    
    def actualizar_progreso_objetivo(self, objetivo_id: int, 
                                     nuevo_valor: float) -> Dict:
        """Actualiza el progreso de un objetivo."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM objetivos WHERE id = ?", (objetivo_id,))
        objetivo = cursor.fetchone()
        
        if not objetivo:
            conn.close()
            return {}
        
        valor_objetivo = objetivo['valor_objetivo']
        valor_inicial = 0  # Asumir que empieza desde 0
        progreso_pct = min(100, (nuevo_valor / valor_objetivo) * 100)
        completado = progreso_pct >= 100
        
        # Actualizar hitos
        hitos = json.loads(objetivo['hitos_json']) if objetivo['hitos_json'] else []
        for hito in hitos:
            if not hito['alcanzado'] and nuevo_valor >= hito['valor']:
                hito['alcanzado'] = True
                hito['fecha_alcanzado'] = datetime.now().isoformat()
        
        hitos_json = json.dumps(hitos)
        
        cursor.execute("""
            UPDATE objetivos
            SET valor_actual = ?, progreso_pct = ?, completado = ?, hitos_json = ?
            WHERE id = ?
        """, (nuevo_valor, progreso_pct, completado, hitos_json, objetivo_id))
        
        conn.commit()
        conn.close()
        
        # Si se completó, otorgar logro
        if completado:
            self._otorgar_logro_objetivo(objetivo['user_id'], objetivo['tipo'])
        
        return {
            'progreso_pct': progreso_pct,
            'completado': completado,
            'hitos_alcanzados': [h for h in hitos if h['alcanzado']]
        }
    
    def obtener_objetivos(self, user_id: int, 
                         incluir_completados: bool = False) -> List[Objetivo]:
        """Obtiene objetivos del usuario."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM objetivos WHERE user_id = ?"
        if not incluir_completados:
            query += " AND completado = 0"
        query += " ORDER BY fecha_inicio DESC"
        
        cursor.execute(query, (user_id,))
        
        objetivos = []
        for row in cursor.fetchall():
            hitos = json.loads(row['hitos_json']) if row['hitos_json'] else []
            objetivo = Objetivo(
                id=row['id'],
                user_id=row['user_id'],
                nombre=row['nombre'],
                descripcion=row['descripcion'],
                tipo=row['tipo'],
                valor_actual=row['valor_actual'],
                valor_objetivo=row['valor_objetivo'],
                unidad=row['unidad'],
                fecha_inicio=row['fecha_inicio'],
                fecha_objetivo=row['fecha_objetivo'],
                progreso_pct=row['progreso_pct'],
                completado=bool(row['completado']),
                hitos=hitos
            )
            objetivos.append(objetivo)
        
        conn.close()
        return objetivos
    
    # ==================== SISTEMA DE LOGROS ====================
    
    def _otorgar_logro(self, user_id: int, nombre: str, descripcion: str,
                       categoria: str, icono: str = "🏆", nivel: int = 1):
        """Otorga un logro al usuario."""
        # Verificar si ya tiene el logro
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM logros
            WHERE user_id = ? AND nombre = ?
        """, (user_id, nombre))
        
        if cursor.fetchone():
            conn.close()
            return  # Ya tiene el logro
        
        fecha = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO logros
            (user_id, nombre, descripcion, icono, categoria, fecha_obtenido, nivel)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, nombre, descripcion, icono, categoria, fecha, nivel))
        
        conn.commit()
        conn.close()
    
    def _verificar_logros_progreso(self, user_id: int):
        """Verifica y otorga logros automáticamente basados en progreso."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Contar fotos de progreso
        cursor.execute("SELECT COUNT(*) as total FROM fotos_progreso WHERE user_id = ?", 
                      (user_id,))
        total_fotos = cursor.fetchone()['total']
        
        if total_fotos >= 1:
            self._otorgar_logro(user_id, "Primera Foto", 
                              "Has registrado tu primera foto de progreso",
                              "progreso", "📸")
        if total_fotos >= 10:
            self._otorgar_logro(user_id, "Documentador Dedicado",
                              "Has registrado 10 fotos de progreso",
                              "progreso", "📷", 2)
        if total_fotos >= 50:
            self._otorgar_logro(user_id, "Maestro del Progreso",
                              "Has registrado 50 fotos de progreso",
                              "progreso", "🎥", 3)
        
        conn.close()
    
    def _otorgar_logro_objetivo(self, user_id: int, tipo_objetivo: str):
        """Otorga logro por completar objetivo."""
        nombre = f"Objetivo de {tipo_objetivo.capitalize()} Alcanzado"
        descripcion = f"Has completado un objetivo de {tipo_objetivo}"
        self._otorgar_logro(user_id, nombre, descripcion, "objetivos", "🎯")
    
    def obtener_logros(self, user_id: int) -> List[Logro]:
        """Obtiene todos los logros del usuario."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM logros
            WHERE user_id = ?
            ORDER BY fecha_obtenido DESC
        """, (user_id,))
        
        logros = []
        for row in cursor.fetchall():
            logro = Logro(
                id=row['id'],
                user_id=row['user_id'],
                nombre=row['nombre'],
                descripcion=row['descripcion'],
                icono=row['icono'],
                categoria=row['categoria'],
                fecha_obtenido=row['fecha_obtenido'],
                nivel=row['nivel']
            )
            logros.append(logro)
        
        conn.close()
        return logros
    
    # ==================== MENSAJERÍA ENRIQUECIDA ====================
    
    def enviar_mensaje_enriquecido(self, remitente_id: int, destinatario_id: int,
                                   tipo: str, contenido: str,
                                   archivo_path: Optional[str] = None) -> int:
        """Envía mensaje con soporte multimedia."""
        archivo_base64 = None
        nombre_archivo = None
        
        if archivo_path and Path(archivo_path).exists():
            with open(archivo_path, 'rb') as f:
                archivo_bytes = f.read()
                archivo_base64 = base64.b64encode(archivo_bytes).decode('utf-8')
                nombre_archivo = Path(archivo_path).name
        
        fecha = datetime.now().isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO mensajes_enriquecidos
            (remitente_id, destinatario_id, tipo, contenido, archivo_base64, 
             nombre_archivo, fecha)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (remitente_id, destinatario_id, tipo, contenido, archivo_base64,
              nombre_archivo, fecha))
        
        mensaje_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return mensaje_id
    
    def obtener_mensajes_enriquecidos(self, user_id: int, 
                                      limite: int = 50) -> List[MensajeEnriquecido]:
        """Obtiene mensajes enriquecidos para un usuario."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM mensajes_enriquecidos
            WHERE destinatario_id = ? OR remitente_id = ?
            ORDER BY fecha DESC
            LIMIT ?
        """, (user_id, user_id, limite))
        
        mensajes = []
        for row in cursor.fetchall():
            mensaje = MensajeEnriquecido(
                id=row['id'],
                remitente_id=row['remitente_id'],
                destinatario_id=row['destinatario_id'],
                tipo=row['tipo'],
                contenido=row['contenido'],
                archivo_base64=row['archivo_base64'],
                nombre_archivo=row['nombre_archivo'],
                leido=bool(row['leido']),
                fecha=row['fecha']
            )
            mensajes.append(mensaje)
        
        conn.close()
        return mensajes
    
    # ==================== ANÁLISIS Y MÉTRICAS ====================
    
    def registrar_sesion_entrenamiento(self, user_id: int, tipo_ejercicio: str,
                                      repeticiones: int, peso_kg: float,
                                      duracion_seg: int, **kwargs):
        """Registra una sesión de entrenamiento con métricas."""
        fecha = datetime.now().isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO analisis_rendimiento
            (user_id, fecha, tipo_ejercicio, repeticiones, peso_kg, duracion_seg,
             frecuencia_cardiaca_promedio, calorias_quemadas, calidad_forma, notas)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, fecha, tipo_ejercicio, repeticiones, peso_kg, duracion_seg,
              kwargs.get('frecuencia_cardiaca', None),
              kwargs.get('calorias', None),
              kwargs.get('calidad_forma', None),
              kwargs.get('notas', '')))
        
        conn.commit()
        conn.close()
    
    def registrar_metricas_recuperacion(self, user_id: int, calidad_sueno: int,
                                       horas_sueno: float, nivel_estres: int,
                                       **kwargs):
        """Registra métricas de recuperación."""
        fecha = datetime.now().isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO metricas_recuperacion
            (user_id, fecha, calidad_sueno, horas_sueno, nivel_estres,
             dolor_muscular, frecuencia_cardiaca_reposo, variabilidad_fc, hidratacion_ml)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, fecha, calidad_sueno, horas_sueno, nivel_estres,
              kwargs.get('dolor_muscular', None),
              kwargs.get('fc_reposo', None),
              kwargs.get('variabilidad_fc', None),
              kwargs.get('hidratacion_ml', None)))
        
        conn.commit()
        conn.close()
    
    def obtener_analisis_rendimiento(self, user_id: int, 
                                     dias: int = 30) -> Dict:
        """Genera análisis de rendimiento del usuario."""
        fecha_inicio = (datetime.now() - timedelta(days=dias)).isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Obtener datos de entrenamiento
        cursor.execute("""
            SELECT tipo_ejercicio, AVG(peso_kg) as peso_promedio,
                   AVG(repeticiones) as reps_promedio,
                   COUNT(*) as total_sesiones
            FROM analisis_rendimiento
            WHERE user_id = ? AND fecha >= ?
            GROUP BY tipo_ejercicio
        """, (user_id, fecha_inicio))
        
        ejercicios = {}
        for row in cursor.fetchall():
            ejercicios[row['tipo_ejercicio']] = {
                'peso_promedio': row['peso_promedio'],
                'reps_promedio': row['reps_promedio'],
                'total_sesiones': row['total_sesiones']
            }
        
        # Obtener métricas de recuperación
        cursor.execute("""
            SELECT AVG(calidad_sueno) as sueno_promedio,
                   AVG(horas_sueno) as horas_promedio,
                   AVG(nivel_estres) as estres_promedio
            FROM metricas_recuperacion
            WHERE user_id = ? AND fecha >= ?
        """, (user_id, fecha_inicio))
        
        recuperacion = cursor.fetchone()
        
        conn.close()
        
        return {
            'periodo_dias': dias,
            'ejercicios': ejercicios,
            'recuperacion': {
                'calidad_sueno_promedio': recuperacion['sueno_promedio'],
                'horas_sueno_promedio': recuperacion['horas_promedio'],
                'nivel_estres_promedio': recuperacion['estres_promedio']
            }
        }
    
    def _procesar_cola(self):
        """Procesa tareas asíncronas en la cola."""
        while True:
            try:
                task = self.processing_queue.get(timeout=1)
                # Procesar tarea
                task()
                self.processing_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error procesando tarea: {e}")


# Instancia global
gestor_funcionalidades = GestorFuncionalidadesAvanzadas()
