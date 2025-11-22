# ping-status


### 📦 Installation
Automatic installation (recommended)
```bash
# Download the
curl -O installer https://raw.githubusercontent.com/your-username/ping-status/main/install-ping-status.sh

# Or via wget
wget https://raw.githubusercontent.com/your-username/ping-status/main/install-ping-status.sh

# Run
the chmod +x installation install-ping-status.sh
./install-ping-status.sh
```
### Installation options

```bash
# Complete installation with test
./install-ping-status.sh

# Skip installing dependencies
./install-ping-status.sh --skip-deps

# Update the configuration
only./install-ping-status.sh --config-only

# Update an existing installation
./install-ping-status.sh --update

# Show the help
./install-ping-status.sh --help
```

After installation, simply run:
```bash
p
```
Or a full team:
```bash
ping-status
```
Output example:
```output
════════════════════════════════
🖥️  System Status  
════════════════════════════════
Ping: 24.5 ms
Uptime: 2h 15m
User: archuser
Hostname: arch-pc
════════════════════════════════
```
Output Settings
Edit the ~/.config/ping-status.conf file

### 🔄 Update
```bash
./install-ping-status.sh --update
```
Troubleshooting
The command was not found
```bash
# Update the command cache
hash -r
# Or run the full path
/usr/local/bin/p
```
