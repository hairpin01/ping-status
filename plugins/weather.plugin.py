#!/usr/bin/env python3

import urllib.request
import json
import configparser
from pathlib import Path

def get_help():
    return """
Weather Plugin
==============

Provides weather information using OpenWeatherMap API or IP-based location fallback.

Available Placeholders:
{weather}        - Full weather information with emojis
{weather_short}  - Short weather summary (first 20 characters)

Configuration:
Add to ~/.config/ping-status.conf:

[weather]
api_key = YOUR_API_KEY_HERE   # Get free API key from https://openweathermap.org/api
city = Moscow                 # Your city name
units = metric                # Temperature units: metric, imperial
lang = en                     # Language code: en, ru, etc.

Fallback Behavior:
- If no API key provided: uses IP-based location with wttr.in service
- If API key provided: uses OpenWeatherMap with more accurate data

Weather Emojis:
☀️ Clear sky    ☁️ Clouds      🌧️ Rain
⛈️ Thunderstorm ❄️ Snow       🌫️ Fog/Mist
💨 Windy       🌈 Other

Examples:
{weather} → ☀️ 22°C (feels 24°C), clear sky, 💧 45%, 💨 3.2m/s
{weather_short} → 🌤️ ☀️ 22°C, clear sky,...
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
        weather_emoji = get_weather_emoji(desc)
        
        return f"{weather_emoji} {temp_c}°C, {desc}, 💧 {humidity}%, 💨 {wind_speed}km/h"
        
    except Exception as e:
        return f"❌ Weather: Failed to get data ({str(e)})"

def get_weather_openweather():
    """Получить погоду через OpenWeatherMap API"""
    config = get_weather_config()
    
    if not config['api_key']:
        return "❌ Weather: API key not configured"
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={config['city']}&appid={config['api_key']}&units={config['units']}&lang={config['lang']}"
        
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        description = data['weather'][0]['description']
        wind_speed = data['wind']['speed']
        
        weather_emoji = get_weather_emoji(description)
        
        return f"{weather_emoji} {temp:.1f}°C (feels {feels_like:.1f}°C), {description}, 💧 {humidity}%, 💨 {wind_speed}m/s"
        
    except Exception as e:
        return f"❌ Weather: API error ({str(e)})"

def get_weather_emoji(description):
    """Получить эмодзи для погоды по описанию"""
    description = description.lower()
    
    if 'sun' in description or 'clear' in description:
        return '☀️'
    elif 'cloud' in description:
        return '☁️'
    elif 'rain' in description or 'drizzle' in description:
        return '🌧️'
    elif 'thunder' in description or 'storm' in description:
        return '⛈️'
    elif 'snow' in description:
        return '❄️'
    elif 'fog' in description or 'mist' in description:
        return '🌫️'
    elif 'wind' in description:
        return '💨'
    else:
        return '🌈'

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
        'weather_short': f"🌤️ {weather_data[:20]}..." if len(weather_data) > 20 else f"🌤️ {weather_data}"
    }
