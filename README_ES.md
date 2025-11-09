# Sistema de Gestión de Gimnasios

Un sistema integral de gestión de gimnasios con arquitectura padre-hijo para administración profesional de gimnasios y participación de miembros.

## ⚡ NUEVO: Resiliencia de Red Mejorada (v3.2.0)

**Actualización Mayor:** El sistema ahora incluye características de resiliencia de red de nivel empresarial:
- ✅ **Cola de Operación Sin Conexión** - Trabaje sin conexión, sincronización automática al reconectar
- ✅ **Monitoreo de Salud de Red** - Seguimiento de calidad de conexión en tiempo real
- ✅ **Tiempos de Espera Adaptativos** - Se ajusta automáticamente a las condiciones de red
- ✅ **Detección de Cortafuegos** - Diagnostica y guía a través de problemas de red
- ✅ **Fallback Automático** - Múltiples estrategias de reintento con retroceso exponencial
- ✅ **Diagnósticos de Conexión** - Herramientas de solución de problemas integradas

Consulte [GUIA_SOLUCION_PROBLEMAS_RED.md](GUIA_SOLUCION_PROBLEMAS_RED.md) para una guía detallada de configuración y solución de problemas.

## 🏋️ Descripción General

Este proyecto implementa una solución completa de gestión de gimnasios diseñada para gimnasios exclusivos y centros de fitness. El sistema consta de:

### 🏢 Aplicación Padre (Administración del Gimnasio)
La aplicación administrativa utilizada por el personal del gimnasio y entrenadores para gestionar toda la operación del gimnasio:
- **Gestión de Miembros**: Base de datos completa de miembros del gimnasio con información personal, evaluaciones y seguimiento de progreso
- **Creación de Programas de Entrenamiento**: Diseñar y asignar rutinas de ejercicios personalizadas y programas de entrenamiento
- **Gestión de Horarios**: Control de clases, sesiones y disponibilidad de entrenadores
- **Administración de Negocio**: Gestión de membresías, seguimiento de pagos e informes financieros
- **Centro de Comunicación**: Mensajería directa con miembros y anuncios grupales
- **Servidor API REST**: Backend basado en FastAPI para sincronización en tiempo real con aplicaciones de miembros

**Componentes Principales:**
- `madre_db.py` - Gestión de base de datos SQLite
- `madre_server.py` - Servidor API REST
- `madre_gui.py` - Interfaz GUI administrativa
- `madre_main.py` - Punto de entrada de la aplicación

### 📱 Aplicación Hija (Miembros del Gimnasio)
La aplicación orientada a miembros que proporciona a los clientes del gimnasio acceso a su información de entrenamiento personalizada:
- **Planes de Entrenamiento Personalizados**: Acceso a rutinas de ejercicios asignadas con videos e instrucciones
- **Seguimiento de Progreso**: Registrar entrenamientos, medidas corporales y ver progreso a lo largo del tiempo
- **Comunicación Directa**: Mensajería en tiempo real con entrenadores y personal del gimnasio
- **Reserva de Sesiones**: Reservar sesiones de entrenamiento y clases
- **Planes de Nutrición**: Acceso a planes de comidas personalizados y orientación nutricional

**Componentes Principales:**
- `hija_comms.py` - Módulo de comunicación API
- `hija_views.py` - Interfaz GUI de miembros
- `hija_main.py` - Punto de entrada de la aplicación

## 🚀 Inicio Rápido

### Requisitos Previos
- Python 3.8 o superior
- Windows, Linux o macOS
- Conexión de red entre dispositivos de administración y miembros del gimnasio

### Instalación

1. **Clonar el repositorio**
```bash
git clone <url-repositorio>
cd PERSONAL-TRIAN
```

2. **Instalar dependencias**

Para la Aplicación de Administración:
```bash
pip install -r requirements_madre.txt
```

Para la Aplicación de Miembros:
```bash
pip install -r requirements_hija.txt
```

3. **Inicializar la base de datos** (solo primera vez)
```bash
python populate_db.py
```

### Ejecutar las Aplicaciones

#### Iniciar la Aplicación de Administración (Personal del Gimnasio)

```bash
python madre_main.py
```

La interfaz de administración se abrirá con:
- Panel de gestión de miembros
- Herramientas de creación de programas de entrenamiento
- Controles de sincronización de contenido
- El servidor API iniciará en `http://0.0.0.0:8000`

#### Iniciar la Aplicación de Miembros

1. Configurar la URL del servidor del gimnasio (si no se ejecuta en la misma máquina):
```bash
# Crear archivo .env
echo "MADRE_BASE_URL=http://192.168.1.100:8000" > .env
```

2. Iniciar la aplicación:
```bash
python hija_main.py
```

3. Iniciar sesión con credenciales de miembro:
   - Miembros predeterminados: `juan_perez`, `maria_lopez` (contraseña: `gym2024`, `fit2024`)
   - Usar el botón de sincronización para descargar sus datos de entrenamiento del servidor del gimnasio

## 📋 Usuarios Predeterminados

El sistema incluye usuarios de demostración con perfiles completos:

| Nombre de Usuario | Contraseña | Acceso | Equipo/Nivel |
|-------------------|-----------|--------|--------------|
| `juan_perez` | `gym2024` | ✅ Habilitado | Fitness Avanzado |
| `maria_lopez` | `fit2024` | ✅ Habilitado | Cardio y Resistencia |
| `carlos_rodriguez` | `trainer123` | ❌ Bloqueado | Principiantes |

Cada usuario incluye:
- Foto de perfil
- Información personal completa (correo electrónico, teléfono, asignación de equipo)
- Horario de entrenamiento mensual
- Galería de fotos personales
- Datos de progreso de entrenamiento

## 🔒 Seguridad

### Características de Seguridad Actuales
- ✅ Hash de contraseñas con SHA256
- ✅ Base de datos SQLite persistente con seguridad de hilos
- ✅ Validación de permisos en el servidor
- ✅ Validación de sincronización de 72 horas para asegurar membresía activa
- ✅ Almacenamiento seguro de credenciales
- ✅ **NUEVO: Limitación de tasa** - Protección contra abuso (60 sol/min por cliente)
- ✅ **NUEVO: Circuit breaker** - Protección contra fallos en cascada
- ✅ **NUEVO: Temporización de solicitudes** - Monitoreo de rendimiento y alertas

## 📦 Distribución

### Crear Ejecutables de Windows

Para distribuir aplicaciones de miembros sin requerir instalación de Python:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed hija_main.py
```

El ejecutable estará en la carpeta `dist/`.

## 📄 Licencia

Este proyecto es un sistema de demostración y prototipo educativo para gestión de gimnasios.
