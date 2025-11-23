#!/usr/bin/env python3

import subprocess
import os
import re

def get_help():
    return """
System Info Plugin (Nerd Font Edition)
=======================================

Provides comprehensive system metrics with Nerd Font icons.

Available Placeholders:
{system_info}    - Compact summary with icons
{cpu_usage}      - CPU usage with Nerd Font icon
{cpu_temp}       - CPU temperature with Nerd Font icon  
{cpu_load}       - System load average with Nerd Font icon
{memory}         - Memory usage with Nerd Font icon
{disk}           - Disk usage with Nerd Font icon
{swap}           - Swap usage with Nerd Font icon
{os}             - Operating system information
{kernel}         - Kernel version

Configuration:
No configuration required. Plugin automatically detects system metrics.

Icons Used:
 - CPU |  - Temperature |  - RAM |  - Disk |  - OS
"""

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
        temp_paths = [
            '/sys/class/thermal/thermal_zone0/temp',
            '/sys/class/hwmon/hwmon0/temp1_input',
            '/sys/class/hwmon/hwmon1/temp1_input',
            '/sys/class/hwmon/hwmon2/temp1_input'
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
            
            name = os_info.get('PRETTY_NAME', os_info.get('NAME', 'Unknown'))
            # Укорачиваем длинные названия
            if 'Arch Linux' in name:
                return "Arch Linux"
            elif 'Ubuntu' in name:
                return "Ubuntu"
            elif 'Debian' in name:
                return "Debian"
            elif 'Fedora' in name:
                return "Fedora"
            else:
                return name.split()[0] if ' ' in name else name
                
        elif os.path.exists('/etc/issue'):
            with open('/etc/issue', 'r') as f:
                return f.read().strip().replace('\\n', '').replace('\\l', '')[:15]
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

def get_gpu_info():
    """Получить информацию о GPU"""
    try:
        # Попробуем получить информацию о GPU
        if shutil.which('nvidia-smi'):
            result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                gpu_name = result.stdout.strip().split('\n')[0]
                return gpu_name.split()[-1]  # Берем последнее слово (обычно модель)
        
        # Для интегрированной графики
        result = subprocess.run(['lspci'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'VGA' in line or '3D' in line:
                if 'NVIDIA' in line:
                    return "NVIDIA"
                elif 'AMD' in line:
                    return "AMD"
                elif 'Intel' in line:
                    return "Intel"
        return "Integrated"
    except:
        return "unknown"

def register():
    """Функция регистрации плагина"""
    memory = get_memory_usage()
    disk = get_disk_usage()
    swap = get_swap_usage()
    
    cpu_usage = get_cpu_usage()
    cpu_temp = get_cpu_temperature()
    
    # Форматируем вывод для компактного отображения
    memory_str = f"{memory['used_mb']}/{memory['total_mb']}MB ({memory['percent']:.1f}%)"
    disk_str = f"{disk['used']}/{disk['total']} ({disk['percent']})"
    
    return {
        'cpu_usage': f"{cpu_usage}",
        'cpu_temp': f"{cpu_temp}",
        'cpu_load': f" {get_load_average()}",
        'memory': f"{memory_str}",
        'disk': f"{disk_str}",
        'swap': f" {swap['used_mb']}/{swap['total_mb']}MB" if swap['total_mb'] > 0 else " disabled",
        'os': f"{get_os_info()}",
        'kernel': f" {get_kernel_version()}",
        'system_info': f" {cpu_usage} |  {memory['used_mb']}MB |  {disk['used']}/{disk['total']}",
        'gpu': f" {get_gpu_info()}"
    }
