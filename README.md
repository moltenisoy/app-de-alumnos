# Gym Management System

A comprehensive gym management system with parent-child architecture for professional gym administration and member engagement.

## ⚡ NEW: Enhanced Network Resilience (v3.2.0)

**Major Update:** The system now includes enterprise-grade network resilience features:
- ✅ **Offline Operation Queue** - Work offline, sync automatically when reconnected
- ✅ **Network Health Monitoring** - Real-time connection quality tracking
- ✅ **Adaptive Timeouts** - Automatically adjusts to network conditions
- ✅ **Firewall Detection** - Diagnoses and guides through network issues
- ✅ **Automatic Fallback** - Multiple retry strategies with exponential backoff
- ✅ **Connection Diagnostics** - Built-in troubleshooting tools

See [NETWORK_TROUBLESHOOTING.md](NETWORK_TROUBLESHOOTING.md) for detailed configuration and troubleshooting guide.

## 🏋️ Overview

This project implements a complete gym management solution designed for exclusive gyms and fitness centers. The system consists of:

### 🏢 Parent Application (Gym Administration)
The administrative application used by gym staff and trainers to manage the entire gym operation:
- **Member Management**: Complete database of gym members with personal information, evaluations, and progress tracking
- **Training Program Creation**: Design and assign personalized workout routines and training programs
- **Schedule Management**: Control of classes, sessions, and trainer availability
- **Business Administration**: Membership management, payment tracking, and financial reporting
- **Communication Hub**: Direct messaging with members and group announcements
- **REST API Server**: FastAPI-based backend for real-time synchronization with member apps

**Core Components:**
- `madre_db.py` - SQLite database management
- `madre_server.py` - REST API server
- `madre_gui.py` - Administrative GUI interface
- `madre_main.py` - Application entry point

### 📱 Child Application (Gym Members)
The member-facing application that provides gym clients with access to their personalized training information:
- **Personalized Training Plans**: Access to assigned workout routines with exercise videos and instructions
- **Progress Tracking**: Record workouts, body measurements, and view progress over time
- **Direct Communication**: Real-time messaging with trainers and gym staff
- **Session Booking**: Reserve training sessions and classes
- **Nutrition Plans**: Access to personalized meal plans and nutritional guidance

**Core Components:**
- `hija_comms.py` - API communication module
- `hija_views.py` - Member GUI interface
- `hija_main.py` - Application entry point

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Windows, Linux, or macOS
- Network connection between gym admin and member devices

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd PERSONAL-TRIAN
```

2. **Install dependencies**

For the Admin Application:
```bash
pip install -r requirements_madre.txt
```

For the Member Application:
```bash
pip install -r requirements_hija.txt
```

3. **Initialize the database** (first time only)
```bash
python populate_db.py
```

### Running the Applications

#### Start the Admin Application (Gym Staff)

```bash
python madre_main.py
```

The admin interface will open with:
- Member management dashboard
- Training program creation tools
- Content synchronization controls
- The API server will start on `http://0.0.0.0:8000`

#### Start the Member Application

1. Configure the gym server URL (if not running on the same machine):
```bash
# Create .env file
echo "MADRE_BASE_URL=http://192.168.1.100:8000" > .env
```

2. Launch the application:
```bash
python hija_main.py
```

3. Log in with member credentials:
   - Default members: `juan_perez`, `maria_lopez` (password: `gym2024`, `fit2024`)
   - Use the sync button to download your training data from the gym server

## 📋 Default Users

The system includes demo users with complete profiles:

| Username | Password | Access | Team/Level |
|----------|----------|--------|------------|
| `juan_perez` | `gym2024` | ✅ Enabled | Advanced Fitness |
| `maria_lopez` | `fit2024` | ✅ Enabled | Cardio & Resistance |
| `carlos_rodriguez` | `trainer123` | ❌ Blocked | Beginners |

Each user includes:
- Profile photo
- Complete personal information (email, phone, team assignment)
- Monthly training schedule
- Personal photo gallery
- Training progress data

## 🎯 Key Features

### For Gym Administrators
- ✅ **Member Database** - Complete member profiles with medical history, contact information, and documents
- ✅ **Training Program Builder** - Create and assign personalized workout routines with exercise library
- ✅ **Progress Monitoring** - Track member progress with measurements, photos, and performance metrics
- ✅ **Schedule Management** - Manage gym calendar, class schedules, and trainer availability
- ✅ **Membership & Payments** - Handle memberships, renewals, payments, and financial reporting
- ✅ **Communication Tools** - Direct messaging and group announcements to members
- ✅ **Real-time Synchronization** - Instant updates across all connected member applications
- ✅ **Server Health Monitoring** - Track server performance and client connections
- ✅ **Rate Limiting** - Protect server from abuse with automatic throttling

### For Gym Members
- ✅ **Personalized Training Plans** - Access workout routines with videos and instructions
- ✅ **Progress Tracking** - Log workouts, record body measurements, and view progress charts
- ✅ **Session Booking** - Reserve training sessions and classes with trainers
- ✅ **Direct Messaging** - Chat with trainers and receive gym announcements
- ✅ **Nutrition Plans** - View personalized meal plans and nutritional guidance
- ✅ **Offline Mode** - Access training data even without internet connection
- ✅ **Auto-sync** - Automatic synchronization with gym server when connected
- ✅ **Network Diagnostics** - Built-in tools to diagnose connection issues
- ✅ **Operation Queue** - Messages and updates queued when offline, sent automatically
- ✅ **Connection Quality Monitor** - Real-time network performance tracking

## 🏗️ Technical Architecture

### System Components

```
Gym Management System/
├── Admin Application (Madre)
│   ├── madre_main.py              # Entry point
│   ├── madre_server.py            # REST API (FastAPI)
│   ├── madre_gui.py               # Admin GUI (CustomTkinter)
│   ├── madre_db.py                # Database layer (SQLite)
│   ├── madre_db_extended.py       # Extended DB features
│   ├── madre_db_extended_features.py
│   ├── madre_db_extended_features2.py
│   ├── madre_server_extended_api.py   # Extended API endpoints
│   └── madre_server_extended_api2.py
│
├── Member Application (Hija)
│   ├── hija_main.py               # Entry point
│   ├── hija_comms.py              # API client
│   ├── hija_views.py              # Member GUI
│   └── hija_views_extended.py     # Extended views
│
├── Shared Modules
│   ├── shared/constants.py        # Shared constants
│   ├── shared/logger.py           # Logging configuration
│   ├── shared/network_monitor.py  # NEW: Network health monitoring
│   ├── shared/offline_queue.py    # NEW: Offline operation queue
│   ├── shared/enhanced_comms.py   # NEW: Enhanced communication layer
│   └── shared/server_resilience.py # NEW: Server resilience features
│
├── Configuration
│   ├── config/settings.py         # Environment variables
│   └── .env                       # Local configuration
│
├── Data
│   ├── data/gym_database.db       # SQLite database
│   └── data/hija_local/           # Local member data
│
├── Documentation
│   ├── README.md                  # This file
│   ├── NETWORK_TROUBLESHOOTING.md # NEW: Network configuration guide
│   └── IMPROVEMENT_SUGGESTIONS.md # NEW: Feature suggestions & roadmap
│
└── Utilities
    ├── populate_db.py             # Database initialization
    ├── test_system.py             # System tests
    ├── test_messaging.py          # Messaging tests
    └── test_resilience.py         # NEW: Resilience features tests
```

### Technology Stack

- **GUI Framework**: CustomTkinter (modern interface over Tkinter)
- **API Server**: FastAPI (high-performance REST API)
- **Database**: SQLite3 with thread-safety
- **HTTP Client**: requests library
- **Concurrency**: Python threading for GUI + server
- **Validation**: Pydantic models
- **Logging**: Python logging with file rotation
- **Configuration**: Environment variables with defaults

### Communication Flow

#### Authentication
1. Member app sends POST request to `/autorizar` with username/password
2. Admin server verifies credentials and member permissions
3. On approval, member app unlocks full functionality

#### Data Synchronization
1. Member app sends GET request to `/sincronizar_datos` with credentials
2. Admin server verifies member and returns training data, schedules, messages
3. Member app updates interface with received content
4. Automatic sync runs every 5-30 minutes in background

### Configuration

The system uses environment variables for configuration. Create a `.env` file to customize:

```bash
# Admin Server Configuration
MADRE_HOST=0.0.0.0
MADRE_PORT=8000

# Member App Configuration (point to gym server)
MADRE_BASE_URL=http://192.168.1.100:8000

# Database
DB_PATH=data/gym_database.db

# Logging
LOG_LEVEL=INFO
```

### Monitoring & Health Check

**View logs in real-time:**
```bash
# Linux/macOS
tail -f logs/madre_server.log

# Windows PowerShell
Get-Content logs/madre_server.log -Wait -Tail 10
```

**Check server health:**
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "online",
  "version": "1.0.0",
  "database_status": "healthy"
}
```

**Check detailed metrics:**
```bash
curl http://localhost:8000/health/metrics
```

Response:
```json
{
  "status": "ok",
  "metrics": {
    "uptime_seconds": 3600.5,
    "uptime_formatted": "1:00:00",
    "total_requests": 1234,
    "total_errors": 5,
    "error_rate": 0.004,
    "avg_response_time": 0.15,
    "status": "healthy"
  },
  "timestamp": "2024-11-07T22:30:00"
}
```

## 🌐 Network Resilience Features

### Connection Monitoring

The system now includes comprehensive network monitoring and diagnostics:

**Automatic Features:**
- ✅ **Health Checking** - Background monitoring every 60 seconds
- ✅ **Quality Scoring** - Network rated as excellent/good/fair/poor/critical
- ✅ **Adaptive Timeouts** - Automatically adjusts based on network quality
- ✅ **Failure Detection** - Recognizes connection issues immediately

**Connection Modes:**
- 🟢 **Normal** - Good connectivity, standard operation
- 🟡 **Degraded** - Poor quality, using longer timeouts
- 🔴 **Offline** - No connectivity, queuing operations
- 🔄 **Recovering** - Connection restored, processing queue

### Offline Operation Queue

Work continues even without connectivity:

**How It Works:**
1. When offline, operations are queued locally (messages, syncs, etc.)
2. Queue persists across app restarts
3. When connection restored, queue processes automatically
4. Failed operations retry with exponential backoff

**Supported Operations:**
- Login attempts (queued for retry)
- Data synchronization
- Message sending
- Chat messages
- Profile updates

**Queue Management:**
```python
# Check queue status
communicator = APICommunicator()
status = communicator.get_connection_status()
print(f"Queued operations: {status['queued_operations']}")

# Manually process queue
processed = communicator.process_offline_queue()
print(f"Processed {processed} operations")
```

### Network Diagnostics

Built-in diagnostic tools help troubleshoot connection issues:

**Automatic Diagnostics:**
```python
diagnosis = communicator.diagnose_connection()
print(f"Issues: {diagnosis['issues']}")
print(f"Recommendations: {diagnosis['recommendations']}")
```

**What Gets Checked:**
- Server reachability
- Port connectivity
- Firewall blocking
- Proxy configuration
- Network quality metrics
- Response time patterns

**Common Issues Detected:**
- Firewall blocking connection
- Antivirus interference
- Corporate proxy requirements
- DNS resolution failures
- Network congestion
- Server overload

### Firewall & Security Software

**Automatic Detection:**
The system can detect when firewalls or security software block connections and provides specific guidance.

**Configuration Help:**
See [NETWORK_TROUBLESHOOTING.md](NETWORK_TROUBLESHOOTING.md) for detailed instructions on:
- Windows Firewall configuration
- macOS firewall settings
- Linux firewall rules (UFW, firewalld, iptables)
- Antivirus exception setup
- Corporate proxy configuration

### Testing Your Connection

**Quick Test:**
```bash
# From member computer, test connectivity
python test_resilience.py
```

**Manual Check:**
```bash
# Test basic connectivity (Windows)
Test-NetConnection -ComputerName [SERVER_IP] -Port 8000

# Test basic connectivity (Mac/Linux)
nc -zv [SERVER_IP] 8000

# Test API endpoint
curl http://[SERVER_IP]:8000/health
```

## 🔒 Security

### Current Security Features
- ✅ Password hashing with SHA256
- ✅ Persistent SQLite database with thread-safety
- ✅ Permission validation on server
- ✅ 72-hour sync validation to ensure active membership
- ✅ Secure credential storage
- ✅ **NEW: Rate limiting** - Protection against abuse (60 req/min per client)
- ✅ **NEW: Circuit breaker** - Protection against cascading failures
- ✅ **NEW: Request timing** - Performance monitoring and alerts

### Production Recommendations
- 🔒 Migrate to bcrypt/argon2 for password hashing
- 🔒 Implement JWT tokens for session management
- 🔐 Add HTTPS/SSL for encrypted communication
- 🔐 Use system keyring for local credential storage
- 🔒 Implement API rate limiting
- 🔐 Consider PostgreSQL with SSL for production

> ⚠️ **Note**: This system includes basic security features suitable for internal gym networks. Additional security measures are recommended before deploying on public networks.

## 📦 Distribution

### Creating Windows Executables

To distribute member applications without requiring Python installation:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed hija_main.py
```

The executable will be in the `dist/` folder.

## 🚀 Future Enhancements

See `GYM_MANAGEMENT_FEATURES.md` for the complete roadmap of planned features, including:

- 📊 Advanced analytics and reporting dashboards
- 💳 Integrated payment processing
- 📱 Mobile app versions for iOS and Android
- 🎥 Video conferencing for virtual training sessions
- 📈 AI-powered training recommendations
- 🌐 Multi-gym support for gym chains
- 🎯 Gamification with achievements and leaderboards

## 📚 Documentation

- `README.md` (this file) - System overview and setup guide
- `GYM_MANAGEMENT_FEATURES.md` - Complete feature roadmap and priorities

## 📄 License

This project is an educational prototype and demonstration system for gym management.
