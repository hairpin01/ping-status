#!/usr/bin/env python3

import psutil
__min_version__ = "3.3.0"

def get_help():
    return """
CPU Bar Plugin
==============

Shows CPU usage as a progress bar.

Available Placeholders:
{cpu_bar} - CPU usage bar (20 characters)
"""

def create_bar(percentage, width=20):
    filled = int(round(percentage / 100 * width))
    bar = '█' * filled + '░' * (width - filled)
    return bar

def register():
    cpu_percent = psutil.cpu_percent(interval=0.1)
    return {
        'cpu_bar': create_bar(cpu_percent)
    }
