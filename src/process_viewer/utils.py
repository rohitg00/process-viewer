import psutil
import os

def get_size_str(bytes):
    """Convert bytes to human readable string"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024:
            return f"{bytes:.1f}{unit}"
        bytes /= 1024
    return f"{bytes:.1f}PB"

def get_permissions():
    """Check if we have sufficient permissions"""
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False

def format_time(seconds):
    """Format seconds into readable time string"""
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    
    if days > 0:
        return f"{days}d {hours}h"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def get_system_info():
    """Get system resource information"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    return {
        'cpu_percent': cpu_percent,
        'memory_used': get_size_str(memory.used),
        'memory_total': get_size_str(memory.total),
        'memory_percent': memory.percent,
        'swap_used': get_size_str(swap.used),
        'swap_total': get_size_str(swap.total),
        'swap_percent': swap.percent
    }
