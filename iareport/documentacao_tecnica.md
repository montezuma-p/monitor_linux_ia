# 🤖 AI Report - Documentação Técnica

## Visão Geral do Sistema

O AI Report é um sistema de análise e geração de relatórios que utiliza inteligência artificial generativa para transformar dados brutos de monitoramento em relatórios humanizados e compreensíveis. Ele consome os JSONs produzidos pelo Health Monitor e gera análises interpretativas em formato HTML, prontas para visualização em navegadores.

## Fundamentos da Arquitetura

### Integração com LLM

O sistema baseia-se na API Gemini do Google, especificamente utilizando o modelo gemini-2.5-flash. A escolha deste modelo equilibra capacidade de análise com velocidade de resposta e custo operacional. O modelo é invocado via SDK oficial `google-genai`, garantindo compatibilidade e acesso às funcionalidades mais recentes.

A autenticação ocorre através de API key configurada como variável de ambiente `GEMINI_API_KEY`. Esta abordagem segue as melhores práticas de segurança, evitando exposição de credenciais no código-fonte e permitindo rotação de chaves sem modificação de código.

### Pipeline de Processamento

O fluxo de processamento segue uma arquitetura pipeline em cinco estágios distintos:

**Descoberta de Dados**: O sistema localiza automaticamente o arquivo JSON mais recente no diretório de entrada. Utiliza timestamps de criação de arquivo para determinar qual relatório processar, eliminando necessidade de intervenção manual.

**Carregamento e Validação**: O JSON é carregado e parseado, com validação básica de estrutura. Erros de formato ou corrupção são detectados nesta fase, prevenindo processamento de dados inválidos.

**Construção de Prompt**: O prompt enviado à LLM é construído de forma estruturada, combinando o JSON de métricas com instruções detalhadas sobre o formato esperado de saída. O prompt inclui contexto sobre o papel da IA (administrador sênior de sistemas Linux), diretrizes de análise e especificação precisa do schema JSON de retorno.

**Invocação da LLM**: O cliente Gemini é invocado com o prompt construído. A resposta é obtida de forma síncrona, bloqueando até conclusão da geração. O sistema não implementa retry automático, assumindo que falhas transitórias são raras com a API Gemini.

**Renderização HTML**: O JSON retornado pela IA é injetado em um template HTML pré-definido através de substituição de placeholders. O resultado é um documento HTML autossuficiente que incorpora CSS inline para garantir renderização consistente sem dependências externas.

## Engenharia de Prompt

O prompt enviado à LLM é meticulosamente elaborado para maximizar qualidade e consistência das respostas. Ele estabelece três componentes fundamentais:

**Persona e Contexto**: Define que a IA deve assumir o papel de um administrador de sistemas Linux experiente, criando um frame mental apropriado para interpretação técnica dos dados. Isso influencia o tom, profundidade e foco da análise gerada.

**Especificação de Saída**: Fornece um schema JSON detalhado que a IA deve seguir na resposta. Isso inclui estrutura de objetos, campos obrigatórios, tipos esperados e exemplos de conteúdo. A especificação é suficientemente prescritiva para garantir parsabilidade, mas flexível o suficiente para permitir criatividade analítica.

**Diretrizes de Análise**: Instruções sobre como interpretar os dados, que aspectos priorizar, como contextualizar números para leigos e quando emitir alertas. Inclui orientações sobre tom (técnico mas acessível), uso de analogias e balanceamento entre completude e concisão.

## Estrutura do Relatório Gerado

O JSON retornado pela IA segue uma estrutura hierárquica com quatro seções principais:

**Resumo Executivo**: Texto corrido de 2-3 parágrafos fornecendo uma visão geral do estado do sistema. Deve ser compreensível para não-técnicos mas suficientemente preciso para técnicos.

**Cartões de Métricas**: Array de objetos representando as métricas mais importantes em formato de cards visuais. Cada card inclui ícone emoji, label descritivo, valor principal destacado e subtexto explicativo.

**Alertas**: Array de alertas identificados pela análise, classificados em críticos e warnings. Cada alerta contém título, descrição detalhada, tipo e recomendações de ação.

**Análise Detalhada por Componente**: Seções dedicadas para cada subsistema (CPU, memória, disco, rede, sistema, logs), contendo análises textuais específicas sobre estado atual, tendências observáveis e observações relevantes.

## Template HTML

O arquivo `template.html` implementa um design responsivo e moderno, utilizando CSS Grid e Flexbox para layout. O styling é completamente autocontido, sem dependências de frameworks CSS externos ou CDNs, garantindo que o relatório seja visualizável offline.

O template utiliza placeholders entre chaves duplas (sintaxe Mustache-like) que são substituídos dinamicamente pelo conteúdo gerado pela IA. Placeholders incluem elementos textuais, arrays que são renderizados como loops e condicionais implícitos através da presença ou ausência de seções.

A renderização de seções repetitivas como cards de métricas e alertas é feita através de concatenação de HTML gerado programaticamente, inserido em containers específicos do template.

## Gerenciamento de Caminhos

O sistema opera com paths relativos ao diretório raiz do projeto, calculados dinamicamente a partir da localização do script. Isso permite que o sistema funcione corretamente independente de onde seja invocado, desde que a estrutura de diretórios do projeto seja mantida.

Três diretórios são relevantes para operação:

- **SCRIPT_DIR**: Diretório onde reside o próprio script reportia.py
- **PROJECT_ROOT**: Raiz do projeto, um nível acima do script
- **REPORTS_DIR**: Diretório de entrada contendo JSONs do Health Monitor
- **OUTPUT_DIR**: Diretório de saída onde HTMLs gerados são salvos

## Tratamento de Erros e Validação

O sistema implementa validação em pontos críticos do pipeline:

**Validação de API Key**: Antes de qualquer processamento, verifica se a variável de ambiente GEMINI_API_KEY está configurada. Ausência resulta em terminação imediata com mensagem clara sobre como configurar.

**Validação de Entrada**: Verifica existência de arquivos JSON no diretório de entrada. Ausência de dados resulta em mensagem informativa e terminação graceful.

**Validação de Parsing**: Erros de parsing JSON (tanto do arquivo de entrada quanto da resposta da IA) são capturados com mensagens específicas sobre a natureza do problema.

**Validação de Diretórios**: Garante que diretórios de saída existam, criando-os automaticamente se necessário.

## Interação com a API Gemini

A comunicação com a API ocorre através do SDK oficial, que abstrai detalhes de protocolo HTTP, autenticação e serialização. O cliente é inicializado uma vez no início da execução e reutilizado para todas as chamadas.

O modelo gemini-2.5-flash é configurado para operar em modo padrão, sem ajustes de temperatura, top-p ou outros hiperparâmetros. Isso prioriza consistência e previsibilidade das respostas.

Não há implementação de streaming - a resposta é aguardada integralmente antes de prosseguir. Para os volumes de dados típicos do Health Monitor, a latência é aceitável (geralmente 2-5 segundos).

## Considerações de Segurança

A API key é mantida fora do código, dependendo de configuração de ambiente. Em ambientes de produção, recomenda-se uso de sistemas de gerenciamento de segredos como HashiCorp Vault ou AWS Secrets Manager.

O sistema não valida ou sanitiza o conteúdo retornado pela IA antes de injetá-lo no HTML. Isso assume confiança no modelo Gemini para não gerar conteúdo malicioso. Em ambientes de alta segurança, seria recomendável implementar sanitização adicional.

## Extensibilidade e Customização

O template HTML pode ser personalizado para refletir identidade visual corporativa, adicionando logos, cores customizadas ou seções adicionais. Desde que os placeholders sejam mantidos, o sistema continuará funcionando normalmente.

O prompt pode ser ajustado para modificar o tom, profundidade ou foco da análise. Mudanças no schema de saída requerem alterações coordenadas entre o prompt e o template HTML.

Integração com outros LLMs é possível substituindo o cliente Gemini por outro compatível, desde que o formato de prompt e parsing de resposta sejam adaptados conforme necessário.

## Performance e Otimização

O principal gargalo de performance é a latência da API Gemini. Para processamento em lote de múltiplos relatórios, seria benéfico implementar processamento paralelo com múltiplas chamadas simultâneas à API, respeitando os rate limits.

O tamanho do prompt enviado é proporcional ao tamanho do JSON de entrada. Para sistemas com coletas muito extensas, pode ser necessário implementar resumo ou filtragem dos dados mais relevantes antes de enviar à LLM.

A geração de HTML via substituição de strings é eficiente para os tamanhos típicos de relatório. Para volumes significativamente maiores, considerar uso de engines de template dedicados como Jinja2.

## Debugging e Troubleshooting

O sistema emite mensagens de status durante execução, permitindo acompanhar o progresso do pipeline. Mensagens incluem identificação do arquivo sendo processado, sucesso/falha de cada etapa e localização do arquivo de saída gerado.

Em caso de falhas na API Gemini, as mensagens de erro são propagadas do SDK, geralmente contendo códigos de status HTTP e descrições textuais do problema. Erros comuns incluem quota excedida, API key inválida ou problemas de conectividade.

Para depuração avançada, pode ser útil salvar o prompt exato enviado à API e a resposta bruta recebida, permitindo análise offline do comportamento do modelo.
