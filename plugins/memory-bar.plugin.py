#!/usr/bin/env python3

import psutil
__min_version__ = "3.3.0"

def get_help():
    return """
Memory Bar Plugin
=================

Shows memory usage as a progress bar with percentage.

Available Placeholders:
{memory_bar} - Memory usage bar (20 characters)
{memory_percent} - Memory usage percentage
"""

def create_bar(percentage, width=20):
    filled = int(round(percentage / 100 * width))
    bar = '█' * filled + '░' * (width - filled)
    return bar

def register():
    memory = psutil.virtual_memory()
    return {
        'memory_bar': create_bar(memory.percent),
        'memory_percent': f"{memory.percent:.1f}"
    }
