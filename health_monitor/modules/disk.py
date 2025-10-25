"""
Módulo para monitoramento de discos e armazenamento
"""
import psutil
import subprocess
import json
from typing import Dict, List, Any


def get_disk_usage() -> List[Dict[str, Any]]:
    """Obtém informações de uso de disco para todas as partições"""
    partitions = []
    
    for partition in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            partitions.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "fstype": partition.fstype,
                "total_gb": round(usage.total / (1024**3), 2),
                "used_gb": round(usage.used / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
                "percent_used": usage.percent
            })
        except PermissionError:
            # Ignorar partições sem permissão de acesso
            continue
    
    return partitions


def get_inodes_info() -> List[Dict[str, Any]]:
    """Obtém informações sobre uso de inodes"""
    inodes = []
    
    try:
        result = subprocess.run(
            ['df', '-i'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Pular cabeçalho
            
            for line in lines:
                parts = line.split()
                if len(parts) >= 6 and parts[0].startswith('/'):
                    try:
                        percent = parts[4].rstrip('%')
                        inodes.append({
                            "filesystem": parts[0],
                            "inodes_total": parts[1],
                            "inodes_used": parts[2],
                            "inodes_free": parts[3],
                            "percent_used": int(percent) if percent != '-' else 0,
                            "mountpoint": parts[5]
                        })
                    except (ValueError, IndexError):
                        continue
    except Exception as e:
        inodes.append({"error": f"Erro ao obter inodes: {str(e)}"})
    
    return inodes


def get_smart_status() -> List[Dict[str, Any]]:
    """Obtém status SMART dos discos (requer smartmontools)"""
    smart_data = []
    
    try:
        # Listar todos os dispositivos de bloco
        result = subprocess.run(
            ['lsblk', '-d', '-n', '-o', 'NAME,TYPE'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                parts = line.split()
                if len(parts) >= 2 and parts[1] == 'disk':
                    device = f"/dev/{parts[0]}"
                    smart_info = _get_device_smart(device)
                    if smart_info:
                        smart_data.append(smart_info)
    except Exception as e:
        smart_data.append({
            "error": f"Erro ao obter SMART: {str(e)}",
            "note": "Certifique-se de que smartmontools está instalado"
        })
    
    return smart_data


def _get_device_smart(device: str) -> Dict[str, Any]:
    """Obtém informações SMART de um dispositivo específico"""
    try:
        result = subprocess.run(
            ['sudo', 'smartctl', '-H', '-A', device],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        smart_info = {
            "device": device,
            "available": False,
            "health_status": "unknown",
            "temperature": None,
            "power_on_hours": None,
            "reallocated_sectors": None
        }
        
        if result.returncode in [0, 4]:  # 0 = OK, 4 = Some SMART errors
            output = result.stdout
            
            # Verificar se SMART está disponível
            if "SMART support is: Available" in output:
                smart_info["available"] = True
            
            # Status de saúde
            if "PASSED" in output:
                smart_info["health_status"] = "PASSED"
            elif "FAILED" in output:
                smart_info["health_status"] = "FAILED"
            
            # Extrair temperatura
            for line in output.split('\n'):
                if 'Temperature_Celsius' in line or 'Airflow_Temperature' in line:
                    parts = line.split()
                    try:
                        smart_info["temperature"] = int(parts[9])
                        break
                    except (IndexError, ValueError):
                        pass
                
                # Power On Hours
                if 'Power_On_Hours' in line:
                    parts = line.split()
                    try:
                        smart_info["power_on_hours"] = int(parts[9])
                    except (IndexError, ValueError):
                        pass
                
                # Reallocated Sectors
                if 'Reallocated_Sector' in line:
                    parts = line.split()
                    try:
                        smart_info["reallocated_sectors"] = int(parts[9])
                    except (IndexError, ValueError):
                        pass
        
        return smart_info
    except FileNotFoundError:
        return {
            "device": device,
            "error": "smartctl não encontrado. Instale smartmontools"
        }
    except Exception as e:
        return {
            "device": device,
            "error": str(e)
        }


def collect_disk_metrics(config: Dict[str, Any]) -> Dict[str, Any]:
    """Coleta todas as métricas de disco"""
    metrics = {
        "partitions": get_disk_usage(),
        "inodes": get_inodes_info()
    }
    
    # Verificar SMART apenas se configurado
    if config.get("monitoring", {}).get("check_smart", True):
        metrics["smart_status"] = get_smart_status()
    
    return metrics
