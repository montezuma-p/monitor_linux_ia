#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Health Reporter - Gerador de Relatórios de Saúde do Sistema usando Gemini
Analisa JSONs do health_monitor e gera relatórios HTML humanizados


  █████████████████████████████████████████
  █                                       █
  █   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░     █
  █   ░   B Y   M O N T E Z U M A   ░     █
  █   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░     █
  █                                       █
  █████████████████████████████████████████

"""

import os
import sys
import json
import glob
from pathlib import Path
from datetime import datetime
from google import genai
from google.genai import types

# Verificar se a chave da API está configurada
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ ERRO: Variável GEMINI_API_KEY não encontrada!")
    print("Configure com: export GEMINI_API_KEY='sua_chave_aqui'")
    sys.exit(1)

# Configurar cliente Gemini
client = genai.Client(api_key=api_key)
model = "gemini-2.5-flash"

# Configurar caminhos relativos ao projeto
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
REPORTS_DIR = PROJECT_ROOT / "exemplosdesaida" / "saidasraw"
OUTPUT_DIR = PROJECT_ROOT / "exemplosdesaida" / "saidascomia"


def obter_ultimo_json():
    """Obtém o arquivo JSON mais recente do diretório de relatórios"""
    json_files = glob.glob(str(REPORTS_DIR / "health_*.json"))
    
    if not json_files:
        print(f"❌ Nenhum relatório encontrado em {REPORTS_DIR}")
        return None
    
    # Pegar o arquivo mais recente
    latest_file = max(json_files, key=os.path.getctime)
    return Path(latest_file)


def ler_json(filepath):
    """Lê e retorna o conteúdo do arquivo JSON"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Erro ao ler arquivo {filepath}: {e}")
        return None


def criar_prompt_analise(dados_json):
    """Cria o prompt para a IA analisar o relatório de saúde"""
    
    prompt = f"""Você é um administrador de sistemas Linux sênior com 15 anos de experiência em Fedora/RHEL.

Analise este relatório de saúde do sistema e crie uma análise INTERPRETATIVA e HUMANIZADA em formato JSON.

DADOS BRUTOS DO SISTEMA:
```json
{json.dumps(dados_json, indent=2, ensure_ascii=False)}
```

IMPORTANTE: Retorne um JSON estruturado que será usado para preencher um template HTML.

ESTRUTURA DO JSON A RETORNAR:

{{
    "resumo_executivo": "2-3 parágrafos explicando o estado geral do sistema em linguagem humana. Contextualize números, use analogias, seja claro.",
    
    "metricas_cards": [
        {{
            "icon": "emoji do ícone",
            "label": "Nome da métrica",
            "value": "Valor principal",
            "subtext": "Texto complementar"
        }}
    ],
    
    "alertas": [
        {{
            "tipo": "critical" ou "warning",
            "titulo": "Título do alerta",
            "descricao": "O que está acontecendo em linguagem clara",
            "impacto": "Por que isso importa",
            "solucao": "O que fazer (pode incluir comandos)",
            "prioridade": "alta, media ou baixa"
        }}
    ],
    
    "analise_discos": "Análise INTERPRETADA dos discos. Explique status SMART, uso de partições, inodes. Traduza números técnicos. Diga se está bom ou ruim.",
    
    "analise_memoria": "Análise INTERPRETADA da memória. Explique RAM, Swap, processos. Contextualize uso (é normal? é muito?). Quando se preocupar?",
    
    "analise_cpu": "Análise INTERPRETADA da CPU. Load average em termos humanos, temperatura, processos. Performance está ok?",
    
    "analise_sistema": "Análise do sistema. Uptime, serviços, distribuição. Tudo funcionando bem?",
    
    "analise_rede": "Análise da rede. Conectividade, interfaces, DNS. Internet ok?",
    
    "analise_logs": "Resumo dos logs. Erros importantes? Warnings? Kernel ok?",
    
    "recomendacoes": [
        {{
            "prioridade": "alta, media ou baixa",
            "titulo": "Título da recomendação",
            "descricao": "Explicação detalhada",
            "comandos": ["comando1", "comando2"] ou null
        }}
    ],
    
    "conclusao": "1-2 parágrafos resumindo: estado geral, pontos positivos, o que merece atenção, próximos passos"
}}

REGRAS CRÍTICAS:

✅ INTERPRETE - não apenas liste dados
✅ EXPLIQUE - contextualize cada métrica  
✅ HUMANIZE - escreva como se estivesse explicando para um colega
✅ SEJA PRÁTICO - dê comandos reais para resolver problemas
✅ USE ANALOGIAS quando útil

EXEMPLOS DO TOM:

❌ ERRADO: "Disco /home: 85% usado"
✅ CORRETO: "Seu disco /home está usando 85% do espaço (340GB de 400GB). Isso significa que você tem apenas 60GB livres. Quando o disco ultrapassa 90%, o sistema pode ficar lento."

❌ ERRADO: "Load average: 2.5"
✅ CORRETO: "Seu sistema tem load average de 2.5 nos últimos 5 minutos. Como você tem 8 cores, isso representa ~31% de uso. Está tranquilo!"

❌ ERRADO: "RAM: 8192MB/16384MB"
✅ CORRETO: "Você está usando 8GB de 16GB de RAM (50%). Isso é perfeitamente normal! Fedora usa memória como cache para acelerar o sistema."

Retorne APENAS o JSON válido, sem markdown, sem explicações extras.

MISSÃO: NÃO APENAS MOSTRE OS DADOS - INTERPRETE, EXPLIQUE E TRADUZA PARA LINGUAGEM HUMANA!
"""

    return prompt


def chamar_gemini(prompt):
    """Chama a API do Gemini para gerar a análise em JSON"""
    try:
        print("⏳ Enviando dados para análise do Gemini...")
        
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.95,
                max_output_tokens=8192
            )
        )
        
        resultado = response.text.strip()
        
        # Limpar markdown se houver
        json_text = resultado
        if "```json" in resultado:
            json_start = resultado.find("```json") + 7
            json_end = resultado.find("```", json_start)
            if json_end > json_start:
                json_text = resultado[json_start:json_end].strip()
        elif "```" in resultado:
            json_start = resultado.find("```") + 3
            json_end = resultado.rfind("```")
            if json_end > json_start:
                json_text = resultado[json_start:json_end].strip()
        
        # Extrair apenas o JSON
        first_brace = json_text.find('{')
        last_brace = json_text.rfind('}')
        if first_brace != -1 and last_brace != -1:
            json_text = json_text[first_brace:last_brace+1]
        
        # Parsear JSON
        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"⚠️ Erro ao parsear JSON: {e}")
            print("Primeiros 500 caracteres da resposta:")
            print(resultado[:500])
            return None
        
    except Exception as e:
        print(f"❌ Erro ao chamar Gemini API: {e}")
        return None


def gerar_metrics_cards(metricas):
    """Gera HTML dos cards de métricas"""
    cards_html = ""
    for metrica in metricas:
        cards_html += f"""
                    <div class="metric-card">
                        <div class="icon">{metrica.get('icon', '📊')}</div>
                        <div class="label">{metrica.get('label', 'Métrica')}</div>
                        <div class="value">{metrica.get('value', 'N/A')}</div>
                        <div class="subtext">{metrica.get('subtext', '')}</div>
                    </div>
"""
    return cards_html


def gerar_alertas_section(alertas):
    """Gera HTML da seção de alertas"""
    if not alertas:
        return ""
    
    html = """
            <div class="section">
                <h2 class="section-title">🚨 Alertas e Problemas</h2>
"""
    
    for alerta in alertas:
        tipo_class = "alert-critical" if alerta.get('tipo') == 'critical' else "alert-warning"
        
        html += f"""
                <div class="alert-box {tipo_class}">
                    <h4>{alerta.get('titulo', 'Alerta')}</h4>
                    <p><strong>Situação:</strong> {alerta.get('descricao', '')}</p>
                    <p><strong>Por que isso importa:</strong> {alerta.get('impacto', '')}</p>
"""
        
        if alerta.get('solucao'):
            html += f"""
                    <div class="solution">
                        <strong>O que fazer:</strong><br>
                        {alerta.get('solucao', '')}
                    </div>
"""
        
        html += """
                </div>
"""
    
    html += """
            </div>
"""
    return html


def gerar_recomendacoes(recomendacoes):
    """Gera HTML das recomendações"""
    html = '<ul class="recommendation-list">\n'
    
    for rec in recomendacoes:
        prioridade = rec.get('prioridade', 'media')
        priority_class = f"priority-{prioridade}"
        
        html += f'<li class="{priority_class}">\n'
        html += f'<strong>{rec.get("titulo", "Recomendação")}</strong><br>\n'
        html += f'{rec.get("descricao", "")}<br>\n'
        
        if rec.get('comandos'):
            html += '<pre><code>'
            for cmd in rec['comandos']:
                html += f'{cmd}\n'
            html += '</code></pre>\n'
        
        html += '</li>\n'
    
    html += '</ul>'
    return html


def preencher_template(analise_json, dados_originais):
    """Preenche o template HTML com os dados da análise"""
    
    # Carregar template
    template_path = Path(__file__).parent / "template.html"
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    except Exception as e:
        print(f"❌ Erro ao ler template: {e}")
        return None
    
    # Determinar status e classe
    health_status = dados_originais.get('summary', {}).get('health_status', 'unknown')
    status_map = {
        'healthy': ('healthy', '🟢', 'Saudável'),
        'warning': ('warning', '🟡', 'Atenção Necessária'),
        'critical': ('critical', '🔴', 'Crítico'),
        'unknown': ('warning', '❓', 'Desconhecido')
    }
    
    status_class, status_icon, status_text = status_map.get(health_status, status_map['unknown'])
    
    # Substituir placeholders
    template = template.replace('{{HOSTNAME}}', dados_originais.get('hostname', 'N/A'))
    template = template.replace('{{TIMESTAMP}}', dados_originais.get('timestamp', 'N/A'))
    template = template.replace('{{STATUS_CLASS}}', status_class)
    template = template.replace('{{STATUS_ICON}}', status_icon)
    template = template.replace('{{STATUS_TEXT}}', status_text)
    
    # Métricas cards
    metrics_html = gerar_metrics_cards(analise_json.get('metricas_cards', []))
    template = template.replace('{{METRICS_CARDS}}', metrics_html)
    
    # Resumo executivo
    template = template.replace('{{RESUMO_EXECUTIVO}}', analise_json.get('resumo_executivo', '<p>Análise não disponível.</p>'))
    
    # Alertas
    alertas_html = gerar_alertas_section(analise_json.get('alertas', []))
    template = template.replace('{{ALERTAS_SECTION}}', alertas_html)
    
    # Análises
    template = template.replace('{{ANALISE_DISCOS}}', analise_json.get('analise_discos', '<p>Análise não disponível.</p>'))
    template = template.replace('{{ANALISE_MEMORIA}}', analise_json.get('analise_memoria', '<p>Análise não disponível.</p>'))
    template = template.replace('{{ANALISE_CPU}}', analise_json.get('analise_cpu', '<p>Análise não disponível.</p>'))
    template = template.replace('{{ANALISE_SISTEMA}}', analise_json.get('analise_sistema', '<p>Análise não disponível.</p>'))
    template = template.replace('{{ANALISE_REDE}}', analise_json.get('analise_rede', '<p>Análise não disponível.</p>'))
    template = template.replace('{{ANALISE_LOGS}}', analise_json.get('analise_logs', '<p>Análise não disponível.</p>'))
    
    # Recomendações
    recomendacoes_html = gerar_recomendacoes(analise_json.get('recomendacoes', []))
    template = template.replace('{{RECOMENDACOES}}', recomendacoes_html)
    
    # Conclusão
    template = template.replace('{{CONCLUSAO}}', analise_json.get('conclusao', '<p>Conclusão não disponível.</p>'))
    
    return template


def salvar_html(html_content, json_filepath):
    """Salva o relatório HTML no diretório de saída"""
    
    # Criar diretório de saída se não existir
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Nome do arquivo baseado no JSON original
    json_filename = json_filepath.stem  # health_20251024_143000
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_filename = f"{json_filename}_report_{timestamp}.html"
    html_filepath = OUTPUT_DIR / html_filename
    
    try:
        with open(html_filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_filepath
    except Exception as e:
        print(f"❌ Erro ao salvar HTML: {e}")
        return None


def abrir_no_navegador(filepath):
    """Abre o relatório HTML no navegador padrão"""
    try:
        os.system(f"xdg-open '{filepath}'")
        return True
    except Exception as e:
        print(f"⚠️ Não foi possível abrir automaticamente: {e}")
        return False


def main():
    """Função principal"""
    print("🏥 AI Health Reporter - Análise Inteligente de Saúde do Sistema")
    print("🤖 Powered by Google Gemini")
    print()
    print("Feito por: Montezuma")
    print()
    
    try:
        # 1. Obter último JSON
        print("📂 Procurando relatórios de saúde...")
        json_file = obter_ultimo_json()
        
        if not json_file:
            print("💡 Execute primeiro o health_monitor.py para gerar um relatório!")
            sys.exit(1)
        
        print(f"✅ Relatório encontrado: {json_file.name}")
        
        # 2. Ler JSON
        print("📖 Lendo dados do relatório...")
        dados = ler_json(json_file)
        
        if not dados:
            sys.exit(1)
        
        # Mostrar informações básicas
        hostname = dados.get('hostname', 'N/A')
        timestamp = dados.get('timestamp', 'N/A')
        health_status = dados.get('summary', {}).get('health_status', 'unknown')
        total_alerts = dados.get('summary', {}).get('total_alerts', 0)
        
        print(f"\n📊 Informações do Relatório:")
        print(f"   🖥️  Hostname: {hostname}")
        print(f"   🕐 Timestamp: {timestamp}")
        print(f"   💚 Status: {health_status}")
        print(f"   🚨 Alertas: {total_alerts}")
        
        # 3. Criar prompt
        print("\n🧠 Preparando análise para IA...")
        prompt = criar_prompt_analise(dados)
        
        # 4. Chamar IA para gerar análise em JSON
        analise_json = chamar_gemini(prompt)
        
        if not analise_json:
            print("❌ Falha ao gerar análise")
            sys.exit(1)
        
        print("✅ Análise JSON gerada pela IA!")
        
        # 5. Preencher template HTML com a análise
        print("🎨 Preenchendo template HTML...")
        html_content = preencher_template(analise_json, dados)
        
        if not html_content:
            print("❌ Falha ao gerar HTML do template")
            sys.exit(1)
        
        print("✅ HTML gerado a partir do template!")
        
        # 6. Salvar HTML
        print("\n💾 Salvando relatório HTML...")
        html_file = salvar_html(html_content, json_file)
        
        if not html_file:
            sys.exit(1)
        
        print(f"✅ Relatório salvo em: {html_file}")
        
        # 6. Perguntar se quer abrir
        print("\n" + "="*60)
        print("✨ RELATÓRIO GERADO COM SUCESSO!")
        print("="*60)
        
        while True:
            abrir = input("\n🌐 Abrir relatório no navegador? (s/n): ").strip().lower()
            if abrir in ['s', 'sim', 'y', 'yes']:
                if abrir_no_navegador(html_file):
                    print("✅ Relatório aberto no navegador!")
                else:
                    print(f"\n💡 Abra manualmente: {html_file}")
                break
            elif abrir in ['n', 'nao', 'não', 'no']:
                print(f"\n💡 Você pode abrir depois: {html_file}")
                break
            else:
                print("Digite 's' para sim ou 'n' para não")
        
        print("\n👋 Análise concluída! Até mais!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Programa interrompido pelo usuário!")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
