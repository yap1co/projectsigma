# External Access Configuration

## Server Configuration

### Current Setup
- **Port**: `5000`
- **Host**: `0.0.0.0` (listens on all network interfaces)
- **Local URL**: `http://localhost:5000` or `http://127.0.0.1:5000`

### Finding Your External IP Address

#### On Windows (PowerShell):
```powershell
# Get your local network IP address
ipconfig | findstr IPv4

# Or get your public/external IP address
Invoke-RestMethod -Uri "https://api.ipify.org?format=json"
```

#### On Windows (Command Prompt):
```cmd
ipconfig
# Look for "IPv4 Address" under your active network adapter
```

#### Quick Online Check:
Visit: https://whatismyipaddress.com/ or https://api.ipify.org

## Accessing the Server

### 1. Local Network Access (Same WiFi/LAN)
If you want to access from other devices on the same network:

**Your Local IP**: Check with `ipconfig` (usually something like `192.168.1.x` or `10.0.0.x`)

**Access URL**: `http://YOUR_LOCAL_IP:5000`
- Example: `http://192.168.1.100:5000`

### 2. External/Internet Access
To access from outside your local network, you need:

#### Option A: Port Forwarding (Router Configuration)
1. Find your router's admin panel (usually `192.168.1.1` or `192.168.0.1`)
2. Set up port forwarding:
   - **External Port**: `5000` (or any port you prefer)
   - **Internal IP**: Your computer's local IP (from `ipconfig`)
   - **Internal Port**: `5000`
   - **Protocol**: TCP
3. Access via: `http://YOUR_PUBLIC_IP:5000`

#### Option B: Cloud Deployment
For production use, consider:
- **Heroku**: Free tier available
- **Railway**: Easy deployment
- **DigitalOcean**: VPS hosting
- **AWS EC2**: Scalable cloud hosting

## Security Considerations

⚠️ **IMPORTANT**: The current server is configured for **development only**!

### Before Exposing Externally:

1. **Disable Debug Mode**:
   ```python
   # In server/app.py, line 857, change:
   app.run(debug=True, host='0.0.0.0', port=5000)
   # To:
   app.run(debug=False, host='0.0.0.0', port=5000)
   ```

2. **Use Production WSGI Server**:
   - **Gunicorn** (recommended):
     ```bash
     pip install gunicorn
     gunicorn -w 4 -b 0.0.0.0:5000 app:app
     ```
   - **Waitress** (Windows-friendly):
     ```bash
     pip install waitress
     waitress-serve --host=0.0.0.0 --port=5000 app:app
     ```

3. **Configure Firewall**:
   ```powershell
   # Allow port 5000 through Windows Firewall
   New-NetFirewallRule -DisplayName "Flask App" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
   ```

4. **Use HTTPS** (for production):
   - Set up SSL/TLS certificate
   - Use reverse proxy (nginx, Apache)
   - Or use a service like Cloudflare

5. **Environment Variables**:
   - Never expose `.env` files
   - Use secure JWT secret keys
   - Use strong database passwords

## Testing External Access

### From Local Network:
1. Find your local IP: `ipconfig`
2. On another device (phone/tablet), connect to same WiFi
3. Access: `http://YOUR_LOCAL_IP:5000`

### From Internet:
1. Set up port forwarding on your router
2. Find your public IP: Visit https://api.ipify.org
3. Access: `http://YOUR_PUBLIC_IP:5000`

## Quick Reference

```bash
# Start server (development)
cd server
python app.py

# Start server (production with Gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Start server (production with Waitress - Windows)
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

## Troubleshooting

### Can't Access from Other Devices:
1. ✅ Check Windows Firewall allows port 5000
2. ✅ Verify server is running on `0.0.0.0` (not `127.0.0.1`)
3. ✅ Ensure devices are on same network
4. ✅ Check router doesn't block local device communication

### Can't Access from Internet:
1. ✅ Configure router port forwarding
2. ✅ Check ISP doesn't block incoming connections
3. ✅ Verify public IP is correct
4. ✅ Consider using a dynamic DNS service (e.g., No-IP, DuckDNS)

## Frontend Configuration

If accessing the backend externally, update the frontend API URL:

**File**: `client/lib/api.ts`

```typescript
// Change from:
const API_URL = 'http://localhost:5000/api'

// To your external URL:
const API_URL = 'http://YOUR_EXTERNAL_IP:5000/api'
// Or for production:
const API_URL = 'https://your-domain.com/api'
```
