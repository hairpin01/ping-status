#!/usr/bin/env python3

import subprocess
import configparser
from pathlib import Path
import statistics

def get_help():
    return """
Multi-Ping Plugin
==================

Pings multiple servers and displays results with average calculation.

Available Placeholders:
{mping}          - Formatted multi-ping results with colors
{mping_short}    - Short version with average only
{mping_avg}      - Just the average ping value

Configuration:
Add to ~/.config/ping-status.conf:

[multi-ping]
# Colors for each server (comma separated)
colors = green,yellow,red,magenta,cyan

# Servers to ping (max 5)
server-1 = 1.1.1.1
server-2 = 8.8.8.8
server-3 = google.com
server-4 = github.com
server-5 = archlinux.org

# Ping attempts (default: 3)
attempts = 3

# Timeout in seconds (default: 1)
timeout = 1

Features:
- Colors each server result individually
- Calculates average of successful pings
- Handles timeouts and unreachable servers
- Compact and detailed display options
"""

def get_multi_ping_config():
    """Получить конфигурацию multi-ping"""
    config_path = Path.home() / '.config' / 'ping-status.conf'
    
    if not config_path.exists():
        config_path = Path('/etc/ping-status.conf')
    
    config = configparser.ConfigParser()
    config.read(config_path)
    
    # Получаем цвета
    colors_str = config.get('multi-ping', 'colors', fallback='green,yellow,red,magenta,cyan')
    colors = [color.strip() for color in colors_str.split(',')]
    
    # Получаем серверы (максимум 5)
    servers = []
    for i in range(1, 6):
        server = config.get('multi-ping', f'server-{i}', fallback='')
        if server:
            servers.append(server)
    
    # Параметры ping
    attempts = config.getint('multi-ping', 'attempts', fallback=3)
    timeout = config.getint('multi-ping', 'timeout', fallback=1)
    
    return {
        'colors': colors,
        'servers': servers,
        'attempts': attempts,
        'timeout': timeout
    }

def ping_server(host, attempts=3, timeout=1):
    """Пинг сервера с несколькими попытками"""
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
                    # Извлекаем числовое значение
                    try:
                        ping_ms = float(ping_time.replace(' ms', ''))
                        successful_pings.append(ping_ms)
                    except ValueError:
                        continue
        except (subprocess.TimeoutExpired, Exception):
            continue
    
    if successful_pings:
        avg_ping = statistics.mean(successful_pings)
        return avg_ping
    else:
        return None

def colorize_text(text, color):
    """Цветовой вывод текста"""
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
    """Получить результаты множественного пинга"""
    config = get_multi_ping_config()
    servers = config['servers']
    colors = config['colors']
    attempts = config['attempts']
    timeout = config['timeout']
    
    if not servers:
        return "No servers configured"
    
    results = []
    successful_pings = []
    
    for i, server in enumerate(servers):
        color = colors[i % len(colors)]  # Циклически используем цвета
        ping_result = ping_server(server, attempts, timeout)
        
        if ping_result is not None:
            result_str = colorize_text(f"{server}: {ping_result:.1f}ms", color)
            results.append(result_str)
            successful_pings.append(ping_result)
        else:
            result_str = colorize_text(f"{server}: timeout", 'red')
            results.append(result_str)
    
    # Форматируем вывод
    if successful_pings:
        avg_ping = statistics.mean(successful_pings)
        avg_str = colorize_text(f"Avg: {avg_ping:.1f}ms", 'white')
        
        detailed = " | ".join(results)
        short = f"{len(successful_pings)}/{len(servers)} servers: {avg_ping:.1f}ms"
        
        return {
            'detailed': f"{detailed} | {avg_str}",
            'short': short,
            'average': f"{avg_ping:.1f}ms"
        }
    else:
        return {
            'detailed': colorize_text("All servers timeout", 'red'),
            'short': colorize_text("All timeout", 'red'),
            'average': colorize_text("timeout", 'red')
        }

def register():
    """Функция регистрации плагина"""
    results = get_multi_ping_results()
    
    return {
        'mping': results['detailed'],
        'mping_short': results['short'],
        'mping_avg': results['average']
    }
