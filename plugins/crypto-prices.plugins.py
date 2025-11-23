#!/usr/bin/env python3

__min_version__ = "3.3.0"

def get_help():
    return """
Crypto Prices Plugin
====================

Показывает текущие цены криптовалют в реальном времени.

Placeholders:
{crypto_btc} - Цена Bitcoin (BTC) в USD
{crypto_eth} - Цена Ethereum (ETH) в USD
{crypto_sol} - Цена Solana (SOL) в USD
{crypto_doge} - Цена Dogecoin (DOGE) в USD
{crypto_prices} - Сводка по всем криптовалютам

Configuration:
Добавьте в конфиг:

[crypto]
# Основные валюты для отслеживания (через запятую)
coins = btc,eth,sol,doge
# Валюта отображения (usd, eur, rub)
currency = usd
# Показывать изменение цены за 24h
show_change = true
# Символы для роста/падения
up_symbol = 🟢
down_symbol = 🔴
# Обновлять каждые X минут (кеширование)
cache_minutes = 5

Пример использования в шаблоне:
{crypto_btc} - покажет: "₿ $45,231.50 🟢+2.3%"
{crypto_prices} - покажет таблицу с ценами
"""

def register():
    import urllib.request
    import json
    import time
    from pathlib import Path
    import os
    
    def get_crypto_price(coin_id, currency='usd'):
        """Получить цену криптовалюты с кешированием"""
        cache_file = Path.home() / '.cache' / 'ping-status' / 'crypto_prices.json'
        cache_file.parent.mkdir(exist_ok=True)
        
        # Проверяем кеш
        if cache_file.exists():
            cache_data = json.loads(cache_file.read_text())
            cache_time = cache_data.get('timestamp', 0)
            if time.time() - cache_time < 300:  # 5 минут кеш
                return cache_data.get(coin_id, {}).get(currency)
        
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies={currency}&include_24hr_change=true"
            
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                # Сохраняем в кеш
                cache_data = {'timestamp': time.time()}
                cache_data[coin_id] = data.get(coin_id, {})
                cache_file.write_text(json.dumps(cache_data))
                
                return data.get(coin_id, {})
                
        except Exception as e:
            print(f"❌ Crypto API error: {e}")
            return None
    
    def format_crypto_display(coin_data, coin_symbol, currency='usd'):
        """Форматировать отображение цены"""
        if not coin_data:
            return f"{coin_symbol} N/A"
        
        price = coin_data.get(currency, 0)
        change_24h = coin_data.get(f'{currency}_24h_change', 0)
        
        # Форматируем цену
        if price > 1000:
            formatted_price = f"${price:,.0f}"
        elif price > 1:
            formatted_price = f"${price:,.2f}"
        else:
            formatted_price = f"${price:.4f}"
        
        # Определяем символ изменения
        config = get_config()
        up_sym = config.get('up_symbol', '🟢')
        down_sym = config.get('down_symbol', '🔴')
        
        change_symbol = up_sym if change_24h >= 0 else down_sym
        change_text = f"{change_symbol}{change_24h:+.1f}%" if config.get('show_change', 'true').lower() == 'true' else ""
        
        return f"{coin_symbol} {formatted_price} {change_text}".strip()
    
    def get_config():
        """Получить конфигурацию плагина"""
        from configparser import ConfigParser
        import os
        
        config_path = Path.home() / '.config' / 'ping-status.conf'
        if not config_path.exists():
            config_path = Path('/etc/ping-status.conf')
        
        config = ConfigParser()
        config.read(config_path)
        
        return {
            'coins': config.get('crypto', 'coins', fallback='btc,eth,sol,doge').split(','),
            'currency': config.get('crypto', 'currency', fallback='usd'),
            'show_change': config.get('crypto', 'show_change', fallback='true'),
            'up_symbol': config.get('crypto', 'up_symbol', fallback='🟢'),
            'down_symbol': config.get('crypto', 'down_symbol', fallback='🔴')
        }
    
    def create_prices_table():
        """Создать таблицу с ценами всех криптовалют"""
        config = get_config()
        coins_data = {}
        
        coin_symbols = {
            'btc': '₿',
            'eth': 'Ξ', 
            'sol': '◎',
            'doge': 'Ð',
            'ada': '₳',
            'dot': '●',
            'matic': '⬡',
            'avax': '🅰',
            'xrp': '✕'
        }
        
        coin_names = {
            'btc': 'bitcoin',
            'eth': 'ethereum',
            'sol': 'solana',
            'doge': 'dogecoin',
            'ada': 'cardano',
            'dot': 'polkadot',
            'matic': 'matic-network',
            'avax': 'avalanche-2',
            'xrp': 'ripple'
        }
        
        for coin in config['coins']:
            coin = coin.strip()
            if coin in coin_names:
                data = get_crypto_price(coin_names[coin], config['currency'])
                if data:
                    coins_data[coin] = data
        
        if not coins_data:
            return "📊 No crypto data"
        
        lines = []
        for coin in config['coins']:
            coin = coin.strip()
            if coin in coins_data and coin in coin_symbols:
                symbol = coin_symbols[coin]
                display = format_crypto_display(coins_data[coin], symbol, config['currency'])
                lines.append(display)
        
        return " | ".join(lines) if len(lines) <= 3 else "\n".join(lines)
    
    # Получаем данные для каждой криптовалюты
    config = get_config()
    result = {}
    
    # Основные криптовалюты
    crypto_map = {
        'btc': ('bitcoin', '₿'),
        'eth': ('ethereum', 'Ξ'),
        'sol': ('solana', '◎'),
        'doge': ('dogecoin', 'Ð'),
        'ada': ('cardano', '₳'),
        'dot': ('polkadot', '●')
    }
    
    for coin in config['coins']:
        coin = coin.strip()
        if coin in crypto_map:
            coin_id, symbol = crypto_map[coin]
            data = get_crypto_price(coin_id, config['currency'])
            if data:
                result[f'crypto_{coin}'] = format_crypto_display(data, symbol, config['currency'])
    
    # Сводная информация
    result['crypto_prices'] = create_prices_table()
    
    return result
