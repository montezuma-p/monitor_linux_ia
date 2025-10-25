"""
Módulo para monitoramento de rede
"""
import psutil
import subprocess
import socket
from typing import Dict, List, Any


def get_network_interfaces() -> List[Dict[str, Any]]:
    """Obtém informações sobre interfaces de rede"""
    interfaces = []
    
    # Estatísticas de rede
    net_io = psutil.net_io_counters(pernic=True)
    # Endereços de rede
    net_addrs = psutil.net_if_addrs()
    # Status das interfaces
    net_stats = psutil.net_if_stats()
    
    for interface_name, stats in net_stats.items():
        interface_info = {
            "name": interface_name,
            "is_up": stats.isup,
            "speed_mbps": stats.speed,
            "mtu": stats.mtu
        }
        
        # Adicionar endereços
        if interface_name in net_addrs:
            addresses = []
            for addr in net_addrs[interface_name]:
                addr_info = {
                    "family": str(addr.family),
                    "address": addr.address
                }
                if addr.netmask:
                    addr_info["netmask"] = addr.netmask
                addresses.append(addr_info)
            interface_info["addresses"] = addresses
        
        # Adicionar estatísticas de I/O
        if interface_name in net_io:
            io = net_io[interface_name]
            interface_info["statistics"] = {
                "bytes_sent_mb": round(io.bytes_sent / (1024**2), 2),
                "bytes_recv_mb": round(io.bytes_recv / (1024**2), 2),
                "packets_sent": io.packets_sent,
                "packets_recv": io.packets_recv,
                "errors_in": io.errin,
                "errors_out": io.errout,
                "drops_in": io.dropin,
                "drops_out": io.dropout
            }
        
        interfaces.append(interface_info)
    
    return interfaces


def get_network_connections() -> Dict[str, Any]:
    """Obtém informações sobre conexões de rede"""
    connections = {
        "total": 0,
        "established": 0,
        "listen": 0,
        "time_wait": 0,
        "close_wait": 0
    }
    
    try:
        conns = psutil.net_connections(kind='inet')
        connections["total"] = len(conns)
        
        for conn in conns:
            status = conn.status
            if status == 'ESTABLISHED':
                connections["established"] += 1
            elif status == 'LISTEN':
                connections["listen"] += 1
            elif status == 'TIME_WAIT':
                connections["time_wait"] += 1
            elif status == 'CLOSE_WAIT':
                connections["close_wait"] += 1
    except (psutil.AccessDenied, PermissionError):
        connections["error"] = "Acesso negado. Execute com sudo para informações completas"
    
    return connections


def check_connectivity(hosts: List[str]) -> List[Dict[str, Any]]:
    """Verifica conectividade com hosts específicos"""
    results = []
    
    for host in hosts:
        result = {
            "host": host,
            "reachable": False,
            "latency_ms": None
        }
        
        try:
            # Usar ping para verificar conectividade
            ping_result = subprocess.run(
                ['ping', '-c', '1', '-W', '2', host],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if ping_result.returncode == 0:
                result["reachable"] = True
                
                # Extrair latência
                output = ping_result.stdout
                for line in output.split('\n'):
                    if 'time=' in line:
                        try:
                            time_part = line.split('time=')[1].split()[0]
                            result["latency_ms"] = round(float(time_part), 2)
                        except (IndexError, ValueError):
                            pass
                        break
        except Exception as e:
            result["error"] = str(e)
        
        results.append(result)
    
    return results


def get_dns_info() -> Dict[str, Any]:
    """Obtém informações sobre configuração DNS"""
    dns_info = {
        "nameservers": [],
        "can_resolve": False
    }
    
    try:
        # Ler /etc/resolv.conf
        with open('/etc/resolv.conf', 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('nameserver'):
                    parts = line.split()
                    if len(parts) >= 2:
                        dns_info["nameservers"].append(parts[1])
    except Exception as e:
        dns_info["error"] = f"Erro ao ler resolv.conf: {str(e)}"
    
    # Testar resolução DNS
    try:
        socket.gethostbyname('google.com')
        dns_info["can_resolve"] = True
    except Exception:
        dns_info["can_resolve"] = False
    
    return dns_info


def collect_network_metrics(config: Dict[str, Any]) -> Dict[str, Any]:
    """Coleta todas as métricas de rede"""
    metrics = {
        "interfaces": get_network_interfaces(),
        "connections": get_network_connections(),
        "dns": get_dns_info()
    }
    
    # Verificar conectividade se configurado
    hosts = config.get("monitoring", {}).get("network_check_hosts", [])
    if hosts:
        metrics["connectivity"] = check_connectivity(hosts)
    
    return metrics
