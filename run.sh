#!/bin/bash

# Monitor Completo - Orquestrador
# Executa coleta de métricas e geração de relatórios

set -e  # Parar em caso de erro


echo "================================================"
echo "  Monitor Completo - Execução Automatizada"
echo "================================================"
echo ""

# Executar Health Monitor
echo "📊 [1/2] Coletando métricas do sistema..."
cd ~/monitor_linux_ia/health_monitor
source venv/bin/activate
python3 health_monitor.py
deactivate
cd ~/monitor_linux_ia
echo "✅ Métricas coletadas com sucesso"
echo ""

# Executar AI Report
echo "🤖 [2/2] Gerando relatório com análise de IA..."
cd ~/monitor_linux_ia/iareport
source venv/bin/activate
python3 reportia.py
deactivate

echo "✅ Relatório gerado com sucesso"
echo ""

echo "================================================"
echo "  Execução Concluída"
echo "================================================"
echo ""
echo "Arquivos gerados:"
echo "  📄 JSON: exemplosdesaida/saidasraw/"
echo "  📄 HTML: exemplosdesaida/saidascomia/"
echo ""
