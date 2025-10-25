# 📊 Monitor Completo - Sistema de Monitoramento e Análise Inteligente

## Introdução

Monitor Completo é uma solução integrada de monitoramento de saúde de sistemas Linux que combina coleta automatizada de métricas com análise inteligente baseada em IA. O sistema foi desenvolvido para oferecer visibilidade profunda sobre o estado operacional de servidores e workstations, transformando dados técnicos brutos em insights compreensíveis e acionáveis.

## Justificativa e Motivação

Administradores de sistemas frequentemente enfrentam o desafio de coletar, interpretar e agir sobre grandes volumes de métricas de sistema. Ferramentas tradicionais oferecem dados brutos, mas exigem expertise significativa para interpretação correta e identificação de problemas.

Este projeto nasceu da necessidade de democratizar o acesso à análise de saúde de sistemas, permitindo que tanto especialistas quanto usuários menos técnicos possam compreender o estado de suas máquinas de forma clara e objetiva. Ao combinar coleta automatizada com análise via IA generativa, eliminamos a necessidade de interpretação manual de métricas complexas.

A solução é especialmente relevante para:

- **Equipes pequenas** que não possuem especialistas dedicados em monitoramento
- **Ambientes educacionais** onde transparência e clareza são fundamentais
- **Desenvolvedores** que precisam monitorar ambientes de desenvolvimento sem overhead
- **Entusiastas** que desejam entender melhor o comportamento de seus sistemas

## Arquitetura da Solução

O Monitor Completo é composto por dois módulos principais que trabalham em conjunto:

### Health Monitor

Coletor de métricas que opera de forma não-invasiva, extraindo informações detalhadas sobre:

- Utilização e temperatura de CPU
- Consumo de memória RAM e swap
- Uso de disco, I/O e saúde SMART
- Estatísticas de rede e conectividade
- Logs do sistema e eventos críticos
- Estado de serviços systemd

As métricas são coletadas pontualmente e exportadas em formato JSON estruturado, facilitando processamento posterior e integração com outras ferramentas.

### AI Report

Analisador inteligente que consome os JSONs gerados pelo Health Monitor e utiliza a API Gemini do Google para gerar relatórios HTML humanizados. A IA interpreta as métricas, identifica padrões, destaca anomalias e oferece recomendações contextualizadas em linguagem acessível.

### Fluxo de Operação

1. O Health Monitor é executado e coleta métricas do sistema
2. Um arquivo JSON timestamped é gerado com todos os dados
3. O AI Report processa o JSON mais recente
4. A IA Gemini analisa os dados e gera insights estruturados
5. Um relatório HTML completo é produzido para visualização

## Instalação e Configuração

### Pré-requisitos

- Python 3.8 ou superior
- Sistema operacional Linux (otimizado para Fedora/RHEL)
- Conta Google Cloud com acesso à API Gemini

### Passo 1: Clonar o Repositório

```bash
git clone <url-do-repositorio>
cd monitor_completo
```

### Passo 2: Configurar Ambientes Virtuais

**Para o Health Monitor:**

```bash
cd health_monitor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..
```

**Para o AI Report:**

```bash
cd iareport
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..
```

### Passo 3: Obter API Key do Gemini

1. Acesse [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Crie ou selecione um projeto
3. Gere uma nova API key
4. Copie a chave gerada

### Passo 4: Configurar Variável de Ambiente

Adicione a API key ao seu arquivo `~/.bashrc` para persistência entre sessões:

```bash
echo 'export GEMINI_API_KEY="sua_chave_aqui"' >> ~/.bashrc
source ~/.bashrc
```

**Alternativa temporária (válida apenas para a sessão atual):**

```bash
export GEMINI_API_KEY="sua_chave_aqui"
```

### Passo 5: Verificar Configuração

Confirme que a variável está configurada corretamente:

```bash
echo $GEMINI_API_KEY
```

Deve exibir sua API key.

### Passo 6: Configurar Parâmetros (Opcional)

Edite `health_monitor/config.json` para ajustar thresholds de alerta, habilitar/desabilitar funcionalidades específicas ou modificar diretórios de saída.

## Uso

### Execução Manual Individual

**Health Monitor:**

```bash
cd health_monitor
source venv/bin/activate
python3 health_monitor.py
deactivate
```

**AI Report:**

```bash
cd iareport
source venv/bin/activate
python3 reportia.py
deactivate
```

### Execução Automatizada Completa

Um script orquestrador está disponível na raiz do projeto para executar todo o pipeline automaticamente:

```bash
chmod +x run.sh  # Apenas na primeira vez
./run.sh
```

O script `run.sh` irá:

1. Executar o Health Monitor para coletar métricas atuais
2. Executar o AI Report para gerar análise do último JSON
3. Exibir mensagem com localização dos arquivos gerados

### Automação via Cron

Para monitoramento periódico, adicione ao crontab:

```bash
# Executar a cada 6 horas
0 */6 * * * /caminho/completo/para/monitor_completo/run.sh

# Executar diariamente às 9h
0 9 * * * /caminho/completo/para/monitor_completo/run.sh
```

## Estrutura de Diretórios

```
monitor_completo/
├── health_monitor/              # Módulo coletor de métricas
│   ├── modules/                 # Módulos especializados por categoria
│   ├── venv/                    # Ambiente virtual Python
│   ├── config.json              # Configurações e thresholds
│   ├── health_monitor.py        # Script principal
│   ├── requirements.txt         # Dependências Python
│   └── documentacao_tecnica.md  # Documentação técnica detalhada
├── iareport/                    # Módulo de análise por IA
│   ├── venv/                    # Ambiente virtual Python
│   ├── reportia.py              # Script principal
│   ├── template.html            # Template do relatório HTML
│   ├── requirements.txt         # Dependências Python
│   └── documentacao_tecnica.md  # Documentação técnica detalhada
├── exemplosdesaida/             # Diretório de saídas
│   ├── saidasraw/               # JSONs brutos do Health Monitor
│   └── saidascomia/             # Relatórios HTML do AI Report
├── run.sh                       # Script orquestrador
└── README.md                    # Esta documentação
```

## Saídas Geradas

### JSONs Brutos (exemplosdesaida/saidasraw/)

Arquivos nomeados como `health_YYYYMMDD_HHMMSS.json` contendo:

- Metadados de coleta
- Métricas categorizadas por componente
- Alertas gerados com base em thresholds
- Timestamps precisos de coleta

### Relatórios HTML (exemplosdesaida/saidascomia/)

Arquivos nomeados como `report_YYYYMMDD_HHMMSS.html` contendo:

- Resumo executivo em linguagem clara
- Cards visuais com métricas principais
- Alertas críticos destacados
- Análise detalhada por componente
- Recomendações de ação quando aplicável

## Personalização

### Ajustar Thresholds de Alerta

Edite `health_monitor/config.json` e modifique os valores em `thresholds`:

```json
{
  "thresholds": {
    "disk_usage_warning": 80,
    "disk_usage_critical": 90,
    "memory_usage_warning": 80,
    "cpu_temp_warning": 70
  }
}
```

### Modificar Visual dos Relatórios

Edite `iareport/template.html` para customizar cores, fontes, logo ou estrutura das seções HTML.

### Desabilitar Funcionalidades

No `config.json`, seção `monitoring`, ajuste flags booleanas:

```json
{
  "monitoring": {
    "check_smart": false,
    "check_systemd_services": true,
    "check_journal_errors": true
  }
}
```

## Solução de Problemas

### "GEMINI_API_KEY não encontrada"

Verifique se a variável foi exportada corretamente:
```bash
echo $GEMINI_API_KEY
```

Se vazia, configure novamente no `~/.bashrc` e execute `source ~/.bashrc`.

### "Nenhum relatório encontrado"

Execute primeiro o Health Monitor para gerar um JSON antes de rodar o AI Report.

### Permissão negada no run.sh

Torne o script executável:
```bash
chmod +x run.sh
```

### Módulo psutil não encontrado

Ative o ambiente virtual correto antes de executar:
```bash
source health_monitor/venv/bin/activate
```

### Erro de API do Gemini

Verifique:
- API key válida e com quota disponível
- Conectividade com internet
- Projeto Google Cloud ativo

## Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça fork do repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob os termos descritos no arquivo LICENSE.

## Créditos

Desenvolvido por Montezuma

Utiliza:
- **psutil** para coleta de métricas do sistema
- **Google Gemini API** para análise inteligente
- Template HTML com design responsivo moderno

## Suporte

Para questões, bugs ou sugestões, abra uma issue no repositório do projeto.
