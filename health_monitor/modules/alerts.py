"""
Módulo para geração de alertas baseados em thresholds
"""
from typing import Dict, List, Any


def check_disk_alerts(disk_metrics: Dict[str, Any], thresholds: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Verifica alertas relacionados a disco"""
    alerts = []
    
    for partition in disk_metrics.get("partitions", []):
        usage = partition.get("percent_used", 0)
        mountpoint = partition.get("mountpoint", "unknown")
        
        if usage >= thresholds.get("disk_usage_critical", 90):
            alerts.append({
                "severity": "critical",
                "category": "disk",
                "message": f"Uso crítico de disco em {mountpoint}: {usage}%",
                "value": usage,
                "threshold": thresholds["disk_usage_critical"],
                "mountpoint": mountpoint
            })
        elif usage >= thresholds.get("disk_usage_warning", 80):
            alerts.append({
                "severity": "warning",
                "category": "disk",
                "message": f"Uso alto de disco em {mountpoint}: {usage}%",
                "value": usage,
                "threshold": thresholds["disk_usage_warning"],
                "mountpoint": mountpoint
            })
    
    # Verificar SMART status
    for smart in disk_metrics.get("smart_status", []):
        if smart.get("health_status") == "FAILED":
            alerts.append({
                "severity": "critical",
                "category": "disk",
                "message": f"SMART falhou para {smart.get('device', 'unknown')}",
                "device": smart.get("device")
            })
    
    return alerts


def check_memory_alerts(memory_metrics: Dict[str, Any], thresholds: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Verifica alertas relacionados a memória"""
    alerts = []
    
    ram_usage = memory_metrics.get("ram", {}).get("percent_used", 0)
    swap_usage = memory_metrics.get("swap", {}).get("percent_used", 0)
    
    # Alertas de RAM
    if ram_usage >= thresholds.get("memory_usage_critical", 95):
        alerts.append({
            "severity": "critical",
            "category": "memory",
            "message": f"Uso crítico de RAM: {ram_usage}%",
            "value": ram_usage,
            "threshold": thresholds["memory_usage_critical"]
        })
    elif ram_usage >= thresholds.get("memory_usage_warning", 80):
        alerts.append({
            "severity": "warning",
            "category": "memory",
            "message": f"Uso alto de RAM: {ram_usage}%",
            "value": ram_usage,
            "threshold": thresholds["memory_usage_warning"]
        })
    
    # Alertas de Swap
    if swap_usage >= thresholds.get("swap_usage_critical", 80):
        alerts.append({
            "severity": "critical",
            "category": "memory",
            "message": f"Uso crítico de Swap: {swap_usage}%",
            "value": swap_usage,
            "threshold": thresholds["swap_usage_critical"]
        })
    elif swap_usage >= thresholds.get("swap_usage_warning", 50):
        alerts.append({
            "severity": "warning",
            "category": "memory",
            "message": f"Uso alto de Swap: {swap_usage}%",
            "value": swap_usage,
            "threshold": thresholds["swap_usage_warning"]
        })
    
    return alerts


def check_cpu_alerts(cpu_metrics: Dict[str, Any], thresholds: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Verifica alertas relacionados a CPU"""
    alerts = []
    
    load_avg = cpu_metrics.get("load_average", {})
    load_1min = load_avg.get("normalized_1min", 0)
    load_5min = load_avg.get("normalized_5min", 0)
    
    # Alertas de carga
    if load_5min >= thresholds.get("cpu_load_critical", 4.0):
        alerts.append({
            "severity": "critical",
            "category": "cpu",
            "message": f"Carga crítica da CPU (5min): {load_5min}",
            "value": load_5min,
            "threshold": thresholds["cpu_load_critical"]
        })
    elif load_5min >= thresholds.get("cpu_load_warning", 2.0):
        alerts.append({
            "severity": "warning",
            "category": "cpu",
            "message": f"Carga alta da CPU (5min): {load_5min}",
            "value": load_5min,
            "threshold": thresholds["cpu_load_warning"]
        })
    
    # Alertas de temperatura
    temp_data = cpu_metrics.get("temperature", {})
    if isinstance(temp_data, dict) and not temp_data.get("error"):
        for sensor_name, readings in temp_data.items():
            if isinstance(readings, list):
                for reading in readings:
                    current_temp = reading.get("current")
                    if current_temp:
                        if current_temp >= thresholds.get("cpu_temp_critical", 85):
                            alerts.append({
                                "severity": "critical",
                                "category": "cpu",
                                "message": f"Temperatura crítica da CPU: {current_temp}°C",
                                "value": current_temp,
                                "threshold": thresholds["cpu_temp_critical"],
                                "sensor": reading.get("label", sensor_name)
                            })
                        elif current_temp >= thresholds.get("cpu_temp_warning", 70):
                            alerts.append({
                                "severity": "warning",
                                "category": "cpu",
                                "message": f"Temperatura alta da CPU: {current_temp}°C",
                                "value": current_temp,
                                "threshold": thresholds["cpu_temp_warning"],
                                "sensor": reading.get("label", sensor_name)
                            })
    
    return alerts


def check_system_alerts(system_metrics: Dict[str, Any], thresholds: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Verifica alertas relacionados ao sistema"""
    alerts = []
    
    # Verificar serviços falhados
    failed_services = system_metrics.get("failed_services", [])
    if failed_services:
        alerts.append({
            "severity": "warning",
            "category": "system",
            "message": f"{len(failed_services)} serviço(s) systemd falharam",
            "services": failed_services
        })
    
    # Verificar serviços importantes inativos
    for service in system_metrics.get("systemd_services", []):
        if not service.get("active", True) and service.get("status") != "inactive":
            alerts.append({
                "severity": "warning",
                "category": "system",
                "message": f"Serviço {service.get('name')} não está ativo",
                "service": service.get("name"),
                "status": service.get("status")
            })
    
    return alerts


def check_network_alerts(network_metrics: Dict[str, Any], thresholds: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Verifica alertas relacionados à rede"""
    alerts = []
    
    # Verificar conectividade
    for conn in network_metrics.get("connectivity", []):
        if not conn.get("reachable", False):
            alerts.append({
                "severity": "warning",
                "category": "network",
                "message": f"Host {conn.get('host')} não acessível",
                "host": conn.get("host")
            })
    
    # Verificar DNS
    dns = network_metrics.get("dns", {})
    if not dns.get("can_resolve", True):
        alerts.append({
            "severity": "critical",
            "category": "network",
            "message": "Falha na resolução DNS",
        })
    
    # Verificar interfaces com erros
    for interface in network_metrics.get("interfaces", []):
        stats = interface.get("statistics", {})
        errors_in = stats.get("errors_in", 0)
        errors_out = stats.get("errors_out", 0)
        
        if errors_in > 100 or errors_out > 100:
            alerts.append({
                "severity": "warning",
                "category": "network",
                "message": f"Interface {interface.get('name')} com erros elevados",
                "interface": interface.get("name"),
                "errors_in": errors_in,
                "errors_out": errors_out
            })
    
    return alerts


def generate_alerts(metrics: Dict[str, Any], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Gera todos os alertas baseados nas métricas coletadas"""
    all_alerts = []
    thresholds = config.get("thresholds", {})
    
    # Coletar alertas de cada categoria
    if "disk" in metrics:
        all_alerts.extend(check_disk_alerts(metrics["disk"], thresholds))
    
    if "memory" in metrics:
        all_alerts.extend(check_memory_alerts(metrics["memory"], thresholds))
    
    if "cpu" in metrics:
        all_alerts.extend(check_cpu_alerts(metrics["cpu"], thresholds))
    
    if "system" in metrics:
        all_alerts.extend(check_system_alerts(metrics["system"], thresholds))
    
    if "network" in metrics:
        all_alerts.extend(check_network_alerts(metrics["network"], thresholds))
    
    return all_alerts
