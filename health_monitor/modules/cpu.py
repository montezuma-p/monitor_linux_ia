"""
Módulo para monitoramento de CPU
"""
import psutil
import subprocess
from typing import Dict, List, Any, Optional


def get_cpu_usage() -> Dict[str, Any]:
    """Obtém informações de uso da CPU"""
    cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
    cpu_freq = psutil.cpu_freq()
    
    return {
        "percent_total": psutil.cpu_percent(interval=0.1),
        "percent_per_core": cpu_percent,
        "core_count": psutil.cpu_count(logical=False),
        "logical_count": psutil.cpu_count(logical=True),
        "frequency_mhz": {
            "current": round(cpu_freq.current, 2) if cpu_freq else None,
            "min": round(cpu_freq.min, 2) if cpu_freq else None,
            "max": round(cpu_freq.max, 2) if cpu_freq else None
        }
    }


def get_load_average() -> Dict[str, Any]:
    """Obtém a carga média do sistema"""
    load_avg = psutil.getloadavg()
    cpu_count = psutil.cpu_count(logical=True)
    
    return {
        "1_min": round(load_avg[0], 2),
        "5_min": round(load_avg[1], 2),
        "15_min": round(load_avg[2], 2),
        "cpu_count": cpu_count,
        "normalized_1min": round(load_avg[0] / cpu_count, 2),
        "normalized_5min": round(load_avg[1] / cpu_count, 2),
        "normalized_15min": round(load_avg[2] / cpu_count, 2)
    }


def get_cpu_temperature() -> Optional[Dict[str, Any]]:
    """Obtém temperatura da CPU (se disponível)"""
    temps = {}
    
    try:
        # Tentar obter temperatura via psutil
        if hasattr(psutil, 'sensors_temperatures'):
            temp_sensors = psutil.sensors_temperatures()
            
            if temp_sensors:
                # Procurar por sensores comuns
                for sensor_name in ['coretemp', 'k10temp', 'cpu_thermal', 'acpitz']:
                    if sensor_name in temp_sensors:
                        sensor_data = temp_sensors[sensor_name]
                        temps[sensor_name] = []
                        
                        for entry in sensor_data:
                            temps[sensor_name].append({
                                "label": entry.label or "Unknown",
                                "current": entry.current,
                                "high": entry.high if entry.high else None,
                                "critical": entry.critical if entry.critical else None
                            })
                
                # Se encontrou alguma temperatura, retornar
                if temps:
                    return temps
    except Exception as e:
        pass
    
    # Tentar método alternativo usando sensors (lm-sensors)
    try:
        result = subprocess.run(
            ['sensors', '-A', '-u'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return {"raw_output": "Available via lm-sensors", "note": "Use 'sensors' command"}
    except FileNotFoundError:
        return {"error": "Sensors não disponível. Instale lm-sensors"}
    except Exception:
        pass
    
    return {"error": "Temperatura não disponível"}


def collect_cpu_metrics(config: Dict[str, Any]) -> Dict[str, Any]:
    """Coleta todas as métricas de CPU"""
    return {
        "usage": get_cpu_usage(),
        "load_average": get_load_average(),
        "temperature": get_cpu_temperature()
    }
