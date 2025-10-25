"""
Módulo para monitoramento do sistema
"""
import psutil
import subprocess
import platform
from datetime import datetime, timedelta
from typing import Dict, List, Any


def get_system_info() -> Dict[str, Any]:
    """Obtém informações básicas do sistema"""
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    
    return {
        "hostname": platform.node(),
        "os": platform.system(),
        "os_version": platform.version(),
        "distribution": _get_distribution_info(),
        "kernel": platform.release(),
        "architecture": platform.machine(),
        "boot_time": boot_time.isoformat(),
        "uptime_seconds": int(uptime.total_seconds()),
        "uptime_human": _format_uptime(uptime)
    }


def _get_distribution_info() -> str:
    """Obtém informações sobre a distribuição Linux"""
    try:
        with open('/etc/os-release', 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('PRETTY_NAME='):
                    return line.split('=')[1].strip().strip('"')
    except Exception:
        pass
    
    return platform.platform()


def _format_uptime(uptime: timedelta) -> str:
    """Formata o uptime em formato legível"""
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    
    return " ".join(parts) if parts else "< 1m"


def get_process_info() -> Dict[str, Any]:
    """Obtém informações sobre processos"""
    process_count = len(psutil.pids())
    
    # Top processos por CPU
    top_cpu = []
    # Top processos por memória
    top_memory = []
    
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Ordenar por CPU
        sorted_cpu = sorted(processes, key=lambda x: x.get('cpu_percent', 0), reverse=True)[:5]
        top_cpu = [
            {
                "pid": p['pid'],
                "name": p['name'],
                "cpu_percent": round(p.get('cpu_percent', 0), 2)
            }
            for p in sorted_cpu
        ]
        
        # Ordenar por memória
        sorted_mem = sorted(processes, key=lambda x: x.get('memory_percent', 0), reverse=True)[:5]
        top_memory = [
            {
                "pid": p['pid'],
                "name": p['name'],
                "memory_percent": round(p.get('memory_percent', 0), 2)
            }
            for p in sorted_mem
        ]
    except Exception as e:
        pass
    
    return {
        "total_processes": process_count,
        "top_cpu_usage": top_cpu,
        "top_memory_usage": top_memory
    }


def get_systemd_services(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Obtém status de serviços systemd importantes"""
    services = []
    
    if not config.get("monitoring", {}).get("check_systemd_services", True):
        return services
    
    # Lista de serviços comuns para verificar
    important_services = [
        'NetworkManager',
        'systemd-journald',
        'sshd',
        'firewalld',
        'chronyd',
        'dbus',
        'polkit'
    ]
    
    for service in important_services:
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', service],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            status = result.stdout.strip()
            
            services.append({
                "name": service,
                "status": status,
                "active": status == "active"
            })
        except Exception as e:
            services.append({
                "name": service,
                "status": "error",
                "error": str(e)
            })
    
    return services


def get_failed_services() -> List[str]:
    """Obtém lista de serviços que falharam"""
    failed = []
    
    try:
        result = subprocess.run(
            ['systemctl', '--failed', '--no-pager', '--no-legend'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                parts = line.split()
                if parts:
                    failed.append(parts[0])
    except Exception:
        pass
    
    return failed


def collect_system_metrics(config: Dict[str, Any]) -> Dict[str, Any]:
    """Coleta todas as métricas do sistema"""
    return {
        "info": get_system_info(),
        "processes": get_process_info(),
        "systemd_services": get_systemd_services(config),
        "failed_services": get_failed_services()
    }
