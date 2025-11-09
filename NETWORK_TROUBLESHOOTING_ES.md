# Guía de Configuración de Red y Solución de Problemas

## Descripción General

Esta guía ayuda a users configure the Entrenador Personal aplicación to work correctly in various red environments, including scenarios with firewalls, antivirus software, or restrictive red configurations.

## Diagnósticos Rápidos

### Verificar Estado de Conexión

The aplicación now includes built-in conexión diagnósticos. Para verificar su conexión:

1. Open the aplicación
2. Buscar the conexión status indicator (top right)
3. Hacer clic en "conexión diagnósticos" or similar opción
4. Revisar el diagnostic report

### Problemas Comunes de Conexión

#### 1. No se Puede Conectar al Servidor

**Síntomas:**
- inicio de sesión fails with "conexión error"
- sincronizar botón shows "Cannot reach servidor"
- conexión status shows "sin conexión"

**Soluciones:**

1. **Verify servidor URL**
   - Verificar que the servidor URL in configuración is correct
   - Default: `http://127.0.0.1:8000` (local servidor)
   - For red servidor: `http://[SERVER_IP]:8000`

2. **Check Internet/red conexión**
   - Asegúrese de tener active internet/red connectivity
   - Intente acceder a other websites or red resources
   - Ping the servidor from command line:
     ```
     ping [SERVER_IP]
     ```

3. **Verify servidor is Running**
   - On the trainer's computer, ensure the Madre application is running
   - Verificar que the API servidor has started successfully
   - Buscar "servidor running on..." message in Madre aplicación

#### 2. cortafuegos Bloqueando la Conexión

**Síntomas:**
- conexión works on some networks but not others
- error message mentions "conexión refused" or "tiempo de espera"
- Diagnostic shows "cortafuegos may be blocking"

**Soluciones for Windows:**

1. **Add Windows cortafuegos Exception**
   - Open Windows Defender cortafuegos
   - Click "Allow an aplicación through cortafuegos"
   - Click "Change configuración" (requires admin)
   - Click "Allow another aplicación..."
   - Browse to Python executable or the aplicación executable
   - Check both "Private" and "Public" networks
   - Click "OK"

2. **Manual puerto Opening (Advanced)**
   - Open "Windows Defender cortafuegos with Advanced Security"
   - Click "Inbound Rules" → "New Rule"
   - Select "puerto" → Click "Next"
   - Select "TCP" and enter puerto `8000`
   - Select "Allow the conexión"
   - Check all profile types
   - Name it "Entrenador Personal aplicación"
   - Click "Finish"

**Soluciones for Mac:**

1. **System Preferences Security**
   - Open System Preferences → Security & Privacy
   - Click cortafuegos pestaña
   - Click lock icon to make changes
   - Click "cortafuegos Options"
   - Click "+" to add Python or the aplicación
   - Set to "Allow incoming connections"

**Soluciones for Linux:**

```bash
# UFW (Ubuntu/Debian)
sudo ufw allow 8000/tcp

# firewalld (Fedora/CentOS/RHEL)
sudo cortafuegos-cmd --permanent --add-puerto=8000/tcp
sudo cortafuegos-cmd --reload

# iptables
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
```

#### 3. antivirus Blocking conexión

**Síntomas:**
- conexión works briefly then stops
- antivirus shows warnings about red activity
- conexión diagnostic shows intermittent failures

**Soluciones:**

1. **Add to antivirus Exceptions**
   - Open your antivirus software
   - Find "Exceptions" or "Exclusions" configuración
   - Add the aplicación folder or executable to exceptions
   - Add the Python executable if using Python version

2. **Common antivirus Products:**

   **Avast/AVG:**
   - configuración → General → Exceptions
   - Add file path or folder

   **Norton:**
   - configuración → antivirus → Scans and Risks → Exclusions
   - Add the aplicación path

   **McAfee:**
   - Navigation → configuración → Real-Time Scanning → Excluded Files
   - Add the aplicación

   **Windows Defender:**
   - Windows Security → Virus & threat protection
   - Manage configuración → Exclusions
   - Add folder or file

#### 4. Corporate red / Proxy Issues

**Síntomas:**
- aplicación works at home but not at work
- Other apps require proxy configuración
- conexión diagnostic shows DNS or proxy errors

**Soluciones:**

1. **Configure Proxy configuración**
   
   Create or edit `.env` file in aplicación directory:
   ```
   HTTP_PROXY=http://proxy.company.com:8080
   HTTPS_PROXY=http://proxy.company.com:8080
   NO_PROXY=localhost,127.0.0.1
   ```

2. **Use Direct IP Address**
   - Instead of hostname, use IP address
   - Example: `http://192.168.1.100:8000` instead of `http://servidor.local:8000`

3. **Contact IT Department**
   - solicitud puerto 8000 be opened for internal communication
   - Provide this documentation to IT staff

#### 5. Slow or Unstable conexión

**Síntomas:**
- Frequent timeouts
- sincronizar takes very long
- conexión quality shows "Poor" or "Critical"

**Soluciones:**

1. **Use Wired conexión**
   - WiFi can be unstable; use Ethernet cable if possible

2. **Reduce red Load**
   - Close other applications using red
   - Pause downloads/uploads
   - Limit streaming while using aplicación

3. **Adjust sincronizar Frequency**
   - In aplicación configuración, increase sincronizar interval
   - Manual sincronizar instead of automatic

4. **Enable sin conexión Mode**
   - The aplicación now queues operations when sin conexión
   - Work sin conexión and sincronizar when conexión improves

## Advanced configuración

### Custom servidor puerto

If puerto 8000 is already in use, change it in both applications:

**Madre (servidor) - .env file:**
```
MADRE_PORT=8080
```

**Hija (cliente) - .env file:**
```
MADRE_BASE_URL=http://[SERVER_IP]:8080
```

### conexión Timeouts

Adjust timeouts for slow networks in `.env`:

```
HTTP_TIMEOUT_SHORT=10
HTTP_TIMEOUT_MEDIUM=20
HTTP_TIMEOUT_LONG=60
```

### red Quality Monitoring

Enable detailed red monitoring in `.env`:

```
ENABLE_NETWORK_MONITORING=true
HEALTH_CHECK_INTERVAL=60
```

## sin conexión Mode & Queue

### How It Works

When the aplicación detects no conexión:
1. Operations are queued locally
2. You can continue working with local data
3. When conexión restores, queued operations execute automatically

### Viewing Queue

- conexión status shows "X operations queued"
- Click to view pending operations
- Manually trigger sincronizar when ready

### Queue Persistence

Queued operations are saved to disk and survive aplicación restart.

## Testing Your configuración

### 1. Test Basic Connectivity

Run this command from command line:

**Windows PowerShell:**
```powershell
Test-NetConnection -ComputerName [SERVER_IP] -puerto 8000
```

**Mac/Linux:**
```bash
nc -zv [SERVER_IP] 8000
```

**éxito:** Shows "conexión successful" or similar
**falla:** Check cortafuegos and servidor status

### 2. Test API endpoint

**Windows PowerShell:**
```powershell
Invoke-WebRequest -Uri "http://[SERVER_IP]:8000/health"
```

**Mac/Linux/Windows Git Bash:**
```bash
curl http://[SERVER_IP]:8000/health
```

**Expected respuesta:**
```json
{
  "status": "en línea",
  "version": "3.1.0",
  "database_status": "healthy"
}
```

### 3. In-aplicación diagnósticos

1. Open aplicación
2. Go to configuración or Tools menú
3. Click "conexión diagnósticos"
4. Review diagnostic report
5. Follow recommended actions

## red Architecture

### Typical Setup

```
[Trainer Computer]
  └─ Madre aplicación (servidor)
     └─ puerto 8000
        └─ Local red (192.168.x.x)
           └─ [Student Computer 1]
              └─ Hija aplicación (cliente)
           └─ [Student Computer 2]
              └─ Hija aplicación (cliente)
           └─ [Student Computer N]
              └─ Hija aplicación (cliente)
```

### Security Considerations

1. **Internal red Only**
   - Run only on trusted local networks
   - Do NOT expose to internet without security

2. **cortafuegos configuración**
   - Only allow connections from known IP ranges
   - Consider MAC address filtering on router

3. **VPN for Remote Access**
   - Use VPN for remote students
   - Configure VPN to route to servidor red

## Getting Help

### Diagnostic Report

When requesting help, provide:

1. **conexión Diagnostic Report**
   - Copy from in-aplicación diagnósticos
   - Include all sections

2. **configuración**
   - servidor URL being used
   - Operating system (Windows/Mac/Linux)
   - red type (Home/Office/Public WiFi)

3. **Logs**
   - Location: `logs/` folder in aplicación directory
   - Relevant files:
     - `hija_comms.log` - Communication logs
     - `network_monitor.log` - red monitoring
     - `offline_queue.log` - Queue operations

### Support Checklist

Before contacting support:

- [ ] Verified servidor is running
- [ ] Checked cortafuegos configuración
- [ ] Tested with antivirus temporarily disabled
- [ ] Tried from different red/location
- [ ] Reviewed diagnostic report
- [ ] Checked logs for errors
- [ ] Attempted manual conexión test (curl/ping)

## Appendix: error Messages

### "error de conexión: No se pudo alcanzar la Aplicación Madre"

**Meaning:** Cannot reach the servidor
**Common Causes:**
- servidor not running
- Wrong servidor URL
- cortafuegos blocking
- red disconnected

### "error: La petición de conexión ha tardado demasiado"

**Meaning:** conexión tiempo de espera
**Common Causes:**
- Slow red
- servidor overloaded
- red congestion
- servidor URL incorrect (wrong IP)

### "Credenciales inválidas"

**Meaning:** Wrong nombre de usuario or contraseña
**Causes:**
- This is NOT a red issue
- Verify credentials with trainer

### "Permiso de acceso denegado por el administrador"

**Meaning:** Account disabled by trainer
**Causes:**
- This is NOT a red issue
- Contact trainer to enable account

### "Sincronización requerida. Última sincronizar: X horas atrás"

**Meaning:** Need to sincronizar (72 hour limit)
**Solution:**
- Click sincronizar botón
- Must have internet conexión
- If sin conexión, will queue and sincronizar automatically

## Best Practices

1. **Keep aplicación Updated**
   - Latest version has improved connectivity
   - Check for updates regularly

2. **Stable red**
   - Use wired conexión when possible
   - Avoid public WiFi for sensitive data

3. **Regular sincronizar**
   - sincronizar at least every 3 days
   - Don't wait until forced

4. **Monitor conexión Quality**
   - Verificar Estado de Conexión periodically
   - Address issues before they become problems

5. **Backup configuración**
   - Save `.env` file configuración
   - Document custom configuración

## solución de problemas Flowchart

```
Cannot Connect?
├─ Can ping servidor IP?
│  ├─ No → Check red conexión, servidor running
│  └─ Yes → Can connect to puerto 8000?
│     ├─ No → Check cortafuegos, antivirus
│     └─ Yes → Can access /health endpoint?
│        ├─ No → servidor issue, check Madre aplicación
│        └─ Yes → Check aplicación configuración/credentials
│
Slow conexión?
├─ WiFi or Wired?
│  ├─ WiFi → Try wired, move closer to router
│  └─ Wired → Check red bandwidth usage
│
Intermittent conexión?
├─ Check antivirus logs
├─ Monitor red quality in aplicación
└─ Consider enabling sin conexión queue
```
