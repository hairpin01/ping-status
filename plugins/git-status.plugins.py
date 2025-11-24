#!/usr/bin/env python3
# Метаданные плагина для автоматического обновления
__plugin_url__ = "https://raw.githubusercontent.com/hairpin01/ping-status/refs/heads/main/plugins/git-status.plugin.py"
__name__ = "git-status"
__last_updated__ = "2025-11-24 10:01:00"
__version__ = "1.0.0"
__min_version__ = "3.3.0"

import os
import subprocess
import configparser
from pathlib import Path

def get_help():
    return """
Git Status Plugin v1.0.0
========================

Показывает статус Git репозиториев в текущей директории.

Placeholders:
{git_status}     - Статус текущего Git репозитория
{git_branch}     - Текущая ветка
{git_commits}    - Количество коммитов для пуша/пулла
{git_changes}    - Измененные файлы
{git_repo_name}  - Название репозитория

Configuration:
Добавьте в конфиг:

[git-status]
# Показывать подробную информацию (true/false)
detailed = true

# Максимальная глубина поиска репозиториев (уровни вложенности)
max_depth = 3

# Автоматически искать репозитории в родительских директориях
auto_find = true

# Показывать иконки статуса
show_icons = true

# Цвета для разных статусов
color_clean = green
color_dirty = yellow
color_unpushed = red
color_no_repo = white

Примеры использования:
{git_status} - "🌿 main ±2 🚀+1" (ветка, изменения, коммиты для пуша)
{git_branch} - "main"
{git_commits} - "🚀+1" (коммиты для пуша)
"""

def get_git_config():
    """Получить конфигурацию плагина"""
    config_path = Path.home() / '.config' / 'ping-status.conf'
    
    if not config_path.exists():
        config_path = Path('/etc/ping-status.conf')
    
    config = configparser.ConfigParser()
    config.read(config_path)
    
    return {
        'detailed': config.getboolean('git-status', 'detailed', fallback=True),
        'max_depth': config.getint('git-status', 'max_depth', fallback=3),
        'auto_find': config.getboolean('git-status', 'auto_find', fallback=True),
        'show_icons': config.getboolean('git-status', 'show_icons', fallback=True),
        'color_clean': config.get('git-status', 'color_clean', fallback='green'),
        'color_dirty': config.get('git-status', 'color_dirty', fallback='yellow'),
        'color_unpushed': config.get('git-status', 'color_unpushed', fallback='red'),
        'color_no_repo': config.get('git-status', 'color_no_repo', fallback='white')
    }

def find_git_repo():
    """Найти Git репозиторий в текущей или родительских директориях"""
    config = get_git_config()
    current_path = Path.cwd()
    max_depth = config['max_depth']
    
    for depth in range(max_depth + 1):
        check_path = current_path
        for _ in range(depth):
            check_path = check_path.parent
            
        git_path = check_path / '.git'
        if git_path.exists():
            return check_path
    
    return None

def run_git_command(repo_path, command):
    """Выполнить Git команду и вернуть результат"""
    try:
        result = subprocess.run(
            ['git'] + command,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except:
        return None

def get_git_branch(repo_path):
    """Получить текущую ветку"""
    branch = run_git_command(repo_path, ['branch', '--show-current'])
    if not branch:
        # Попробуем другой способ
        head_ref = run_git_command(repo_path, ['symbolic-ref', '--short', 'HEAD'])
        return head_ref or "detached"
    return branch

def get_git_status(repo_path):
    """Получить статус Git"""
    status_output = run_git_command(repo_path, ['status', '--porcelain'])
    return status_output

def get_unpushed_commits(repo_path, branch):
    """Получить количество неотправленных коммитов"""
    if branch == "detached":
        return 0
    
    # Коммиты для пуша
    push_count = run_git_command(repo_path, ['rev-list', '--count', f'{branch}@{{u}}..{branch}'])
    # Коммиты для пулла
    pull_count = run_git_command(repo_path, ['rev-list', '--count', f'{branch}..{branch}@{{u}}'])
    
    return {
        'push': int(push_count) if push_count else 0,
        'pull': int(pull_count) if pull_count else 0
    }

def get_remote_url(repo_path):
    """Получить URL удаленного репозитория"""
    remote = run_git_command(repo_path, ['remote', 'get-url', 'origin'])
    if remote:
        # Извлекаем имя репозитория из URL
        if '/' in remote:
            repo_name = remote.split('/')[-1]
            if repo_name.endswith('.git'):
                repo_name = repo_name[:-4]
            return repo_name
    return None

def colorize_text(text, color):
    """Цветовой вывод текста"""
    colors = {
        'black': '30',
        'red': '31',
        'green': '32',
        'yellow': '33',
        'blue': '34',
        'magenta': '35',
        'cyan': '36',
        'white': '37'
    }
    color_code = colors.get(color.lower(), '37')
    return f'\033[{color_code}m{text}\033[0m'

def format_git_output(repo_path, config):
    """Форматировать вывод Git статуса"""
    if not repo_path:
        no_repo_msg = "No Git repo"
        if config['show_icons']:
            no_repo_msg = "❌ " + no_repo_msg
        return {
            'git_status': colorize_text(no_repo_msg, config['color_no_repo']),
            'git_branch': "",
            'git_commits': "",
            'git_changes': "",
            'git_repo_name': ""
        }
    
    branch = get_git_branch(repo_path)
    status = get_git_status(repo_path)
    unpushed = get_unpushed_commits(repo_path, branch)
    repo_name = get_remote_url(repo_path) or repo_path.name
    
    # Определяем статус
    has_changes = bool(status)
    has_unpushed = unpushed['push'] > 0
    has_unpulled = unpushed['pull'] > 0
    
    # Выбираем цвет на основе статуса
    if has_unpushed:
        status_color = config['color_unpushed']
    elif has_changes:
        status_color = config['color_dirty']
    else:
        status_color = config['color_clean']
    
    # Форматируем вывод
    icons = config['show_icons']
    
    # Основной статус
    status_parts = []
    if icons:
        status_parts.append("🌿")
    status_parts.append(branch)
    
    if has_changes:
        change_count = len(status.split('\n'))
        status_parts.append(f"±{change_count}")
    
    commit_parts = []
    if unpushed['push'] > 0:
        if icons:
            commit_parts.append(f"🚀+{unpushed['push']}")
        else:
            commit_parts.append(f"↑{unpushed['push']}")
    
    if unpushed['pull'] > 0:
        if icons:
            commit_parts.append(f"📥+{unpushed['pull']}")
        else:
            commit_parts.append(f"↓{unpushed['pull']}")
    
    if commit_parts:
        status_parts.extend(commit_parts)
    
    git_status = " ".join(status_parts)
    
    # Детальная информация
    if config['detailed']:
        changes_info = []
        if status:
            file_stats = {'M': 0, 'A': 0, 'D': 0, 'R': 0, '?': 0}
            for line in status.split('\n'):
                if line:
                    status_code = line[:2].strip()
                    if status_code:
                        first_char = status_code[0]
                        if first_char in file_stats:
                            file_stats[first_char] += 1
            
            change_parts = []
            if file_stats['M'] > 0:
                change_parts.append(f"M:{file_stats['M']}")
            if file_stats['A'] > 0:
                change_parts.append(f"A:{file_stats['A']}")
            if file_stats['D'] > 0:
                change_parts.append(f"D:{file_stats['D']}")
            if file_stats['?'] > 0:
                change_parts.append(f"?:{file_stats['?']}")
            
            changes_info = " ".join(change_parts)
        else:
            changes_info = "clean"
        
        git_changes = changes_info
    else:
        git_changes = "±" + str(len(status.split('\n'))) if status else "clean"
    
    # Коммиты для пуша/пулла
    commits_info = []
    if unpushed['push'] > 0:
        commits_info.append(f"push+{unpushed['push']}")
    if unpushed['pull'] > 0:
        commits_info.append(f"pull+{unpushed['pull']}")
    git_commits = " ".join(commits_info) if commits_info else "synced"
    
    return {
        'git_status': colorize_text(git_status, status_color),
        'git_branch': branch,
        'git_commits': git_commits,
        'git_changes': git_changes,
        'git_repo_name': repo_name
    }

def register():
    """Функция регистрации плагина"""
    try:
        config = get_git_config()
        repo_path = find_git_repo()
        return format_git_output(repo_path, config)
    except Exception as e:
        return {
            'git_status': f"Git error: {str(e)}",
            'git_branch': "error",
            'git_commits': "error",
            'git_changes': "error",
            'git_repo_name': "error"
        }