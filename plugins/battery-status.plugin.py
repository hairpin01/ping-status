#!/usr/bin/env python3
# Метаданные плагина для автоматического обновления
__plugin_url__ = "https://raw.githubusercontent.com/hairpin01/ping-status/refs/heads/main/plugins/battery-status.plugin.py"
__name__ = "battery-status"
__last_updated__ = "2025-11-23 23:37:00"
__version__ = "1.0.0"
__min_version__ = "3.3.0"

import os
from pathlib import Path

def get_help():
    return """
Battery Status Plugin v1.0.0
============================

Показывает состояние батареи ноутбука.

Available Placeholders:
{battery}         - Статус батареи с иконкой и процентом
{battery_level}   - Только уровень заряда в процентах
{battery_status}  - Только статус (Charging/Discharging/Full)
{battery_icon}    - Только иконка состояния
{battery_time}    - Оставшееся время (только для разрядки)

Configuration:
Add to ~/.config/ping-status.conf:

[battery]
# Показывать оставшееся время (true/false)
show_time = true

# Использовать цветовые индикаторы (true/false)  
use_colors = true

# Custom icons (optional)
icon_charging = 🔌
icon_discharging = 🔋  
icon_full = ✅
icon_unknown = ❓

Features:
- Определяет уровень заряда и статус
- Цветовые индикаторы для критического уровня
- Показывает оставшееся время работы
- Простой и легковесный
"""

def get_battery_info():
    """Получить информацию о батарее"""
    battery_path = Path("/sys/class/power_supply/")
    
    if not battery_path.exists():
        return None
    
    # Ищем батареи (BAT0, BAT1, etc)
    batteries = list(battery_path.glob("BAT*"))
    if not batteries:
        return None
    
    # Берем первую найденную батарею
    battery = batteries[0]
    
    try:
        # Читаем уровень заряда
        capacity_file = battery / "capacity"
        if capacity_file.exists():
            with open(capacity_file, 'r') as f:
                capacity = int(f.read().strip())
        else:
            return None
        
        # Читаем статус
        status_file = battery / "status"
        if status_file.exists():
            with open(status_file, 'r') as f:
                status = f.read().strip()
        else:
            status = "Unknown"
        
        # Читаем оставшееся время (если доступно)
        time_file = battery / "time_to_empty"
        time_remaining = None
        if time_file.exists():
            with open(time_file, 'r') as f:
                time_minutes = int(f.read().strip())
                if time_minutes > 0:
                    hours = time_minutes // 60
                    minutes = time_minutes % 60
                    time_remaining = f"{hours}h{minutes}m"
        
        return {
            'capacity': capacity,
            'status': status,
            'time_remaining': time_remaining
        }
        
    except Exception:
        return None

def get_battery_config():
    """Получить конфигурацию плагина"""
    from configparser import ConfigParser
    
    config_path = Path.home() / '.config' / 'ping-status.conf'
    if not config_path.exists():
        config_path = Path('/etc/ping-status.conf')
    
    config = ConfigParser()
    config.read(config_path)
    
    return {
        'show_time': config.getboolean('battery', 'show_time', fallback=True),
        'use_colors': config.getboolean('battery', 'use_colors', fallback=True),
        'icon_charging': config.get('battery', 'icon_charging', fallback='🔌'),
        'icon_discharging': config.get('battery', 'icon_discharging', fallback='🔋'),
        'icon_full': config.get('battery', 'icon_full', fallback='✅'),
        'icon_unknown': config.get('battery', 'icon_unknown', fallback='❓')
    }

def colorize_battery_level(text, capacity):
    """Цветовая индикация уровня батареи"""
    if not isinstance(capacity, int):
        return text
    
    if capacity <= 15:
        color = 'red'
    elif capacity <= 30:
        color = 'yellow'  
    else:
        color = 'green'
    
    # ANSI color codes
    colors = {
        'red': '\033[31m',
        'yellow': '\033[33m', 
        'green': '\033[32m',
        'reset': '\033[0m'
    }
    
    return f"{colors[color]}{text}{colors['reset']}"

def register():
    """Функция регистрации плагина"""
    battery_info = get_battery_info()
    config = get_battery_config()
    
    if not battery_info:
        return {
            'battery': 'No battery',
            'battery_level': 'N/A',
            'battery_status': 'Not available',
            'battery_icon': '🔌',
            'battery_time': 'N/A'
        }
    
    capacity = battery_info['capacity']
    status = battery_info['status']
    time_remaining = battery_info['time_remaining']
    
    # Выбираем иконку по статусу
    icons = {
        'Charging': config['icon_charging'],
        'Discharging': config['icon_discharging'], 
        'Full': config['icon_full'],
        'Unknown': config['icon_unknown']
    }
    
    icon = icons.get(status, config['icon_unknown'])
    
    # Форматируем уровень
    level_text = f"{capacity}%"
    if config['use_colors']:
        level_text = colorize_battery_level(level_text, capacity)
    
    # Форматируем время
    time_text = time_remaining if (time_remaining and config['show_time'] and status == 'Discharging') else ''
    if time_text:
        time_text = f" ({time_text})"
    
    # Основной вывод
    battery_output = f"{icon} {level_text}{time_text}"
    
    # Статус текстом
    status_text = status if status != 'Unknown' else 'Not charging'
    
    return {
        'battery': battery_output,
        'battery_level': level_text,
        'battery_status': status_text,
        'battery_icon': icon,
        'battery_time': time_remaining if time_remaining else 'N/A'
    }
