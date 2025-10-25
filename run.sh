#!/bin/bash

# Monitor Completo - Orquestrador
# Executa coleta de métricas e geração de relatórios

set -e  # Parar em caso de erro

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "================================================"
echo "  Monitor Completo - Execução Automatizada"
echo "================================================"
echo ""

# Executar Health Monitor
echo "📊 [1/2] Coletando métricas do sistema..."
cd "$SCRIPT_DIR/health_monitor"
source venv/bin/activate
python3 health_monitor.py
deactivate
cd "$SCRIPT_DIR"
echo "✅ Métricas coletadas com sucesso"
echo ""

# Executar AI Report
echo "🤖 [2/2] Gerando relatório com análise de IA..."
cd "$SCRIPT_DIR/iareport"
source venv/bin/activate
python3 reportia.py
deactivate
cd "$SCRIPT_DIR"
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
