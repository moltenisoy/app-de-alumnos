# Network Configuration & Troubleshooting Guide

## Overview

This guide helps users configure the Personal Trainer app to work correctly in various network environments, including scenarios with firewalls, antivirus software, or restrictive network configurations.

## Quick Diagnostics

### Check Connection Status

The app now includes built-in connection diagnostics. To check your connection:

1. Open the app
2. Look for the connection status indicator (top right)
3. Click on "Connection Diagnostics" or similar option
4. Review the diagnostic report

### Common Connection Issues

#### 1. Cannot Connect to Server

**Symptoms:**
- Login fails with "Connection error"
- Sync button shows "Cannot reach server"
- Connection status shows "Offline"

**Solutions:**

1. **Verify Server URL**
   - Check that the server URL in settings is correct
   - Default: `http://127.0.0.1:8000` (local server)
   - For network server: `http://[SERVER_IP]:8000`

2. **Check Internet/Network Connection**
   - Ensure you have active internet/network connectivity
   - Try accessing other websites or network resources
   - Ping the server from command line:
     ```
     ping [SERVER_IP]
     ```

3. **Verify Server is Running**
   - On the trainer's computer, ensure the Madre application is running
   - Check that the API server has started successfully
   - Look for "Server running on..." message in Madre app

#### 2. Firewall Blocking Connection

**Symptoms:**
- Connection works on some networks but not others
- Error message mentions "Connection refused" or "Timeout"
- Diagnostic shows "Firewall may be blocking"

**Solutions for Windows:**

1. **Add Windows Firewall Exception**
   - Open Windows Defender Firewall
   - Click "Allow an app through firewall"
   - Click "Change settings" (requires admin)
   - Click "Allow another app..."
   - Browse to Python executable or the app executable
   - Check both "Private" and "Public" networks
   - Click "OK"

2. **Manual Port Opening (Advanced)**
   - Open "Windows Defender Firewall with Advanced Security"
   - Click "Inbound Rules" → "New Rule"
   - Select "Port" → Click "Next"
   - Select "TCP" and enter port `8000`
   - Select "Allow the connection"
   - Check all profile types
   - Name it "Personal Trainer App"
   - Click "Finish"

**Solutions for Mac:**

1. **System Preferences Security**
   - Open System Preferences → Security & Privacy
   - Click Firewall tab
   - Click lock icon to make changes
   - Click "Firewall Options"
   - Click "+" to add Python or the app
   - Set to "Allow incoming connections"

**Solutions for Linux:**

```bash
# UFW (Ubuntu/Debian)
sudo ufw allow 8000/tcp

# firewalld (Fedora/CentOS/RHEL)
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# iptables
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
```

#### 3. Antivirus Blocking Connection

**Symptoms:**
- Connection works briefly then stops
- Antivirus shows warnings about network activity
- Connection diagnostic shows intermittent failures

**Solutions:**

1. **Add to Antivirus Exceptions**
   - Open your antivirus software
   - Find "Exceptions" or "Exclusions" settings
   - Add the app folder or executable to exceptions
   - Add the Python executable if using Python version

2. **Common Antivirus Products:**

   **Avast/AVG:**
   - Settings → General → Exceptions
   - Add file path or folder

   **Norton:**
   - Settings → Antivirus → Scans and Risks → Exclusions
   - Add the app path

   **McAfee:**
   - Navigation → Settings → Real-Time Scanning → Excluded Files
   - Add the app

   **Windows Defender:**
   - Windows Security → Virus & threat protection
   - Manage settings → Exclusions
   - Add folder or file

#### 4. Corporate Network / Proxy Issues

**Symptoms:**
- App works at home but not at work
- Other apps require proxy configuration
- Connection diagnostic shows DNS or proxy errors

**Solutions:**

1. **Configure Proxy Settings**
   
   Create or edit `.env` file in app directory:
   ```
   HTTP_PROXY=http://proxy.company.com:8080
   HTTPS_PROXY=http://proxy.company.com:8080
   NO_PROXY=localhost,127.0.0.1
   ```

2. **Use Direct IP Address**
   - Instead of hostname, use IP address
   - Example: `http://192.168.1.100:8000` instead of `http://server.local:8000`

3. **Contact IT Department**
   - Request port 8000 be opened for internal communication
   - Provide this documentation to IT staff

#### 5. Slow or Unstable Connection

**Symptoms:**
- Frequent timeouts
- Sync takes very long
- Connection quality shows "Poor" or "Critical"

**Solutions:**

1. **Use Wired Connection**
   - WiFi can be unstable; use Ethernet cable if possible

2. **Reduce Network Load**
   - Close other applications using network
   - Pause downloads/uploads
   - Limit streaming while using app

3. **Adjust Sync Frequency**
   - In app settings, increase sync interval
   - Manual sync instead of automatic

4. **Enable Offline Mode**
   - The app now queues operations when offline
   - Work offline and sync when connection improves

## Advanced Configuration

### Custom Server Port

If port 8000 is already in use, change it in both applications:

**Madre (Server) - .env file:**
```
MADRE_PORT=8080
```

**Hija (Client) - .env file:**
```
MADRE_BASE_URL=http://[SERVER_IP]:8080
```

### Connection Timeouts

Adjust timeouts for slow networks in `.env`:

```
HTTP_TIMEOUT_SHORT=10
HTTP_TIMEOUT_MEDIUM=20
HTTP_TIMEOUT_LONG=60
```

### Network Quality Monitoring

Enable detailed network monitoring in `.env`:

```
ENABLE_NETWORK_MONITORING=true
HEALTH_CHECK_INTERVAL=60
```

## Offline Mode & Queue

### How It Works

When the app detects no connection:
1. Operations are queued locally
2. You can continue working with local data
3. When connection restores, queued operations execute automatically

### Viewing Queue

- Connection status shows "X operations queued"
- Click to view pending operations
- Manually trigger sync when ready

### Queue Persistence

Queued operations are saved to disk and survive app restart.

## Testing Your Configuration

### 1. Test Basic Connectivity

Run this command from command line:

**Windows PowerShell:**
```powershell
Test-NetConnection -ComputerName [SERVER_IP] -Port 8000
```

**Mac/Linux:**
```bash
nc -zv [SERVER_IP] 8000
```

**Success:** Shows "Connection successful" or similar
**Failure:** Check firewall and server status

### 2. Test API Endpoint

**Windows PowerShell:**
```powershell
Invoke-WebRequest -Uri "http://[SERVER_IP]:8000/health"
```

**Mac/Linux/Windows Git Bash:**
```bash
curl http://[SERVER_IP]:8000/health
```

**Expected Response:**
```json
{
  "status": "online",
  "version": "3.1.0",
  "database_status": "healthy"
}
```

### 3. In-App Diagnostics

1. Open app
2. Go to Settings or Tools menu
3. Click "Connection Diagnostics"
4. Review diagnostic report
5. Follow recommended actions

## Network Architecture

### Typical Setup

```
[Trainer Computer]
  └─ Madre App (Server)
     └─ Port 8000
        └─ Local Network (192.168.x.x)
           └─ [Student Computer 1]
              └─ Hija App (Client)
           └─ [Student Computer 2]
              └─ Hija App (Client)
           └─ [Student Computer N]
              └─ Hija App (Client)
```

### Security Considerations

1. **Internal Network Only**
   - Run only on trusted local networks
   - Do NOT expose to internet without security

2. **Firewall Configuration**
   - Only allow connections from known IP ranges
   - Consider MAC address filtering on router

3. **VPN for Remote Access**
   - Use VPN for remote students
   - Configure VPN to route to server network

## Getting Help

### Diagnostic Report

When requesting help, provide:

1. **Connection Diagnostic Report**
   - Copy from in-app diagnostics
   - Include all sections

2. **Configuration**
   - Server URL being used
   - Operating system (Windows/Mac/Linux)
   - Network type (Home/Office/Public WiFi)

3. **Logs**
   - Location: `logs/` folder in app directory
   - Relevant files:
     - `hija_comms.log` - Communication logs
     - `network_monitor.log` - Network monitoring
     - `offline_queue.log` - Queue operations

### Support Checklist

Before contacting support:

- [ ] Verified server is running
- [ ] Checked firewall settings
- [ ] Tested with antivirus temporarily disabled
- [ ] Tried from different network/location
- [ ] Reviewed diagnostic report
- [ ] Checked logs for errors
- [ ] Attempted manual connection test (curl/ping)

## Appendix: Error Messages

### "Error de conexión: No se pudo alcanzar la Aplicación Madre"

**Meaning:** Cannot reach the server
**Common Causes:**
- Server not running
- Wrong server URL
- Firewall blocking
- Network disconnected

### "Error: La petición de conexión ha tardado demasiado"

**Meaning:** Connection timeout
**Common Causes:**
- Slow network
- Server overloaded
- Network congestion
- Server URL incorrect (wrong IP)

### "Credenciales inválidas"

**Meaning:** Wrong username or password
**Causes:**
- This is NOT a network issue
- Verify credentials with trainer

### "Permiso de acceso denegado por el administrador"

**Meaning:** Account disabled by trainer
**Causes:**
- This is NOT a network issue
- Contact trainer to enable account

### "Sincronización requerida. Última sync: X horas atrás"

**Meaning:** Need to sync (72 hour limit)
**Solution:**
- Click sync button
- Must have internet connection
- If offline, will queue and sync automatically

## Best Practices

1. **Keep App Updated**
   - Latest version has improved connectivity
   - Check for updates regularly

2. **Stable Network**
   - Use wired connection when possible
   - Avoid public WiFi for sensitive data

3. **Regular Sync**
   - Sync at least every 3 days
   - Don't wait until forced

4. **Monitor Connection Quality**
   - Check connection status periodically
   - Address issues before they become problems

5. **Backup Configuration**
   - Save `.env` file configuration
   - Document custom settings

## Troubleshooting Flowchart

```
Cannot Connect?
├─ Can ping server IP?
│  ├─ No → Check network connection, server running
│  └─ Yes → Can connect to port 8000?
│     ├─ No → Check firewall, antivirus
│     └─ Yes → Can access /health endpoint?
│        ├─ No → Server issue, check Madre app
│        └─ Yes → Check app configuration/credentials
│
Slow Connection?
├─ WiFi or Wired?
│  ├─ WiFi → Try wired, move closer to router
│  └─ Wired → Check network bandwidth usage
│
Intermittent Connection?
├─ Check antivirus logs
├─ Monitor network quality in app
└─ Consider enabling offline queue
```
