### ping-status
> [Telegram,
> hairpin](t.me/Hairpin00)

# 📦 Installation
```bash
# Download the
curl -O installer https://raw.githubusercontent.com/hairpin01/ping-status/main/install.sh
```
> [!NOTE]
> Or via wget `wget https://raw.githubusercontent.com/hairpin01/ping-status/main/install.sh`
# Run the
`chmod +x installation install.sh`

`./install.sh`

# Installation options
 `Skip installing` dependencies `--skip-deps`
 Update the configuration only `--config-only`
 Update an existing installation `--update`
> [!TIP]
> Show the help
> `./install --help`

1. After installation, simply run: `p`
2. Or a full team: `ping-status`

> [!NOTE] 
> Output example:
```output
════════════════════════════════
🖥️  System Status  
════════════════════════════════
Ping: XXX ms
Uptime: XXh XXm 
User: archuser
Hostname: arch-pc
═══════════════════════════════
```
> [!TIP]
> Output Settings
> Edit the `~/.config/ping-status.conf` file

# 🔄 Update
```
./install --update
```
# Troubleshooting
The command was not found
```
# Update the command cache
hash -r
# Or run the full path
/usr/local/bin/p
```

# Removal:
1. Through the installer
`./install.sh --uninstall`

2. Via the script
`sudo ping-status --uninstall`

> [!TIP]
> Checking for updates:
> `ping-status --check-update`
> Show the version: `ping-status --version`

### Use with themes
Installation with a `theme`:
```
# Install with a minimalistic theme
./install.sh --theme minimal
```
```
# Install with a modern theme 
./install.sh --theme classic
```
> [!TIP]
> Install with the theme from the URL
> `./install.sh --theme url https://example.com/my-theme.conf`
