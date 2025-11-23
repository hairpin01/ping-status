#!/usr/bin/env python3
# Метаданные плагина для автоматического обновления
__plugin_url__ = "https://raw.githubusercontent.com/hairpin01/ping-status/refs/heads/main/plugins/disk-usage.plugin.py"
__name__ = "disk-usage"
__last_updated__ = "2025-11-23 23:32:00"
__version__ = "1.0.0"
__min_version__ = "3.3.0"

import shutil
from pathlib import Path

def get_help():
    return """
Disk Usage Plugin v1.0.0
========================

Shows disk usage in a compact, human-readable format.

Available Placeholders:
{disk}       - Main disk usage (e.g.: "💾 75%")
{disk_root}  - Root partition usage  
{disk_home}  - Home partition usage
{disk_all}   - All mounted disks summary

Configuration:
Add to ~/.config/ping-status.conf:

[disk-usage]
# Warning threshold (default: 85)
warning_threshold = 85

# Critical threshold (default: 95)  
critical_threshold = 95

# Show emoji (true/false)
show_emoji = true

# Monitor specific paths (comma separated)
paths = /,/home,/var

Features:
- Color-coded by usage level (green/yellow/red)
- Compact display perfect for status bars
- Multiple partition monitoring
- Threshold-based warnings
"""

def get_disk_config():
    """Get disk usage configuration"""
    config_path = Path.home() / '.config' / 'ping-status.conf'
    
    if not config_path.exists():
        config_path = Path('/etc/ping-status.conf')
    
    config = configparser.ConfigParser()
    config.read(config_path)
    
    return {
        'warning_threshold': config.getint('disk-usage', 'warning_threshold', fallback=85),
        'critical_threshold': config.getint('disk-usage', 'critical_threshold', fallback=95),
        'show_emoji': config.getboolean('disk-usage', 'show_emoji', fallback=True),
        'paths': [p.strip() for p in config.get('disk-usage', 'paths', fallback='/').split(',')]
    }

def get_disk_color(usage_percent, warning=85, critical=95):
    """Get color based on disk usage percentage"""
    if usage_percent >= critical:
        return 'red'
    elif usage_percent >= warning:
        return 'yellow'
    else:
        return 'green'

def format_disk_usage(path="/", show_emoji=True, warning=85, critical=95):
    """Format disk usage for a specific path"""
    try:
        usage = shutil.disk_usage(path)
        used_percent = (usage.used / usage.total) * 100
        used_gb = usage.used / (1024**3)
        total_gb = usage.total / (1024**3)
        
        color = get_disk_color(used_percent, warning, critical)
        emoji = "💾 " if show_emoji else ""
        
        # Compact format for status display
        if used_percent < 1:
            return f"{emoji}0%", color
        elif used_percent < 10:
            return f"{emoji}{used_percent:.0f}%", color
        else:
            return f"{emoji}{used_percent:.0f}%", color
            
    except Exception:
        return "💾 N/A", 'red'

def get_disk_summary():
    """Get summary of all monitored disks"""
    config = get_disk_config()
    paths = config['paths']
    
    if len(paths) == 1:
        # Single disk - simple format
        usage, color = format_disk_usage(
            paths[0], 
            config['show_emoji'],
            config['warning_threshold'],
            config['critical_threshold']
        )
        return usage, color
    else:
        # Multiple disks - show count of critical/warning disks
        critical_count = 0
        warning_count = 0
        
        for path in paths:
            try:
                usage = shutil.disk_usage(path)
                used_percent = (usage.used / usage.total) * 100
                
                if used_percent >= config['critical_threshold']:
                    critical_count += 1
                elif used_percent >= config['warning_threshold']:
                    warning_count += 1
            except:
                continue
        
        emoji = "💾 " if config['show_emoji'] else ""
        
        if critical_count > 0:
            return f"{emoji}{critical_count} crit", 'red'
        elif warning_count > 0:
            return f"{emoji}{warning_count} warn", 'yellow'
        else:
            return f"{emoji}ok", 'green'

def colorize_text(text, color):
    """Colorize text using ANSI codes"""
    colors = {
        'black': '30',
        'red': '31', 
        'green': '32',
        'yellow': '33',
        'blue': '34',
        'magenta': '35',
        'cyan': '36',
        'white': '37'
    }
    color_code = colors.get(color.lower(), '37')
    return f'\033[{color_code}m{text}\033[0m'

def register():
    """Plugin registration function"""
    try:
        config = get_disk_config()
        
        # Main disk usage (first path)
        main_usage, main_color = format_disk_usage(
            config['paths'][0],
            config['show_emoji'],
            config['warning_threshold'], 
            config['critical_threshold']
        )
        
        # Root partition
        root_usage, root_color = format_disk_usage(
            '/',
            config['show_emoji'],
            config['warning_threshold'],
            config['critical_threshold']
        )
        
        # Home partition (if different from root)
        home_usage, home_color = format_disk_usage(
            str(Path.home()),
            config['show_emoji'], 
            config['warning_threshold'],
            config['critical_threshold']
        )
        
        # Summary of all disks
        summary_usage, summary_color = get_disk_summary()
        
        return {
            'disk': colorize_text(main_usage, main_color),
            'disk_root': colorize_text(root_usage, root_color),
            'disk_home': colorize_text(home_usage, home_color),
            'disk_all': colorize_text(summary_usage, summary_color)
        }
        
    except Exception as e:
        error_msg = "💾 err"
        return {
            'disk': colorize_text(error_msg, 'red'),
            'disk_root': colorize_text(error_msg, 'red'),
            'disk_home': colorize_text(error_msg, 'red'), 
            'disk_all': colorize_text(error_msg, 'red')
        }
