"""
Módulo para coleta de logs do sistema
"""
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any


def get_journal_errors(hours: int = 24) -> List[Dict[str, Any]]:
    """Obtém erros e warnings do journal das últimas N horas"""
    errors = []
    
    try:
        # Calcular timestamp de início
        since_time = datetime.now() - timedelta(hours=hours)
        since_str = since_time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Buscar por mensagens de erro e críticas
        result = subprocess.run(
            ['journalctl', '-p', 'err', '--since', since_str, '--no-pager', '-o', 'json'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            import json
            for line in result.stdout.strip().split('\n'):
                try:
                    entry = json.loads(line)
                    errors.append({
                        "timestamp": entry.get('__REALTIME_TIMESTAMP', ''),
                        "priority": entry.get('PRIORITY', ''),
                        "unit": entry.get('_SYSTEMD_UNIT', entry.get('SYSLOG_IDENTIFIER', 'unknown')),
                        "message": entry.get('MESSAGE', '')[:200]  # Limitar tamanho da mensagem
                    })
                except json.JSONDecodeError:
                    continue
            
            # Limitar a 50 entradas mais recentes
            errors = errors[-50:]
    except FileNotFoundError:
        errors.append({"error": "journalctl não encontrado"})
    except Exception as e:
        errors.append({"error": f"Erro ao coletar logs: {str(e)}"})
    
    return errors


def get_journal_warnings(hours: int = 24) -> List[Dict[str, Any]]:
    """Obtém warnings do journal das últimas N horas"""
    warnings = []
    
    try:
        since_time = datetime.now() - timedelta(hours=hours)
        since_str = since_time.strftime('%Y-%m-%d %H:%M:%S')
        
        result = subprocess.run(
            ['journalctl', '-p', 'warning', '--since', since_str, '--no-pager', '-o', 'json'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            import json
            for line in result.stdout.strip().split('\n'):
                try:
                    entry = json.loads(line)
                    warnings.append({
                        "timestamp": entry.get('__REALTIME_TIMESTAMP', ''),
                        "unit": entry.get('_SYSTEMD_UNIT', entry.get('SYSLOG_IDENTIFIER', 'unknown')),
                        "message": entry.get('MESSAGE', '')[:200]
                    })
                except json.JSONDecodeError:
                    continue
            
            # Limitar a 30 entradas mais recentes
            warnings = warnings[-30:]
    except Exception as e:
        warnings.append({"error": f"Erro ao coletar warnings: {str(e)}"})
    
    return warnings


def get_boot_messages() -> List[str]:
    """Obtém mensagens do último boot"""
    messages = []
    
    try:
        result = subprocess.run(
            ['journalctl', '-b', '-p', 'err', '--no-pager', '--no-hostname', '-n', '20'],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode == 0 and result.stdout.strip():
            messages = result.stdout.strip().split('\n')
    except Exception as e:
        messages.append(f"Erro ao coletar mensagens de boot: {str(e)}")
    
    return messages


def get_kernel_messages() -> List[str]:
    """Obtém mensagens recentes do kernel"""
    messages = []
    
    try:
        result = subprocess.run(
            ['dmesg', '-T', '-l', 'err,warn', '--color=never'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            # Pegar apenas as últimas 20 linhas
            messages = lines[-20:]
    except FileNotFoundError:
        messages.append("dmesg não encontrado ou sem permissão")
    except Exception as e:
        messages.append(f"Erro ao coletar mensagens do kernel: {str(e)}")
    
    return messages


def collect_log_metrics(config: Dict[str, Any]) -> Dict[str, Any]:
    """Coleta todas as métricas de logs"""
    metrics = {}
    
    if config.get("monitoring", {}).get("check_journal_errors", True):
        hours = config.get("monitoring", {}).get("journal_errors_hours", 24)
        
        metrics = {
            "errors": get_journal_errors(hours),
            "warnings": get_journal_warnings(hours),
            "boot_errors": get_boot_messages(),
            "kernel_messages": get_kernel_messages(),
            "collection_period_hours": hours
        }
    
    return metrics
