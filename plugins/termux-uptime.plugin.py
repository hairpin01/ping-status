#!/usr/bin/env python3
__plugin_url__ = "https://raw.githubusercontent.com/hairpin01/ping-status/refs/heads/main/plugins/termux-uptime.plugin.py"
__name__ = "termux-uptime"
__last_updated__ = "2025-11-24 1:17:00"
__version__ = "1.0.0"
__min_version__ = "3.3.0"

import os
import time
import subprocess
from pathlib import Path

def get_help():
    return """
Termux Uptime Plugin v1.0.0
===========================

Альтернативный способ получения времени работы системы для Termux.

Placeholders:
{tuptime} - Время работы системы (аналог uptime для Termux)
{tsession} - Время работы текущей сессии Termux
{tbattery} - Информация о батарее (если доступно)

Особенности:
- Работает в Termux без root прав
- Использует альтернативные методы получения uptime
- Показывает время сессии и батарею
"""

def get_termux_uptime():
    """Получить время работы системы для Termux"""
    try:
        # Способ 1: Через procfs (если доступно)
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                return format_uptime(uptime_seconds)
        except:
            pass
        
        # Способ 2: Через системные свойства Android
        try:
            result = subprocess.run(['getprop', 'sys.boot_completed'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and '1' in result.stdout:
                # Пытаемся получить время загрузки через dmesg
                result = subprocess.run(['dmesg'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'BOOT_COMPLETED' in line or 'boot_complete' in line:
                            # Парсим время из dmesg
                            import re
                            time_match = re.search(r'\[\s*(\d+\.\d+)\]', line)
                            if time_match:
                                boot_time = float(time_match.group(1))
                                current_time = time.time()
                                uptime_seconds = current_time - boot_time
                                return format_uptime(uptime_seconds)
        except:
            pass
        
        # Способ 3: Через статистику системы
        try:
            result = subprocess.run(['cat', '/proc/stat'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.startswith('btime'):
                        boot_timestamp = int(line.split()[1])
                        current_timestamp = time.time()
                        uptime_seconds = current_timestamp - boot_timestamp
                        return format_uptime(uptime_seconds)
        except:
            pass
        
        # Способ 4: Время с момента установки Termux (приблизительно)
        try:
            termux_dir = Path('/data/data/com.termux/files/home')
            if termux_dir.exists():
                install_time = termux_dir.stat().st_mtime
                current_time = time.time()
                uptime_seconds = current_time - install_time
                return f"~{format_uptime(uptime_seconds)}"
        except:
            pass
        
        return "unknown"
        
    except Exception as e:
        return f"error: {str(e)}"

def get_termux_session():
    """Получить время текущей сессии Termux"""
    try:
        # Время с момента запуска shell процесса
        pid = os.getppid()  # Родительский процесс (shell)
        try:
            # Читаем время начала процесса из /proc
            with open(f'/proc/{pid}/stat', 'r') as f:
                stat_data = f.read().split()
                # Время начала процесса в clock ticks
                start_time_ticks = int(stat_data[21])
                # Получаем clock ticks per second
                clock_ticks = os.sysconf(os.sysconf_names['SC_CLK_TCK'])
                # Получаем время загрузки системы
                with open('/proc/stat', 'r') as stat_file:
                    for line in stat_file:
                        if line.startswith('btime'):
                            boot_time = int(line.split()[1])
                            break
                # Вычисляем время начала процесса
                start_time = boot_time + (start_time_ticks / clock_ticks)
                current_time = time.time()
                session_seconds = current_time - start_time
                return format_uptime(session_seconds)
        except:
            # Альтернативный способ: время создания домашней директории сессии
            home_dir = Path.home()
            session_start = home_dir.stat().st_atime
            current_time = time.time()
            session_seconds = current_time - session_start
            return f"~{format_uptime(session_seconds)}"
            
    except Exception as e:
        return "unknown"

def get_battery_info():
    """Получить информацию о батарее Android"""
    try:
        # Способ 1: Через системные свойства
        result = subprocess.run(['dumpsys', 'battery'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            battery_info = {}
            for line in result.stdout.split('\n'):
                if 'level' in line.lower():
                    battery_info['level'] = line.split(':')[1].strip()
                elif 'scale' in line.lower():
                    battery_info['scale'] = line.split(':')[1].strip()
                elif 'status' in line.lower() or 'charging' in line.lower():
                    battery_info['status'] = line.split(':')[1].strip()
            
            if 'level' in battery_info:
                level = battery_info['level']
                status = battery_info.get('status', '')
                
                # Определяем иконку статуса
                if 'charging' in status.lower() or 'ac' in status.lower():
                    icon = '🔌'
                elif 'full' in status.lower():
                    icon = '✅'
                else:
                    icon = '🔋'
                
                return f"{icon} {level}%"
        
        # Способ 2: Через файловую систему
        try:
            battery_path = Path('/sys/class/power_supply/battery/')
            if battery_path.exists():
                capacity_file = battery_path / 'capacity'
                status_file = battery_path / 'status'
                
                if capacity_file.exists():
                    with open(capacity_file, 'r') as f:
                        level = f.read().strip()
                    
                    status = "unknown"
                    if status_file.exists():
                        with open(status_file, 'r') as f:
                            status = f.read().strip().lower()
                    
                    if 'charging' in status:
                        icon = '🔌'
                    elif 'full' in status:
                        icon = '✅'
                    else:
                        icon = '🔋'
                    
                    return f"{icon} {level}%"
        except:
            pass
            
        return "🔋 N/A"
        
    except Exception as e:
        return "🔋 error"

def format_uptime(seconds):
    """Форматировать время в читаемый вид"""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"

def register():
    """Функция регистрации плагина"""
    try:
        return {
            'tuptime': get_termux_uptime(),
            'tsession': get_termux_session(),
            'tbattery': get_battery_info()
        }
    except Exception as e:
        return {
            'tuptime': f"error: {str(e)}",
            'tsession': "unknown",
            'tbattery': "🔋 N/A"
        }