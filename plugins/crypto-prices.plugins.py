#!/usr/bin/env python3

__min_version__ = "3.3.0"
__version__ = "1.0.1"
__plugin_url__ = "https://raw.githubusercontent.com/hairpin01/ping-status/refs/heads/main/plugins/crypto-prices.plugins.py"
__name__ = "crypto-prices"
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
{crypto_ada} - Цена Cardano (ADA) в USD
{crypto_dot} - Цена Polkadot (DOT) в USD
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

Пример использования в шаблоне:
{crypto_btc} - покажет: "₿ $45,231.50 🟢+2.3%"
{crypto_prices} - покажет таблицу с ценами
"""

def register():
    import urllib.request
    import json
    import time
    from pathlib import Path
    
    def get_crypto_price(coin_id, currency='usd'):
        """Получить цену криптовалюты с кешированием"""
        cache_file = Path.home() / '.cache' / 'ping-status' / 'crypto_prices.json'
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Проверяем кеш
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                cache_time = cache_data.get('timestamp', 0)
                if time.time() - cache_time < 300:  # 5 минут кеш
                    return cache_data.get(coin_id, {})
            except:
                pass
        
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies={currency}&include_24hr_change=true"
            
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                # Сохраняем в кеш
                cache_data = {'timestamp': time.time()}
                cache_data.update(data)
                with open(cache_file, 'w') as f:
                    json.dump(cache_data, f)
                
                return data.get(coin_id, {})
                
        except Exception as e:
            print(f"❌ Crypto API error: {e}")
            return {}
    
    def get_plugin_config():
        """Получить конфигурацию плагина"""
        from configparser import ConfigParser
        
        config_path = Path.home() / '.config' / 'ping-status.conf'
        if not config_path.exists():
            config_path = Path('/etc/ping-status.conf')
        
        config = ConfigParser()
        config.read(config_path)
        
        crypto_config = {
            'coins': [c.strip() for c in config.get('crypto', 'coins', fallback='btc,eth,sol,doge').split(',')],
            'currency': config.get('crypto', 'currency', fallback='usd'),
            'show_change': config.get('crypto', 'show_change', fallback='true').lower() == 'true',
            'up_symbol': config.get('crypto', 'up_symbol', fallback='🟢'),
            'down_symbol': config.get('crypto', 'down_symbol', fallback='🔴')
        }
        return crypto_config
    
    def format_crypto_display(coin_data, coin_symbol, currency='usd', show_change=True, up_symbol='🟢', down_symbol='🔴'):
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
        change_symbol = up_symbol if change_24h >= 0 else down_symbol
        change_text = f" {change_symbol}{change_24h:+.1f}%" if show_change else ""
        
        return f"{coin_symbol} {formatted_price}{change_text}"
    
    def create_prices_table():
        """Создать таблицу с ценами всех криптовалют"""
        config = get_plugin_config()
        coins_data = {}
        
        coin_symbols = {
            'btc': '₿',
            'eth': 'Ξ', 
            'sol': '◎',
            'doge': 'Ð',
            'ada': '₳',
            'dot': '●'
        }
        
        coin_names = {
            'btc': 'bitcoin',
            'eth': 'ethereum',
            'sol': 'solana',
            'doge': 'dogecoin',
            'ada': 'cardano',
            'dot': 'polkadot'
        }
        
        for coin in config['coins']:
            if coin in coin_names:
                data = get_crypto_price(coin_names[coin], config['currency'])
                if data:
                    coins_data[coin] = data
        
        if not coins_data:
            return "📊 No crypto data"
        
        lines = []
        for coin in config['coins']:
            if coin in coins_data and coin in coin_symbols:
                symbol = coin_symbols[coin]
                display = format_crypto_display(
                    coins_data[coin], 
                    symbol, 
                    config['currency'],
                    config['show_change'],
                    config['up_symbol'],
                    config['down_symbol']
                )
                lines.append(display)
        
        # Если строк мало, объединяем в одну строку
        if len(lines) <= 3:
            return " | ".join(lines)
        else:
            # Иначе разбиваем на несколько строк
            result = []
            for i in range(0, len(lines), 2):
                result.append(" | ".join(lines[i:i+2]))
            return "\n".join(result)
    
    # Получаем конфигурацию
    config = get_plugin_config()
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
    
    # Получаем данные для каждой криптовалюты
    for coin in config['coins']:
        if coin in crypto_map:
            coin_id, symbol = crypto_map[coin]
            data = get_crypto_price(coin_id, config['currency'])
            result[f'crypto_{coin}'] = format_crypto_display(
                data, 
                symbol, 
                config['currency'],
                config['show_change'],
                config['up_symbol'],
                config['down_symbol']
            )
    
    # Сводная информация
    result['crypto_prices'] = create_prices_table()
    
    # Заполняем отсутствующие значения
    for coin in ['btc', 'eth', 'sol', 'doge', 'ada', 'dot']:
        if f'crypto_{coin}' not in result:
            result[f'crypto_{coin}'] = f"{crypto_map.get(coin, ('', '?'))[1]} N/A"
    
    return result
