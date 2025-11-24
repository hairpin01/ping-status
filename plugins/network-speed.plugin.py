#!/usr/bin/env python3

__plugin_url__ = "https://raw.githubusercontent.com/hairpin01/ping-status/refs/heads/main/plugins/network-speed.plugin.py"
__name__ = "network-speed"
__last_updated__ = "2025-11-24 10:49:00"
__version__ = "1.0.0"
__min_version__ = "3.3.0"

import psutil
import time
import threading
from pathlib import Path
import json

def get_help():
    return """
Network Speed Plugin v1.0.0
============================

Показывает текущую скорость сети (загрузка/отдача) в реальном времени.

Placeholders:
{net_speed}        - Текущая скорость загрузки и отдачи
{download_speed}   - Скорость загрузки
{upload_speed}     - Скорость отдачи
{network_usage}    - Использование сети за сессию
{network_interface} - Активный сетевой интерфейс

Configuration:
Добавьте в конфиг:
[network-speed]
# Интервал обновления в секундах (по умолчанию: 2)
interval = 2
# Единицы измерения (mbps, kbps, B/s) 
units = mbps
# Показывать иконки (true/false)
show_icons = true
# Интерфейс для мониторинга (auto для автоматического выбора)
interface = auto
"""

class NetworkSpeedMonitor:
    def __init__(self):
        self.download_speed = 0
        self.upload_speed = 0
        self.total_download = 0
        self.total_upload = 0
        self.last_download = 0
        self.last_upload = 0
        self.last_time = time.time()
        self.running = False
        self.thread = None
        self.interface = self.get_active_interface()
        
    def get_active_interface(self):
        """Определить активный сетевой интерфейс"""
        try:
            stats = psutil.net_io_counters(pernic=True)
            for interface, data in stats.items():
                # Исключаем виртуальные и локальные интерфейсы
                if (interface.startswith(('eth', 'wlan', 'en', 'wl', 'rmnet')) and 
                    data.bytes_sent + data.bytes_recv > 0):
                    return interface
            return "lo"  # fallback на loopback
        except:
            return "unknown"
    
    def start_monitoring(self, interval=2):
        """Запустить мониторинг сети в отдельном потоке"""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.thread.daemon = True
        self.thread.start()
    
    def stop_monitoring(self):
        """Остановить мониторинг"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
    
    def _monitor_loop(self, interval):
        """Цикл мониторинга сети"""
        # Начальные значения
        try:
            stats = psutil.net_io_counters(pernic=True)
            if self.interface in stats:
                self.last_download = stats[self.interface].bytes_recv
                self.last_upload = stats[self.interface].bytes_sent
            else:
                # Если интерфейс не найден, используем общую статистику
                total_stats = psutil.net_io_counters()
                self.last_download = total_stats.bytes_recv
                self.last_upload = total_stats.bytes_sent
        except:
            self.last_download = 0
            self.last_upload = 0
            
        self.last_time = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                time_diff = current_time - self.last_time
                
                if time_diff > 0:
                    # Получаем текущую статистику
                    try:
                        stats = psutil.net_io_counters(pernic=True)
                        if self.interface in stats and self.interface != "unknown":
                            current_download = stats[self.interface].bytes_recv
                            current_upload = stats[self.interface].bytes_sent
                        else:
                            # Fallback на общую статистику
                            total_stats = psutil.net_io_counters()
                            current_download = total_stats.bytes_recv
                            current_upload = total_stats.bytes_sent
                    except:
                        current_download = 0
                        current_upload = 0
                    
                    # Вычисляем скорость
                    download_diff = current_download - self.last_download
                    upload_diff = current_upload - self.last_upload
                    
                    self.download_speed = download_diff / time_diff
                    self.upload_speed = upload_diff / time_diff
                    
                    # Обновляем общий трафик
                    self.total_download += download_diff
                    self.total_upload += upload_diff
                    
                    # Сохраняем текущие значения для следующего измерения
                    self.last_download = current_download
                    self.last_upload = current_upload
                    self.last_time = current_time
                
                time.sleep(interval)
                
            except Exception as e:
                # В случае ошибки продолжаем работу
                time.sleep(interval)
    
    def format_speed(self, speed_bytes, units="mbps", show_icons=True):
        """Форматировать скорость в читаемый вид"""
        try:
            if units == "mbps":
                speed = (speed_bytes * 8) / 1_000_000  # Мбит/с
                unit_str = "Mbps"
            elif units == "kbps":
                speed = (speed_bytes * 8) / 1_000  # Кбит/с
                unit_str = "Kbps"
            elif units == "B/s":
                speed = speed_bytes  # Байт/с
                if speed >= 1_000_000:
                    speed = speed / 1_000_000
                    unit_str = "MB/s"
                elif speed >= 1_000:
                    speed = speed / 1_000
                    unit_str = "KB/s"
                else:
                    unit_str = "B/s"
            else:
                # Автоматический выбор единиц
                if speed_bytes > 1_000_000:  # > 1 MB/s
                    speed = (speed_bytes * 8) / 1_000_000
                    unit_str = "Mbps"
                elif speed_bytes > 1_000:  # > 1 KB/s
                    speed = (speed_bytes * 8) / 1_000
                    unit_str = "Kbps"
                else:
                    speed = speed_bytes
                    unit_str = "B/s"
            
            icon = "↓" if "download" in inspect.stack()[1].function else "↑"
            
            if show_icons:
                return f"{icon} {speed:.1f} {unit_str}"
            else:
                return f"{speed:.1f} {unit_str}"
                
        except:
            return "N/A"
    
    def format_usage(self):
        """Форматировать общее использование сети"""
        try:
            if self.total_download >= 1_000_000_000:  # GB
                download_usage = self.total_download / 1_000_000_000
                upload_usage = self.total_upload / 1_000_000_000
                return f"↓{download_usage:.1f}GB ↑{upload_usage:.1f}GB"
            elif self.total_download >= 1_000_000:  # MB
                download_usage = self.total_download / 1_000_000
                upload_usage = self.total_upload / 1_000_000
                return f"↓{download_usage:.1f}MB ↑{upload_usage:.1f}MB"
            else:  # KB
                download_usage = self.total_download / 1_000
                upload_usage = self.total_upload / 1_000
                return f"↓{download_usage:.1f}KB ↑{upload_usage:.1f}KB"
        except:
            return "Usage: N/A"

# Глобальный монитор
monitor = NetworkSpeedMonitor()

def get_network_config():
    """Получить конфигурацию плагина"""
    from configparser import ConfigParser
    import os
    
    config_path = Path.home() / '.config' / 'ping-status.conf'
    if not config_path.exists():
        config_path = Path('/etc/ping-status.conf')
    
    config = ConfigParser()
    config.read(config_path)
    
    return {
        'interval': config.getint('network-speed', 'interval', fallback=2),
        'units': config.get('network-speed', 'units', fallback='mbps'),
        'show_icons': config.getboolean('network-speed', 'show_icons', fallback=True),
        'interface': config.get('network-speed', 'interface', fallback='auto')
    }

def register():
    """Функция регистрации плагина"""
    import inspect
    
    config = get_network_config()
    
    # Запускаем мониторинг если еще не запущен
    if not monitor.running:
        monitor.start_monitoring(config['interval'])
    
    # Даем немного времени для сбора данных при первом запуске
    if monitor.last_time == time.time():
        time.sleep(0.5)
    
    try:
        # Форматируем скорости
        download_str = monitor.format_speed(
            monitor.download_speed, 
            config['units'], 
            config['show_icons']
        )
        
        upload_str = monitor.format_speed(
            monitor.upload_speed, 
            config['units'], 
            config['show_icons']
        )
        
        usage_str = monitor.format_usage()
        
        return {
            'net_speed': f"{download_str} {upload_str}",
            'download_speed': download_str,
            'upload_speed': upload_str,
            'network_usage': usage_str,
            'network_interface': monitor.interface
        }
        
    except Exception as e:
        return {
            'net_speed': "Network: N/A",
            'download_speed': "↓ N/A",
            'upload_speed': "↑ N/A", 
            'network_usage': "Usage: N/A",
            'network_interface': "unknown"
        }

# Останавливаем мониторинг при завершении работы
import atexit
atexit.register(monitor.stop_monitoring)