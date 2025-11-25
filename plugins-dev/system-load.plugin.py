#!/usr/bin/env python3
# Метаданные плагина
__plugin_url__ = "https://raw.githubusercontent.com/hairpin01/ping-status/refs/heads/main/plugins-dev/system-load.plugin.py"
__name__ = "system-load"
__last_updated__ = "2025-11-25 18:16:00"
__version__ = "1.0.0"
__min_version__ = "3.3.0"

import os
import psutil
import multiprocessing

def get_help():
    return """
System Load Plugin v1.0.0
=========================

Показывает загрузку системы и температуру (если доступно).

Placeholders:
{system_load} - Сводка по загрузке системы
{load_avg} - Средняя загрузка системы (1min, 5min, 15min)
{cpu_cores} - Количество ядер CPU
{memory_usage} - Использование памяти
{swap_usage} - Использование swap
{temperature} - Температура CPU

Configuration:
Добавьте в конфиг:
[system-load]
# Показывать температуру (true/false)
show_temperature = true
# Показывать swap (true/false)  
show_swap = true
"""

def get_temperature():
    """Получить температуру CPU"""
    try:
        if hasattr(psutil, "sensors_temperatures"):
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                # Для Intel CPU
                return max([temp.current for temp in temps['coretemp']])
            elif 'cpu_thermal' in temps:
                # Для Raspberry Pi
                return temps['cpu_thermal'][0].current
        return None
    except:
        return None

def get_plugin_config():
    """Получить конфигурацию плагина"""
    from configparser import ConfigParser
    
    config_path = Path.home() / '.config' / 'ping-status.conf'
    if not config_path.exists():
        config_path = Path('/etc/ping-status.conf')
    
    config = ConfigParser()
    config.read(config_path)
    
    return {
        'show_temperature': config.getboolean('system-load', 'show_temperature', fallback=True),
        'show_swap': config.getboolean('system-load', 'show_swap', fallback=True)
    }

def register():
    """Функция регистрации плагина"""
    try:
        config = get_plugin_config()
        
        # Загрузка CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        load_avg = os.getloadavg()
        
        # Память
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_gb = memory.used / (1024**3)
        memory_total_gb = memory.total / (1024**3)
        
        # Swap
        swap = psutil.swap_memory()
        swap_percent = swap.percent
        
        # Температура
        temp = get_temperature()
        
        # Форматируем вывод
        load_avg_str = f"{load_avg[0]:.1f}/{load_avg[1]:.1f}/{load_avg[2]:.1f}"
        memory_str = f"{memory_percent:.0f}% ({memory_used_gb:.1f}GB/{memory_total_gb:.1f}GB)"
        
        # Собираем сводку
        parts = [
            f"🔥 CPU: {cpu_percent:.0f}%",
            f"📊 Load: {load_avg_str}"
        ]
        
        if config['show_temperature'] and temp:
            parts.append(f"🌡️ {temp:.0f}°C")
            
        parts.append(f"💾 RAM: {memory_str}")
        
        if config['show_swap'] and swap.total > 0:
            parts.append(f"💿 Swap: {swap_percent:.0f}%")
        
        cpu_cores = multiprocessing.cpu_count()
        
        return {
            'system_load': " | ".join(parts),
            'load_avg': load_avg_str,
            'cpu_cores': str(cpu_cores),
            'memory_usage': f"{memory_percent:.0f}%",
            'swap_usage': f"{swap_percent:.0f}%" if swap.total > 0 else "N/A",
            'temperature': f"{temp:.0f}°C" if temp else "N/A"
        }
        
    except Exception as e:
        return {
            'system_load': "System: Error",
            'load_avg': "N/A",
            'cpu_cores': "N/A",
            'memory_usage': "N/A",
            'swap_usage': "N/A",
            'temperature': "N/A"
        }
