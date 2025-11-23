#!/usr/bin/env python3

import subprocess
import os
from datetime import datetime

def get_cpu_usage():
    """Получить загрузку CPU"""
    try:
        with open('/proc/stat', 'r') as f:
            lines = f.readlines()
        for line in lines:
            if line.startswith('cpu '):
                values = line.split()
                total = sum(int(x) for x in values[1:])
                idle = int(values[4])
                usage = 100 - (idle * 100 / total)
                return f"{usage:.1f}%"
    except:
        return "unknown"

def get_cpu_temperature():
    """Получить температуру CPU"""
    try:
        # Попробуем разные пути к файлам температуры
        temp_paths = [
            '/sys/class/thermal/thermal_zone0/temp',
            '/sys/class/hwmon/hwmon0/temp1_input',
            '/sys/class/hwmon/hwmon1/temp1_input'
        ]
        
        for path in temp_paths:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    temp = int(f.read().strip())
                    return f"{temp / 1000:.1f}°C"
        return "unknown"
    except:
        return "unknown"

def get_memory_usage():
    """Получить использование памяти"""
    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
        meminfo = {}
        for line in lines:
            key, value = line.split(':', 1)
            meminfo[key.strip()] = value.strip().split(' ')[0]
        
        total = int(meminfo['MemTotal'])
        available = int(meminfo.get('MemAvailable', meminfo.get('MemFree', '0')))
        used = total - available
        usage_percent = (used / total) * 100
        return {
            'used_mb': used // 1024,
            'total_mb': total // 1024,
            'percent': usage_percent
        }
    except:
        return {'used_mb': 0, 'total_mb': 0, 'percent': 0}

def get_disk_usage():
    """Получить использование диска"""
    try:
        result = subprocess.run(['df', '/', '-h'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        if len(lines) > 1:
            values = lines[1].split()
            return {
                'used': values[2],
                'total': values[1],
                'percent': values[4]
            }
        return {'used': '0', 'total': '0', 'percent': '0%'}
    except:
        return {'used': '0', 'total': '0', 'percent': '0%'}

def get_swap_usage():
    """Получить использование swap"""
    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
        meminfo = {}
        for line in lines:
            key, value = line.split(':', 1)
            meminfo[key.strip()] = value.strip().split(' ')[0]
        
        swap_total = int(meminfo.get('SwapTotal', 0))
        swap_free = int(meminfo.get('SwapFree', 0))
        
        if swap_total > 0:
            swap_used = swap_total - swap_free
            swap_percent = (swap_used / swap_total) * 100
            return {
                'used_mb': swap_used // 1024,
                'total_mb': swap_total // 1024,
                'percent': swap_percent
            }
        return {'used_mb': 0, 'total_mb': 0, 'percent': 0}
    except:
        return {'used_mb': 0, 'total_mb': 0, 'percent': 0}

def get_load_average():
    """Получить среднюю нагрузку системы"""
    try:
        with open('/proc/loadavg', 'r') as f:
            loadavg = f.read().strip().split()
        return f"{loadavg[0]}, {loadavg[1]}, {loadavg[2]}"
    except:
        return "unknown"

def get_os_info():
    """Получить информацию об ОС"""
    try:
        if os.path.exists('/etc/os-release'):
            with open('/etc/os-release', 'r') as f:
                lines = f.readlines()
            os_info = {}
            for line in lines:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os_info[key] = value.strip('"')
            return f"{os_info.get('PRETTY_NAME', 'Unknown')}"
        elif os.path.exists('/etc/issue'):
            with open('/etc/issue', 'r') as f:
                return f.read().strip().replace('\\n', '').replace('\\l', '')
        else:
            return "Unknown"
    except:
        return "Unknown"

def get_kernel_version():
    """Получить версию ядра"""
    try:
        result = subprocess.run(['uname', '-r'], capture_output=True, text=True)
        return result.stdout.strip()
    except:
        return "unknown"

def register():
    """Функция регистрации плагина"""
    memory = get_memory_usage()
    disk = get_disk_usage()
    swap = get_swap_usage()
    
    return {
        'cpu_usage': f"🖥️ CPU: {get_cpu_usage()}",
        'cpu_temp': f"🌡️ Temp: {get_cpu_temperature()}",
        'cpu_load': f"📊 Load: {get_load_average()}",
        'memory': f"🧠 RAM: {memory['used_mb']}/{memory['total_mb']}MB ({memory['percent']:.1f}%)",
        'disk': f"💾 Disk: {disk['used']}/{disk['total']} ({disk['percent']})",
        'swap': f"💿 Swap: {swap['used_mb']}/{swap['total_mb']}MB ({swap['percent']:.1f}%)" if swap['total_mb'] > 0 else "💿 Swap: disabled",
        'os': f"🐧 OS: {get_os_info()}",
        'kernel': f"🔧 Kernel: {get_kernel_version()}",
        'system_info': f"🖥️ {get_cpu_usage()} | 🧠 {memory['used_mb']}MB | 💾 {disk['used']}/{disk['total']}"
    }
