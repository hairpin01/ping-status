#!/usr/bin/env python3

import psutil

def get_help():
    return """
Memory Bar Plugin
=================

Shows memory usage as a progress bar.

Available Placeholders:
{memory_bar} - Memory usage bar (20 characters)
"""

def create_bar(percentage, width=20):
    filled = int(round(percentage / 100 * width))
    bar = '█' * filled + '░' * (width - filled)
    return bar

def register():
    memory = psutil.virtual_memory()
    return {
        'memory_bar': create_bar(memory.percent)
    }
