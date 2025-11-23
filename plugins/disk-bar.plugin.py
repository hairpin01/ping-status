#!/usr/bin/env python3
__plugin_url__ = "https://raw.githubusercontent.com/hairpin01/ping-status/refs/heads/main/plugins/disk-bar.plugin.py"
__name__ = "disk-bar"
__last_updated__ = "2025-11-25 23:31:00"
__version__ = "1.0.0"
__min_version__ = "3.3.0"

import shutil
import configparser
from pathlib import Path

def get_help():
    return """
Disk Bar Plugin v1.0.0
======================

Shows disk usage as visual progress bars.

Available Placeholders:
{disk_bar}        - Main disk bar (default: /)
{disk_bar_root}   - Root partition bar  
{disk_bar_home}   - Home partition bar
{disk_bar_boot}   - Boot partition bar
{disk_bar_all}    - All disks summary bar

Configuration:
Add to ~/.config/ping-status.conf:

[disk-bar]
# Bar style (default: modern)
# Options: modern, classic, blocks, gradient, simple
bar_style = modern

# Bar length (default: 10)
bar_length = 10

# Show percentage (true/false)
show_percentage = true

# Show used/total (true/false) 
show_size = false

# Colors for different usage levels
color_low = green
color_medium = yellow  
color_high = red

# Usage thresholds (percentage)
threshold_medium = 70
threshold_high = 90

# Characters for bar (depends on style)
filled_char = ■
empty_char = □
gradient_chars = ░▒▓█

Features:
- Multiple visual styles
- Color-coded by usage level
- Customizable bar length
- Multiple partition support
- Compact and informative
"""

def get_disk_bar_config():
    """Get disk bar configuration"""
    config_path = Path.home() / '.config' / 'ping-status.conf'
    
    if not config_path.exists():
        config_path = Path('/etc/ping-status.conf')
    
    config = configparser.ConfigParser()
    config.read(config_path)
    
    return {
        'bar_style': config.get('disk-bar', 'bar_style', fallback='modern'),
        'bar_length': config.getint('disk-bar', 'bar_length', fallback=10),
        'show_percentage': config.getboolean('disk-bar', 'show_percentage', fallback=True),
        'show_size': config.getboolean('disk-bar', 'show_size', fallback=False),
        'color_low': config.get('disk-bar', 'color_low', fallback='green'),
        'color_medium': config.get('disk-bar', 'color_medium', fallback='yellow'),
        'color_high': config.get('disk-bar', 'color_high', fallback='red'),
        'threshold_medium': config.getint('disk-bar', 'threshold_medium', fallback=70),
        'threshold_high': config.getint('disk-bar', 'threshold_high', fallback=90),
        'filled_char': config.get('disk-bar', 'filled_char', fallback='■'),
        'empty_char': config.get('disk-bar', 'empty_char', fallback='□'),
        'gradient_chars': config.get('disk-bar', 'gradient_chars', fallback='░▒▓█')
    }

def get_disk_usage(path):
    """Get disk usage for path"""
    try:
        usage = shutil.disk_usage(path)
        used_percent = (usage.used / usage.total) * 100
        used_gb = usage.used / (1024**3)
        total_gb = usage.total / (1024**3)
        return used_percent, used_gb, total_gb
    except Exception:
        return None, None, None

def get_usage_color(percent, config):
    """Get color based on usage percentage"""
    if percent >= config['threshold_high']:
        return config['color_high']
    elif percent >= config['threshold_medium']:
        return config['color_medium']
    else:
        return config['color_low']

def format_size(gb):
    """Format size in GB to human readable"""
    if gb is None:
        return "N/A"
    
    if gb < 1:
        return f"{gb*1024:.0f}MB"
    elif gb < 10:
        return f"{gb:.1f}GB"
    else:
        return f"{gb:.0f}GB"

def create_bar(percent, config):
    """Create visual progress bar"""
    if percent is None:
        return "N/A"
    
    bar_length = config['bar_length']
    style = config['bar_style']
    
    filled_length = int(bar_length * percent / 100)
    empty_length = bar_length - filled_length
    
    if style == 'modern':
        # Modern style with blocks
        filled_char = config['filled_char']
        empty_char = config['empty_char']
        bar = filled_char * filled_length + empty_char * empty_length
        return f"[{bar}]"
    
    elif style == 'classic':
        # Classic progress bar
        bar = '█' * filled_length + '░' * empty_length
        return f"[{bar}]"
    
    elif style == 'blocks':
        # Block characters
        bars = ['▱', '▰']
        bar = bars[1] * filled_length + bars[0] * empty_length
        return bar
    
    elif style == 'gradient':
        # Gradient effect
        chars = config['gradient_chars']
        if len(chars) < 4:
            chars = '░▒▓█'
        
        bar = ""
        for i in range(bar_length):
            progress = (i + 1) / bar_length
            if progress <= percent / 100:
                # Calculate gradient level
                level = min(int(progress * len(chars)), len(chars) - 1)
                bar += chars[level]
            else:
                bar += chars[0]
        return bar
    
    elif style == 'simple':
        # Simple brackets
        bar = '|' * filled_length + '.' * empty_length
        return f"[{bar}]"
    
    else:
        # Default modern style
        bar = '■' * filled_length + '□' * empty_length
        return f"[{bar}]"

def create_disk_bar(path, label=None):
    """Create disk bar for specific path"""
    config = get_disk_bar_config()
    percent, used_gb, total_gb = get_disk_usage(path)
    
    if percent is None:
        return "N/A"
    
    # Create the bar
    bar = create_bar(percent, config)
    
    # Get color
    color = get_usage_color(percent, config)
    
    # Build the output
    parts = []
    
    if label:
        parts.append(f"{label}:")
    
    parts.append(bar)
    
    if config['show_percentage']:
        parts.append(f"{percent:.0f}%")
    
    if config['show_size'] and used_gb is not None and total_gb is not None:
        parts.append(f"({format_size(used_gb)}/{format_size(total_gb)})")
    
    output = " ".join(parts)
    return colorize_text(output, color)

def create_summary_bar():
    """Create summary bar for all disks"""
    config = get_disk_bar_config()
    
    # Check main partitions
    partitions = [
        ('/', 'root'),
        (str(Path.home()), 'home'),
        ('/boot', 'boot')
    ]
    
    critical_count = 0
    total_percent = 0
    valid_partitions = 0
    
    for path, label in partitions:
        percent, _, _ = get_disk_usage(path)
        if percent is not None:
            valid_partitions += 1
            total_percent += percent
            if percent >= config['threshold_high']:
                critical_count += 1
    
    if valid_partitions == 0:
        return colorize_text("No disks", 'red')
    
    avg_percent = total_percent / valid_partitions
    
    # Create summary
    if critical_count > 0:
        summary = f"🚨 {critical_count} crit"
        color = config['color_high']
    elif avg_percent >= config['threshold_medium']:
        summary = "⚠️  high"
        color = config['color_medium']
    else:
        summary = "✓ ok"
        color = config['color_low']
    
    return colorize_text(summary, color)

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
        return {
            'disk_bar': create_disk_bar('/'),
            'disk_bar_root': create_disk_bar('/'),
            'disk_bar_home': create_disk_bar(str(Path.home())),
            'disk_bar_boot': create_disk_bar('/boot'),
            'disk_bar_all': create_summary_bar()
        }
    except Exception as e:
        error_msg = "💾 error"
        return {
            'disk_bar': colorize_text(error_msg, 'red'),
            'disk_bar_root': colorize_text(error_msg, 'red'),
            'disk_bar_home': colorize_text(error_msg, 'red'),
            'disk_bar_boot': colorize_text(error_msg, 'red'),
            'disk_bar_all': colorize_text(error_msg, 'red')
        }
