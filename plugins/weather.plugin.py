#!/usr/bin/env python3

import urllib.request
import json
import configparser
from pathlib import Path
__min_version__ = "3.3.0"

def get_help():
    return """
Weather Plugin (Nerd Font Edition)
===================================

Provides weather information using OpenWeatherMap API with Nerd Font icons.

Available Placeholders:
{weather}        - Full weather information with Nerd Font icons
{weather_short}  - Short weather summary

Configuration:
Add to ~/.config/ping-status.conf:

[weather]
api_key = YOUR_API_KEY_HERE   # Get free API key from https://openweathermap.org/api
city = Moscow                 # Your city name
units = metric                # Temperature units: metric, imperial
lang = en                     # Language code: en, ru, etc.

Icons Used:
 - Weather section |  - Temperature |  - Wind |  - Humidity
"""

def get_weather_config():
    """Получить конфигурацию погоды"""
    config_path = Path.home() / '.config' / 'ping-status.conf'
    
    if not config_path.exists():
        config_path = Path('/etc/ping-status.conf')
    
    config = configparser.ConfigParser()
    config.read(config_path)
    
    # Настройки по умолчанию
    city = config.get('weather', 'city', fallback='Moscow')
    api_key = config.get('weather', 'api_key', fallback='')
    units = config.get('weather', 'units', fallback='metric')
    lang = config.get('weather', 'lang', fallback='en')
    
    return {
        'city': city,
        'api_key': api_key,
        'units': units,
        'lang': lang
    }

def get_weather_by_ip():
    """Получить погоду по IP (геолокация)"""
    try:
        # Получить примерную локацию по IP
        location_response = urllib.request.urlopen('http://ip-api.com/json/', timeout=5)
        location_data = json.loads(location_response.read().decode('utf-8'))
        
        city = location_data.get('city', 'Moscow')
        country = location_data.get('countryCode', 'RU')
        
        # Используем wttr.in как fallback
        weather_response = urllib.request.urlopen(f'http://wttr.in/{city}?format=j1', timeout=5)
        weather_data = json.loads(weather_response.read().decode('utf-8'))
        
        current = weather_data['current_condition'][0]
        temp_c = current['temp_C']
        desc = current['weatherDesc'][0]['value']
        humidity = current['humidity']
        wind_speed = current['windspeedKmph']
        
        # Подбор эмодзи по описанию погоды
        weather_icon = get_weather_nerd_icon(desc)
        
        return f"{weather_icon} {temp_c}°C, {desc},  {humidity}%,  {wind_speed}km/h"
        
    except Exception as e:
        return f" Weather unavailable"

def get_weather_openweather():
    """Получить погоду через OpenWeatherMap API"""
    config = get_weather_config()
    
    if not config['api_key']:
        return " Configure API key"
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={config['city']}&appid={config['api_key']}&units={config['units']}&lang={config['lang']}"
        
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        description = data['weather'][0]['description']
        wind_speed = data['wind']['speed']
        
        weather_icon = get_weather_nerd_icon(description)
        
        return f"{weather_icon} {temp:.1f}°C (feels {feels_like:.1f}°C), {description},  {humidity}%,  {wind_speed}m/s"
        
    except Exception as e:
        return f" API error"

def get_weather_nerd_icon(description):
    """Получить Nerd Font иконку для погоды по описанию"""
    description = description.lower()
    
    if 'sun' in description or 'clear' in description:
        return ''  # nf-fa-sun_o
    elif 'cloud' in description:
        return ''  # nf-fa-cloud
    elif 'rain' in description or 'drizzle' in description:
        return ''  # nf-weather-rain
    elif 'thunder' in description or 'storm' in description:
        return ''  # nf-fa-bolt
    elif 'snow' in description:
        return ''  # nf-fa-snowflake_o
    elif 'fog' in description or 'mist' in description:
        return ''  # nf-fa-eye_slash
    elif 'wind' in description:
        return ''  # nf-weather-wind
    elif 'partly' in description:
        return ''  # nf-weather-day_cloudy_high
    else:
        return ''  # nf-fa-circle

def get_weather():
    """Основная функция получения погоды"""
    config = get_weather_config()
    
    # Если есть API ключ, используем OpenWeatherMap
    if config['api_key']:
        return get_weather_openweather()
    else:
        # Иначе используем метод по IP
        return get_weather_by_ip()

def register():
    """Функция регистрации плагина"""
    weather_data = get_weather()
    return {
        'weather': weather_data,
        'weather_short': f" {weather_data[:25]}..." if len(weather_data) > 25 else f" {weather_data}"
    }
