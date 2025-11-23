### ping-status
> [Telegram,
> hairpin](t.me/Hairpin00)

# 📦 Installation
```bash
# Download the
curl -sSL https://raw.githubusercontent.com/hairpin01/ping-status/main/install.sh | bash
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



# Install with a modern theme 
```
./install.sh --theme classic
```
> [!TIP]
> Install with the theme from the URL
> `./install.sh --theme-url https://example.com/my-theme.conf`


### Plugins
> [!NOTE]
> Where are the plugins stored? `~/.config/ping-status/plugins/`
## Installing plugins
```
# Show available plugins
ping-status --list-plugins
```
```
# Install the
ping-status --install-plugin system-info plugin
```
```
# Install the plugin from the URL
ping-status --plugin-url https://example.com/plugin.py
```
```
# Show help for plugins
ping-status --plugin-help # All plugins
ping-status --plugin-help system-info # Specific plugin
```

## Creating your own plugins
> [!TIP]
> Create a file in ~/.config/ping-status/plugins/your-plugin.plugin.py:
```python
#!/usr/bin/env python3

def get_help():
    return """
My Plugin
=========

Description of your plugin.

Placeholders:
{custom_field} - Description of what this field shows.

Configuration:
Add to config:
[my_plugin]
setting = value
"""

def register():
    return {
        'custom_field': 'Your custom value'
    }
```
> [!TIP]
> The plugin/theme must have
```
[compatibility]
min_version = 3.3.0 # (for themes)
```
```
__min_version__ = "3.3.0" # (for plugins)
__plugin_url__ = "URL"
__name__ = "plugin"
__version__ = "0.0.0"
__last_update__ = "2025-11-23 23:13:00"
```

> [!WARNING]
> to enable plugins, add to the conf file
``` 
[plugins]
enabled = system-info,weather # or all
```
# Example
```ini
[settings]
host = google.com
text = ╔═══════════════════════════════╗
       ║         SYSTEM STATUS         ║
       ╠═══════════════════════════════╣
       ║ 🚀 Hostname: {hostname}       ║
       ║ 👨‍💻 User: {user}               ║
       ║ ⏱️  Uptime: {uptime}          ║
       ║ 📡 Ping: {ping}               ║
       ║ {system_info}                 ║
       ║ {weather}                     ║
       ╚═══════════════════════════════╝

[colors]
hostname = cyan
user = blue
uptime = yellow
ping = green

[plugins]
enabled = system-info,weather

[weather]
api_key = YOUR_API_KEY_HERE
city = Moscow
units = metric
lang = en
```
