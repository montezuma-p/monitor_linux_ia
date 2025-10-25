"""
Módulo para monitoramento de memória
"""
import psutil
from typing import Dict, Any


def get_memory_info() -> Dict[str, Any]:
    """Obtém informações sobre uso de memória RAM"""
    mem = psutil.virtual_memory()
    
    return {
        "total_gb": round(mem.total / (1024**3), 2),
        "available_gb": round(mem.available / (1024**3), 2),
        "used_gb": round(mem.used / (1024**3), 2),
        "free_gb": round(mem.free / (1024**3), 2),
        "percent_used": mem.percent,
        "buffers_gb": round(mem.buffers / (1024**3), 2) if hasattr(mem, 'buffers') else 0,
        "cached_gb": round(mem.cached / (1024**3), 2) if hasattr(mem, 'cached') else 0,
        "shared_gb": round(mem.shared / (1024**3), 2) if hasattr(mem, 'shared') else 0
    }


def get_swap_info() -> Dict[str, Any]:
    """Obtém informações sobre uso de swap"""
    swap = psutil.swap_memory()
    
    return {
        "total_gb": round(swap.total / (1024**3), 2),
        "used_gb": round(swap.used / (1024**3), 2),
        "free_gb": round(swap.free / (1024**3), 2),
        "percent_used": swap.percent,
        "swap_in_gb": round(swap.sin / (1024**3), 2) if hasattr(swap, 'sin') else 0,
        "swap_out_gb": round(swap.sout / (1024**3), 2) if hasattr(swap, 'sout') else 0
    }


def collect_memory_metrics(config: Dict[str, Any]) -> Dict[str, Any]:
    """Coleta todas as métricas de memória"""
    return {
        "ram": get_memory_info(),
        "swap": get_swap_info()
    }
