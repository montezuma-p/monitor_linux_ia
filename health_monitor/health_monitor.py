#!/usr/bin/env python3
"""
Health Monitor - Sistema de monitoramento de saúde para Fedora Workstation
Coleta métricas do sistema e gera relatórios em JSON
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Adicionar o diretório modules ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules import disk, memory, cpu, system, network, logs, alerts


def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Carrega arquivo de configuração"""
    script_dir = Path(__file__).parent
    config_file = script_dir / config_path
    
    # Definir diretório de saída padrão na raiz do projeto
    project_root = script_dir.parent
    default_output_dir = project_root / "exemplosdesaida" / "saidasraw"
    
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️  Arquivo de configuração não encontrado: {config_file}")
        print("Usando configuração padrão...")
        return {
            "output_dir": str(default_output_dir),
            "thresholds": {},
            "monitoring": {}
        }
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao ler arquivo de configuração: {e}")
        sys.exit(1)


def collect_all_metrics(config: Dict[str, Any]) -> Dict[str, Any]:
    """Coleta todas as métricas do sistema"""
    print("📊 Coletando métricas do sistema...")
    
    metrics = {}
    
    # Coletar métricas de disco
    print("  💾 Disco...")
    try:
        metrics["disk"] = disk.collect_disk_metrics(config)
    except Exception as e:
        print(f"    ⚠️  Erro: {e}")
        metrics["disk"] = {"error": str(e)}
    
    # Coletar métricas de memória
    print("  🧠 Memória...")
    try:
        metrics["memory"] = memory.collect_memory_metrics(config)
    except Exception as e:
        print(f"    ⚠️  Erro: {e}")
        metrics["memory"] = {"error": str(e)}
    
    # Coletar métricas de CPU
    print("  ⚡ CPU...")
    try:
        metrics["cpu"] = cpu.collect_cpu_metrics(config)
    except Exception as e:
        print(f"    ⚠️  Erro: {e}")
        metrics["cpu"] = {"error": str(e)}
    
    # Coletar métricas do sistema
    print("  🖥️  Sistema...")
    try:
        metrics["system"] = system.collect_system_metrics(config)
    except Exception as e:
        print(f"    ⚠️  Erro: {e}")
        metrics["system"] = {"error": str(e)}
    
    # Coletar métricas de rede
    print("  🌐 Rede...")
    try:
        metrics["network"] = network.collect_network_metrics(config)
    except Exception as e:
        print(f"    ⚠️  Erro: {e}")
        metrics["network"] = {"error": str(e)}
    
    # Coletar logs
    print("  📋 Logs...")
    try:
        metrics["logs"] = logs.collect_log_metrics(config)
    except Exception as e:
        print(f"    ⚠️  Erro: {e}")
        metrics["logs"] = {"error": str(e)}
    
    return metrics


def generate_report(config: Dict[str, Any]) -> Dict[str, Any]:
    """Gera relatório completo do sistema"""
    # Timestamp do relatório
    timestamp = datetime.now()
    
    # Coletar métricas
    metrics = collect_all_metrics(config)
    
    # Gerar alertas
    print("🚨 Gerando alertas...")
    system_alerts = alerts.generate_alerts(metrics, config)
    
    # Montar relatório completo
    report = {
        "timestamp": timestamp.isoformat(),
        "timestamp_unix": int(timestamp.timestamp()),
        "hostname": metrics.get("system", {}).get("info", {}).get("hostname", "unknown"),
        "metrics": metrics,
        "alerts": system_alerts,
        "summary": {
            "total_alerts": len(system_alerts),
            "critical_alerts": sum(1 for a in system_alerts if a.get("severity") == "critical"),
            "warning_alerts": sum(1 for a in system_alerts if a.get("severity") == "warning"),
            "health_status": "critical" if any(a.get("severity") == "critical" for a in system_alerts) else (
                "warning" if system_alerts else "healthy"
            )
        }
    }
    
    return report


def save_report(report: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Salva relatório em arquivo JSON"""
    # Usar caminho relativo ao projeto se não especificado
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    default_output_dir = project_root / "exemplosdesaida" / "saidasraw"
    
    output_dir = Path(config.get("output_dir", str(default_output_dir)))
    
    # Criar diretório se não existir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Nome do arquivo com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"health_{timestamp}.json"
    filepath = output_dir / filename
    
    # Salvar JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return str(filepath)


def print_summary(report: Dict[str, Any]):
    """Imprime resumo do relatório"""
    print("\n" + "="*60)
    print("📊 RESUMO DO MONITORAMENTO DE SAÚDE")
    print("="*60)
    
    summary = report.get("summary", {})
    health_status = summary.get("health_status", "unknown")
    
    # Status geral
    status_icon = {
        "healthy": "✅",
        "warning": "⚠️",
        "critical": "❌"
    }.get(health_status, "❓")
    
    print(f"\n{status_icon} Status Geral: {health_status.upper()}")
    print(f"🕐 Timestamp: {report.get('timestamp', 'N/A')}")
    print(f"🖥️  Hostname: {report.get('hostname', 'N/A')}")
    
    # Alertas
    print(f"\n🚨 Alertas:")
    print(f"   Total: {summary.get('total_alerts', 0)}")
    print(f"   Críticos: {summary.get('critical_alerts', 0)}")
    print(f"   Avisos: {summary.get('warning_alerts', 0)}")
    
    # Listar alertas críticos
    critical_alerts = [a for a in report.get("alerts", []) if a.get("severity") == "critical"]
    if critical_alerts:
        print(f"\n❌ Alertas Críticos:")
        for alert in critical_alerts[:5]:  # Mostrar apenas os 5 primeiros
            print(f"   • {alert.get('message', 'N/A')}")
    
    # Métricas rápidas
    metrics = report.get("metrics", {})
    
    if "memory" in metrics:
        ram = metrics["memory"].get("ram", {})
        print(f"\n🧠 RAM: {ram.get('percent_used', 0):.1f}% ({ram.get('used_gb', 0):.1f}/{ram.get('total_gb', 0):.1f} GB)")
    
    if "cpu" in metrics:
        cpu_usage = metrics["cpu"].get("usage", {}).get("percent_total", 0)
        load = metrics["cpu"].get("load_average", {})
        print(f"⚡ CPU: {cpu_usage:.1f}% | Load: {load.get('1_min', 0):.2f}, {load.get('5_min', 0):.2f}, {load.get('15_min', 0):.2f}")
    
    if "disk" in metrics:
        partitions = metrics["disk"].get("partitions", [])
        if partitions:
            root_partition = next((p for p in partitions if p.get("mountpoint") == "/"), partitions[0])
            print(f"💾 Disco (/): {root_partition.get('percent_used', 0):.1f}% ({root_partition.get('free_gb', 0):.1f} GB livres)")
    
    print("\n" + "="*60)


def main():
    """Função principal"""
    print("🏥 Health Monitor - Iniciando monitoramento...")
    print()
    
    # Carregar configuração
    config = load_config()
    
    try:
        # Gerar relatório
        report = generate_report(config)
        
        # Salvar relatório
        print("\n💾 Salvando relatório...")
        filepath = save_report(report, config)
        print(f"✅ Relatório salvo em: {filepath}")
        
        # Imprimir resumo
        print_summary(report)
        
        # Status de saída baseado na saúde do sistema
        health_status = report.get("summary", {}).get("health_status", "unknown")
        if health_status == "critical":
            sys.exit(2)
        elif health_status == "warning":
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Monitoramento interrompido pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
