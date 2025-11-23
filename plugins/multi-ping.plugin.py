#!/usr/bin/env python3

__plugin_url__ = "https://raw.githubusercontent.com/hairpin01/ping-status/refs/heads/main/plugins/multi-ping.plugin.py"
__name__ = "multi-ping"
__last_updated__ = "2025-11-23 23:00:00"
__version__ = "1.2.0"
__min_version__ = "3.3.0"

import subprocess
import configparser
from pathlib import Path
import statistics
import time

def get_help():
    return """
Multi-Ping Plugin v1.2.0
========================

Pings multiple servers and displays results with average calculation.

Available Placeholders:
{mping}          - Formatted multi-ping results with colors
{mping_short}    - Short version with average only  
{mping_avg}      - Just the average ping value
{mping_status}   - Status icons (✅/❌) for each server

Configuration:
Add to ~/.config/ping-status.conf:

[multi-ping]
# Servers to ping (supports up to 8 servers)
server-1 = 1.1.1.1
server-2 = 8.8.8.8
server-3 = google.com
server-4 = github.com
server-5 = archlinux.org

# Display names (optional, uses host if not set)
name-1 = Cloudflare
name-2 = Google DNS
name-3 = Google
name-4 = GitHub
name-5 = Arch Linux

# Colors for each server (comma separated)
colors = green,yellow,blue,magenta,cyan,white

# Ping attempts (default: 2)
attempts = 2

# Timeout in seconds (default: 1)
timeout = 1

# Display format (compact, detailed, status)
format = compact

# Show offline servers (true/false)
show_offline = true

Features:
- Colors each server result individually
- Calculates average of successful pings  
- Handles timeouts and unreachable servers
- Multiple display formats
- Caching for performance
"""

def get_multi_ping_config():
    """Get multi-ping configuration"""
    config_path = Path.home() / '.config' / 'ping-status.conf'
    
    if not config_path.exists():
        config_path = Path('/etc/ping-status.conf')
    
    config = configparser.ConfigParser()
    config.read(config_path)
    
    # Get colors
    colors_str = config.get('multi-ping', 'colors', fallback='green,yellow,blue,magenta,cyan,white')
    colors = [color.strip() for color in colors_str.split(',')]
    
    # Get servers and their display names
    servers = []
    display_names = {}
    
    for i in range(1, 9):  # Support up to 8 servers
        server = config.get('multi-ping', f'server-{i}', fallback='')
        if server:
            servers.append(server)
            # Get display name if specified
            name = config.get('multi-ping', f'name-{i}', fallback='')
            if name:
                display_names[server] = name
    
    # Ping parameters
    attempts = config.getint('multi-ping', 'attempts', fallback=2)
    timeout = config.getint('multi-ping', 'timeout', fallback=1)
    
    # Display settings
    display_format = config.get('multi-ping', 'format', fallback='compact')
    show_offline = config.getboolean('multi-ping', 'show_offline', fallback=True)
    
    return {
        'colors': colors,
        'servers': servers,
        'display_names': display_names,
        'attempts': attempts,
        'timeout': timeout,
        'format': display_format,
        'show_offline': show_offline
    }

def ping_server(host, attempts=2, timeout=1):
    """Ping server with multiple attempts and caching"""
    cache_file = Path.home() / '.cache' / 'ping-status' / 'multi-ping.json'
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Check cache (5 second cache for performance)
    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            if host in cache_data:
                cached_time = cache_data[host].get('timestamp', 0)
                if time.time() - cached_time < 5:  # 5 second cache
                    return cache_data[host].get('result')
        except:
            pass
    
    successful_pings = []
    
    for attempt in range(attempts):
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', str(timeout), host],
                capture_output=True,
                text=True,
                timeout=timeout + 1
            )
            
            if result.returncode == 0:
                time_line = [line for line in result.stdout.split('\n') if 'time=' in line]
                if time_line:
                    ping_time = time_line[0].split('time=')[1].split(' ')[0]
                    try:
                        # Extract numeric value, handle different formats
                        ping_ms = float(ping_time.replace(' ms', '').replace('ms', ''))
                        successful_pings.append(ping_ms)
                    except ValueError:
                        continue
        except (subprocess.TimeoutExpired, Exception):
            continue
    
    result = statistics.mean(successful_pings) if successful_pings else None
    
    # Update cache
    try:
        cache_data = {}
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
        cache_data[host] = {
            'timestamp': time.time(),
            'result': result
        }
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)
    except:
        pass
    
    return result

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

def get_multi_ping_results():
    """Get multi-ping results with formatting"""
    config = get_multi_ping_config()
    servers = config['servers']
    colors = config['colors']
    display_names = config['display_names']
    attempts = config['attempts']
    timeout = config['timeout']
    display_format = config['format']
    show_offline = config['show_offline']
    
    if not servers:
        return {
            'detailed': colorize_text("No servers configured", 'red'),
            'short': colorize_text("No servers", 'red'),
            'average': colorize_text("N/A", 'red'),
            'status': colorize_text("No config", 'red')
        }
    
    results = []
    status_icons = []
    successful_pings = []
    
    for i, server in enumerate(servers):
        color = colors[i % len(colors)]
        display_name = display_names.get(server, server)
        
        ping_result = ping_server(server, attempts, timeout)
        
        if ping_result is not None:
            # Successful ping
            if display_format == 'detailed':
                result_str = colorize_text(f"{display_name}: {ping_result:.1f}ms", color)
            else:
                # Compact format
                result_str = colorize_text(f"{ping_result:.0f}ms", color)
            
            results.append(result_str)
            status_icons.append("✅")
            successful_pings.append(ping_result)
        else:
            # Failed ping
            if show_offline:
                if display_format == 'detailed':
                    result_str = colorize_text(f"{display_name}: timeout", 'red')
                else:
                    result_str = colorize_text("✗", 'red')
                results.append(result_str)
            status_icons.append("❌")
    
    # Format output based on display format
    if successful_pings:
        avg_ping = statistics.mean(successful_pings)
        success_count = len(successful_pings)
        total_count = len(servers)
        
        if display_format == 'detailed':
            detailed = " | ".join(results)
            avg_str = colorize_text(f"Avg: {avg_ping:.1f}ms", 'white')
            detailed_output = f"{detailed} | {avg_str}"
        elif display_format == 'status':
            detailed_output = " ".join(status_icons)
        else:  # compact
            detailed_output = " ".join(results)
        
        short = f"{success_count}/{total_count} ok: {avg_ping:.1f}ms"
        status_output = " ".join(status_icons)
        
        return {
            'detailed': detailed_output,
            'short': short,
            'average': f"{avg_ping:.1f}ms",
            'status': status_output
        }
    else:
        error_msg = colorize_text("All servers offline", 'red')
        return {
            'detailed': error_msg,
            'short': error_msg,
            'average': error_msg,
            'status': "❌❌❌"
        }

def register():
    """Plugin registration function"""
    try:
        results = get_multi_ping_results()
        return {
            'mping': results['detailed'],
            'mping_short': results['short'],
            'mping_avg': results['average'],
            'mping_status': results['status']
        }
    except Exception as e:
        error_msg = f"Multi-ping error: {str(e)}"
        return {
            'mping': error_msg,
            'mping_short': error_msg,
            'mping_avg': "error",
            'mping_status': "⚠️"
        }
