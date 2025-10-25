# 📊 Health Monitor - Documentação Técnica

## Visão Geral do Sistema

O Health Monitor é um sistema de monitoramento de saúde desenvolvido em Python para ambientes Linux, especialmente otimizado para Fedora Workstation. Trata-se de um coletor de métricas de sistema que opera de forma não-invasiva, gerando saídas estruturadas em formato JSON para posterior análise e processamento.

## Arquitetura do Sistema

### Estrutura Modular

O sistema foi projetado seguindo o princípio de responsabilidade única, onde cada módulo possui uma função específica e bem delimitada. A arquitetura modular permite fácil manutenção, extensibilidade e testes isolados de cada componente.

O núcleo do sistema reside no arquivo principal `health_monitor.py`, que atua como orquestrador das coletas. Ele coordena a execução sequencial de todos os módulos coletores, agregando os resultados em uma estrutura de dados unificada.

### Módulos de Coleta

O diretório `modules` contém seis módulos especializados, cada um responsável por uma categoria específica de métricas:

**CPU (`cpu.py`)**: Realiza a coleta de métricas relacionadas ao processador, incluindo percentual de uso global e por núcleo, frequências operacionais, temperatura dos sensores térmicos e carga média do sistema em diferentes janelas temporais. A normalização da carga considera o número de núcleos disponíveis para fornecer uma visão proporcional da utilização.

**Memória (`memory.py`)**: Monitora o estado da memória RAM e swap do sistema. Coleta informações sobre total disponível, utilização atual, buffers, cache e pressão de memória. Fornece dados tanto em valores absolutos quanto percentuais, facilitando análises de tendência.

**Disco (`disk.py`)**: Responsável pela coleta de métricas de armazenamento, incluindo uso de partições, operações de I/O, latências, throughput e estatísticas SMART quando disponíveis. Permite identificação precoce de problemas em dispositivos de armazenamento através da análise de saúde SMART.

**Rede (`network.py`)**: Monitora interfaces de rede, coletando estatísticas de tráfego, pacotes transmitidos e recebidos, erros de transmissão, drops e estado de conectividade. Pode executar testes de conectividade com hosts externos configuráveis para validar a saúde da rede.

**Sistema (`system.py`)**: Coleta informações sobre o sistema operacional, kernel, hostname, uptime, processos em execução e informações de hardware. Fornece o contexto necessário para interpretar as demais métricas.

**Logs (`logs.py`)**: Integra-se com o systemd journal para extrair eventos relevantes do sistema. Filtra mensagens de erro, warnings e eventos críticos em uma janela temporal configurável, permitindo correlação entre anomalias métricas e eventos do sistema.

### Sistema de Alertas

O módulo `alerts.py` implementa um motor de regras baseado em thresholds configuráveis. Ele avalia cada métrica coletada contra valores limites definidos no arquivo de configuração, gerando alertas classificados em níveis de severidade: warning (aviso) e critical (crítico).

O sistema de alertas opera de forma reativa, processando as métricas já coletadas e aplicando lógica de negócio para determinar condições que requerem atenção. Cada alerta gerado contém contexto suficiente para diagnóstico, incluindo a métrica afetada, valor atual, threshold violado e componente relacionado.

## Fluxo de Execução

A execução do sistema segue um pipeline bem definido:

1. **Inicialização**: Carregamento do arquivo de configuração JSON, validação de parâmetros e preparação do ambiente de execução.

2. **Coleta Sequencial**: Cada módulo é invocado sequencialmente, executando suas rotinas de coleta específicas. O sistema implementa tratamento de exceções por módulo, garantindo que falhas isoladas não comprometam toda a coleta.

3. **Agregação**: As métricas coletadas são agregadas em uma estrutura de dados hierárquica, preservando a organização por categoria.

4. **Análise de Alertas**: O motor de alertas processa todas as métricas coletadas, aplicando as regras de threshold e gerando alertas quando necessário.

5. **Metadados**: Adiciona informações contextuais ao relatório, como timestamp de coleta, versão do sistema e hostname.

6. **Serialização**: A estrutura completa é serializada em JSON com formatação legível, incluindo indentação e ordenação de chaves para facilitar inspeção manual.

7. **Persistência**: O arquivo JSON é gravado no diretório de saída configurado, com nomenclatura baseada em timestamp para permitir séries temporais.

## Sistema de Configuração

O arquivo `config.json` centraliza todos os parâmetros operacionais do sistema. Ele define o diretório de saída para os relatórios, os thresholds para geração de alertas e flags de controle para habilitar ou desabilitar funcionalidades específicas.

A estrutura de configuração é hierárquica, agrupando parâmetros relacionados. Os thresholds são definidos por métrica e por nível de severidade, permitindo ajuste fino do comportamento do sistema de alertas.

O bloco de monitoring controla funcionalidades opcionais como verificação SMART de discos, análise de serviços systemd, extração de erros do journal e testes de conectividade de rede. Isso permite adaptar o sistema para diferentes cenários de uso, desde ambientes de desenvolvimento até servidores de produção.

## Dependências e Requisitos

O sistema possui dependência mínima externa, utilizando principalmente a biblioteca `psutil` para acesso às métricas do sistema operacional. Esta biblioteca fornece uma interface multiplataforma para informações de sistema, processos, disco, rede e sensores.

Para funcionalidades avançadas como leitura SMART de discos, o sistema invoca utilitários externos do sistema operacional através de subprocess, como `smartctl`. A detecção de ausência dessas ferramentas é feita gracefully, registrando warnings mas não interrompendo a execução.

## Formato de Saída

O JSON gerado possui uma estrutura previsível e bem documentada, facilitando consumo por sistemas downstream. A raiz contém um objeto `metadata` com informações contextuais, seguido de objetos para cada categoria de métrica (`cpu`, `memory`, `disk`, `network`, `system`, `logs`) e um array `alerts` com todos os alertas gerados.

Cada categoria de métrica possui sua própria estrutura interna, otimizada para representar os dados específicos daquele domínio. Valores numéricos são arredondados para precisão apropriada, evitando ruído desnecessário nos dados.

## Considerações de Desempenho

O sistema foi projetado para ter overhead mínimo. As coletas são pontuais, não mantendo processos em background. O intervalo de amostragem para métricas como uso de CPU é configurado para ser curto o suficiente para capturar o estado atual, mas longo o suficiente para não introduzir overhead significativo.

A arquitetura modular permite que módulos computacionalmente caros sejam desabilitados via configuração quando não necessários, otimizando o tempo de execução em ambientes com requisitos específicos.

## Extensibilidade

Adicionar novas categorias de métricas é trivial devido à arquitetura modular. Basta criar um novo módulo no diretório `modules` seguindo a interface estabelecida: uma função principal que recebe a configuração e retorna um dicionário com as métricas coletadas.

O sistema de alertas também é extensível, permitindo adicionar novas regras de análise sem modificar os módulos de coleta. Isso mantém a separação clara entre coleta de dados e análise de dados.

## Tratamento de Erros

O sistema implementa tratamento de erros em múltiplas camadas. Falhas em módulos individuais são capturadas e registradas, mas não interrompem a execução dos demais módulos. Erros críticos que impedem a operação normal, como impossibilidade de gravar o arquivo de saída, resultam em terminação controlada com mensagem apropriada.

Quando um módulo falha, o campo correspondente no JSON de saída contém um objeto `error` com descrição do problema, permitindo diagnóstico posterior e garantindo que a estrutura do JSON permaneça válida.
