# Sharing Travel Tales on Local Network (Docker) 🔥

Follow these steps to let your friends on the same WiFi access the application.

## 1. Find Your Private IP address
- **Windows**: Run `ipconfig` in Command Prompt. Look for "IPv4 Address" (e.g., `192.168.1.105`).
- **macOS/Linux**: Run `ifconfig` or `ip addr`. Look for `inet` under your WiFi interface.

## 2. Start the Container
Use the development profile to support hot-reloading and clear logs:
```bash
docker compose --profile dev up --build -d
```
Check logs to verify the server is listening:
```bash
docker compose --profile dev logs -f
# Should see: * Running on all addresses (0.0.0.0)
```

## 3. Firewall Setup (Crucial)
Your computer might block incoming requests on port 5000 by default.
- **Windows**: Ensure "Python" or "Docker Desktop" is allowed through Windows Defender Firewall for **Private networks**.
- **Linux (ufw)**: `sudo ufw allow 5000`
- **macOS**: System Settings -> Network -> Firewall -> Options -> Allow incoming connections for Python.

## 4. Friend Access
Give your friends your IP and the port:
**Link**: `http://<YOUR-IP>:5000`
- Example: `http://192.168.1.105:5000`

## 5. Troubleshooting
- **Cannot Reach**: 
  - Verify both devices are on the **exact same WiFi**.
  - Try to `ping <YOUR-IP>` from your friend's device.
  - Disable VPNs on both devices.
- **Broken Data**:
  - Run `http://<YOUR-IP>:5000/seed-data` once to populate the database.
- **Still Stuck**:
  - Reset everything: `docker compose --profile dev down && docker compose --profile dev up -d`

## ⚠️ Security Reminder
- This setup is for **local network only**.
- Do not use "Port Forwarding" to expose this to the public internet.
- The Flask dev server is not audited for production security.
