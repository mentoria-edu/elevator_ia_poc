# Plano de Implementação: Garbage Collector do Repositório

## Objetivo

Implementar um Garbage Collector para inspeção e manutenção controlada do
repositório. A ferramenta deve localizar artefatos possivelmente obsoletos,
registrar o estado encontrado e gerar relatórios para revisão humana.

A ferramenta não pode excluir, sobrescrever ou mover arquivos automaticamente.

## Resultado esperado

Permitir executar:

    uv run python -m tools.garbage_collector scan
    uv run python -m tools.garbage_collector inventory
    uv run python -m tools.garbage_collector report
    uv run python -m tools.garbage_collector check

O comando check deve executar o fluxo completo:

1. Ler o arquivo de regras e confirmar que ele existe, contém YAML válido,
   possui a estrutura esperada e não contém regras inválidas ou duplicadas.
2. Ler o arquivo de exceções e confirmar que ele existe, contém YAML válido,
   possui a estrutura esperada e que cada registro contém `path`, `reason`,
   `owner` e `removal_condition` válidos. Também deve rejeitar registros
   duplicados, caminhos inexistentes, caminhos fora da raiz do projeto e
   campos de expiração, que não fazem parte do formato suportado.
3. Varrer o repositório.
4. Atualizar o inventário.
5. Gerar o relatório Markdown.
6. Retornar código de saída apropriado.

## Definição operacional das validações

Os termos “validar”, “verificar” e “processar” neste plano possuem os
significados abaixo. A implementação deve cumprir todos os itens; não cabe ao
agente escolher uma interpretação mais ampla ou mais restrita.

### 1. Validação das regras

Antes da varredura, o sistema deve ler o arquivo de regras e rejeitá-lo quando
qualquer uma das condições abaixo ocorrer:

- o arquivo não existir;
- o YAML for inválido;
- o documento raiz não for um mapa/objeto;
- `version` não existir ou não for um inteiro suportado;
- `rules` não existir ou não for uma lista;
- uma regra não for um mapa/objeto;
- `id` não existir, não for texto ou estiver duplicado;
- `description` não existir ou não for texto não vazio;
- `severity` não for uma das severidades suportadas: `none`, `warning` ou
  `error`;
- `action` não for uma ação suportada: `review`;
- a regra não declarar ao menos um critério de localização (`path` ou
  `patterns`);
- `extensions`, quando informado, não for uma lista de extensões de texto;
- `patterns`, quando informado, não for uma lista de padrões de texto;
- `max_age_days`, quando informado, não for um inteiro maior ou igual a zero;
- `tracked_only`, quando informado, não for booleano;
- o caminho configurado for absoluto ou escapar da raiz do projeto.

O resultado da validação deve ser explícito:

- configuração válida: continuar a execução;
- configuração inválida: informar cada erro encontrado, não executar a
  varredura e retornar código de saída diferente de zero.

A validação não deve corrigir, completar ou reescrever automaticamente o
arquivo de regras.

### 2. Validação das exceções

Antes da varredura, o sistema deve ler
`docs/garbage-collector/exceptions/active-exceptions.yml` e verificar, para
cada exceção:

- o arquivo de exceções existir;
- o YAML ser válido;
- o documento raiz possuir `version` e `exceptions`;
- `exceptions` ser uma lista;
- cada item possuir `path`, `reason`, `owner` e `removal_condition`;
- todos esses campos serem textos não vazios;
- nenhum item possuir o campo `expires_at` ou qualquer outro campo de
  expiração;
- `path` ser relativo à raiz do projeto e não escapar dela;
- o caminho referenciado existir no momento da execução;
- não existirem dois registros para o mesmo `path`;
- cada exceção válida ser registrada como ativa indefinidamente, até que seu
  registro seja removido explicitamente;
- uma exceção inválida não ser usada para ocultar candidatos da varredura.

O resultado deve seguir estas regras:

- todas as exceções válidas: continuar a execução e mantê-las ativas;
- exceção incompleta, malformada, duplicada, com caminho inexistente ou com
  campo de expiração: informar erro de configuração, não tratá-la como
  exceção válida e retornar código diferente de zero;
- arquivo de exceções ausente: tratar como configuração inválida, exceto se
  houver uma opção explícita de permitir arquivo vazio.

A validação das exceções não remove registros nem altera o arquivo
`active-exceptions.yml`.

### 3. Validação da raiz e dos caminhos

Antes de analisar os artefatos, o sistema deve:

- resolver `--project-root` ou usar o diretório atual;
- confirmar que a raiz existe e é um diretório;
- resolver todos os caminhos configurados relativamente à raiz;
- rejeitar caminhos absolutos ou que usem `..` para sair da raiz;
- manter os caminhos registrados em formato relativo e normalizado;
- ignorar diretórios e arquivos excluídos explicitamente pela configuração do
  projeto, quando essa configuração existir;
- não seguir links simbólicos para fora da raiz do projeto.

Falha em qualquer uma dessas verificações deve interromper a execução antes
de gravar inventário ou relatório.

### 4. Validação da varredura

Para cada regra habilitada, o sistema deve aplicar exatamente os critérios
declarados no YAML:

- `path` limita a busca ao caminho configurado;
- `extensions` limita a busca às extensões informadas;
- `patterns` compara os nomes relativos conforme o padrão configurado;
- `max_age_days` compara a última modificação com a data de referência;
- `tracked_only: true` restringe a regra a caminhos versionados pelo Git;
- exceções válidas e vigentes impedem apenas o candidato correspondente ao
  mesmo `path` e não alteram os demais resultados;
- nenhum arquivo é considerado obsoleto apenas por estar sem referências
  encontradas pelo scanner;
- nenhum candidato é removido, movido, renomeado ou reescrito.

Cada candidato deve conter evidência suficiente para revisão humana: caminho,
regra aplicada, motivo, severidade, ação recomendada e, quando aplicável,
data de modificação, idade calculada e padrão que produziu o resultado.

### 5. Validação do inventário

Ao gerar o inventário, o sistema deve verificar que:

- todas as entradas possuem os campos exigidos pelo modelo de dados;
- os caminhos são relativos, normalizados e únicos;
- cada `rule_id` referencia uma regra carregada;
- cada severidade e status pertence ao conjunto permitido;
- entradas idênticas são ordenadas sempre da mesma forma;
- `inventory.yml` representa apenas a execução atual;
- o arquivo histórico é criado sem substituir históricos anteriores;
- a serialização pode ser lida novamente pelo próprio sistema.

O inventário não pode afirmar que um artefato deve ser removido. Ele deve
registrá-lo somente como candidato à revisão.

### 6. Validação do relatório

O relatório deve ser considerado válido somente quando contiver:

- data e hora da execução;
- raiz do projeto analisada;
- versão das regras;
- quantidade total de arquivos analisados;
- quantidade de candidatos;
- quantidade de resultados `error` e `warning`;
- tabela com caminho, regra, severidade, motivo e ação recomendada;
- evidências de cada candidato;
- indicação explícita de erros de configuração, quando existirem;
- próximos passos sem instrução de exclusão automática.

O conteúdo deve ser determinístico: mesma entrada, mesma data de referência e
mesma versão das regras devem produzir o mesmo relatório, exceto pela
informação de horário de execução quando ela for obrigatoriamente registrada.

### 7. Validação de mutações permitidas

Depois de cada comando, o sistema deve garantir que somente os destinos
permitidos foram alterados:

- `inventory.yml`;
- arquivos em `inventory/history/`;
- arquivos em `reports/`.

Qualquer tentativa de alterar outro caminho deve ser bloqueada e reportada
como erro. A implementação não deve conter fluxo que invoque exclusão,
movimentação ou renomeação de arquivos do repositório.

## Escopo

### Incluído

- ExecPlans ativos sem atualização recente;
- exceções ativas e configuráveis;
- arquivos temporários versionados;
- relatórios antigos;
- inventário atual e histórico;
- relatórios Markdown determinísticos;
- exceções configuráveis;
- testes unitários;
- interface de linha de comando.

### Não incluído

- exclusão ou movimentação automática;
- análise semântica completa do código;
- uso de uma LLM como validador;
- decisão automática de que um arquivo está obsoleto;
- alteração automática de ExecPlans, ADRs ou outros documentos.

## Estrutura de arquivos

Reutilizar arquivos equivalentes já existentes. Criar ou completar:

    docs/
    └── garbage-collector/
        ├── README.md
        ├── schedule.md
        ├── rules/
        │   └── default-rules.yml
        ├── inventory/
        │   ├── inventory.yml
        │   └── history/
        ├── reports/
        │   ├── README.md
        │   └── .gitkeep
        └── exceptions/
            └── active-exceptions.yml

    tools/
    ├── __init__.py
    └── garbage_collector/
        ├── __init__.py
        ├── __main__.py
        ├── cli.py
        ├── models.py
        ├── configuration.py
        ├── rules.py
        ├── scan.py
        ├── inventory.py
        ├── output_paths.py
        └── report.py

    tests/
    └── garbage_collector/
        ├── test_configuration.py
        ├── test_rules.py
        ├── test_scan.py
        ├── test_inventory.py
        ├── test_report.py
        └── test_cli.py

Respeitar AGENTS.md, ARCHITECTURE.md, PLANS.md e docs/standards/.

## Regras iniciais

Declarar as regras em docs/garbage-collector/rules/default-rules.yml.

Formato inicial:

    version: 1
    rules:
      - id: stale-active-exec-plan
        description: ExecPlan ativo sem atualização recente
        path: docs/exec-plans/active
        extensions: [.md]
        max_age_days: 30
        severity: warning
        action: review

      - id: tracked-temporary-file
        description: Arquivo temporário versionado
        patterns: ["*.tmp", "*.bak", "*.log", "*.pyc", "__pycache__", ".DS_Store"]
        tracked_only: true
        severity: warning
        action: review

      - id: stale-report
        description: Relatório antigo que pode ser arquivado
        path: docs/garbage-collector/reports
        patterns: ["????-??-??-scan.md"]
        extensions: [.md]
        max_age_days: 90
        severity: warning
        action: review

As regras devem ser configuração, não critérios duplicados em módulos Python.

## Exceções

Usar `docs/garbage-collector/exceptions/active-exceptions.yml`.

Cada exceção deve possuir `path`, `reason`, `owner` e
`removal_condition`. Exceções permanecem ativas indefinidamente e só deixam
de ser consideradas quando forem removidas explicitamente do arquivo:

    version: 1
    exceptions:
      - path: src/legacy_adapter.py
        reason: Mantido por compatibilidade com consumidor externo
        owner: equipe-do-projeto
        removal_condition: Remover após a migração externa

O arquivo não deve possuir `expires_at` nem qualquer outro campo de expiração.
Exceções sem prazo de expiração são válidas por definição. A remoção de uma
exceção deve ser uma alteração explícita e revisada do arquivo.

## Modelo de dados

Criar tipos explícitos para:

- regra de inspeção;
- exceção ativa;
- candidato encontrado;
- resultado da varredura;
- entrada do inventário;
- relatório da execução.

Evitar Any, dicionários genéricos e strings soltas para severidade, status ou
tipo de artefato. Usar enums ou tipos próprios quando apropriado.

Cada candidato deve registrar:

- path;
- rule_id;
- description;
- severity;
- recommended_action;
- last_modified, quando aplicável;
- evidence.

## Inventário

Gravar o inventário atual em:

    docs/garbage-collector/inventory/inventory.yml

Gerar uma cópia histórica em:

    docs/garbage-collector/inventory/history/YYYY-MM-DDTHHMMSSZ.yml

O inventário deve descrever o estado observado. Ele não deve declarar que um
arquivo pode ser removido; deve apenas registrar que ele é candidato à revisão.

## Relatórios

Gerar relatórios em:

    docs/garbage-collector/reports/YYYY-MM-DD-scan.md

O relatório deve conter data, quantidade de arquivos analisados, quantidade de
candidatos, erros, warnings, versão das regras, tabela de candidatos, evidências
e próximos passos.

Ordenar os candidatos por caminho e depois por rule_id. A mesma entrada deve
produzir o mesmo conteúdo, desconsiderando timestamps de execução.

## Interface de linha de comando

Implementar:

- scan: varre sem gravar inventário ou relatório;
- inventory: varre e grava o inventário;
- report: gera relatório;
- check: executa o fluxo completo.

Requisitos:

- aceitar --project-root e usar o diretório atual por padrão;
- permitir caminhos alternativos para regras e exceções;
- imprimir mensagens simples para o usuário;
- retornar código diferente de zero para configuração inválida;
- separar saída de usuário de logs estruturados;
- implementar --fail-on error e --fail-on warning somente se ambos forem testados.

Exemplos:

    uv run python -m tools.garbage_collector scan
    uv run python -m tools.garbage_collector check --project-root .
    uv run python -m tools.garbage_collector check --fail-on warning

## Segurança e limites de mutação

A ferramenta só pode gravar:

- inventory.yml;
- arquivos em inventory/history/;
- relatórios em reports/.

Não usar unlink, remove, rmtree, rename ou equivalentes para alterar outros
arquivos. Não executar comandos Git destrutivos.

Antes de alterar regras, exceções ou resultados, criar ou atualizar um ExecPlan
e obter a aprovação exigida pelo projeto. Para decisões arquiteturais ou de
alto impacto, registrar também a decisão em um ADR, quando aplicável.

## Ordem de implementação

### Etapa 1 — Diagnóstico

1. Ler os arquivos de instrução e standards.
2. Verificar estrutura existente e configurações Python.
3. Identificar ferramentas instaladas.
4. Reutilizar convenções existentes.
5. Registrar conflitos antes de modificar arquivos.

### Etapa 2 — Configuração e modelos

1. Criar ou validar os YAMLs.
2. Implementar carregamento e validação.
3. Criar modelos tipados.
4. Testar YAML válido, inválido e campos obrigatórios.

### Etapa 3 — Varredura

1. Detectar ExecPlans obsoletos.
2. Carregar e aplicar as exceções ativas aos candidatos encontrados.
3. Detectar arquivos temporários versionados.
4. Detectar relatórios antigos.
5. Ordenar resultados deterministicamente.
6. Confirmar que a varredura não altera artefatos.

### Etapa 4 — Inventário e relatório

1. Serializar o inventário.
2. Gravar estado atual.
3. Criar histórico com timestamp UTC.
4. Gerar Markdown.
5. Testar conteúdo, ordenação e caminhos.

### Etapa 5 — CLI

1. Implementar subcomandos.
2. Conectar serviços internos.
3. Implementar códigos de saída.
4. Testar argumentos válidos e inválidos.
5. Testar que não há exclusões ou movimentações.

### Etapa 6 — Documentação e integração

1. Documentar uso em docs/garbage-collector/README.md.
2. Documentar agendamento em schedule.md.
3. Documentar relatórios.
4. Atualizar AGENTS.md com o fluxo de segurança.
5. Executar formatter, linter e testes.

## Testes obrigatórios

- regra válida é carregada e permite continuar a execução;
- arquivo de regras ausente, YAML inválido ou estrutura raiz inválida é
  rejeitado;
- regra sem identificador, com identificador duplicado ou com campo obrigatório
  ausente é rejeitada;
- regra com severidade, ação, critério de localização ou idade inválidos é
  rejeitada;
- caminho absoluto ou caminho que escapa da raiz do projeto é rejeitado;
- arquivo de exceções ausente, YAML inválido ou estrutura raiz inválida é
  rejeitado;
- exceção sem `path`, `reason`, `owner` ou `removal_condition` é rejeitada;
- exceção com `expires_at` ou outro campo de expiração é rejeitada;
- exceção com caminho inexistente ou caminho duplicado é rejeitada;
- exceção vigente e completa é aceita e impede somente o candidato do mesmo
  caminho;
- exceção válida permanece ativa até ser removida explicitamente do arquivo;
- ExecPlan dentro do prazo não é reportado;
- ExecPlan fora do prazo é reportado;
- arquivo temporário não versionado não é reportado;
- relatório antigo é identificado;
- raiz inexistente ou que não seja diretório é rejeitada;
- caminhos registrados no resultado são relativos, normalizados e únicos;
- candidatos são ordenados deterministicamente;
- candidato contém regra, motivo, severidade, ação e evidência;
- inventário atual e histórico são gerados;
- histórico anterior não é sobrescrito;
- inventário pode ser lido novamente;
- relatório contém estatísticas corretas;
- relatório contém todos os campos obrigatórios e não recomenda exclusão
  automática;
- CLI retorna erro para configuração inválida;
- CLI não exclui nem move arquivos;
- tentativa de alterar caminho fora dos destinos permitidos é bloqueada;
- execução repetida produz resultados equivalentes, desconsiderando timestamps.

Usar fake classes nomeadas para filesystem, relógio ou Git quando essas
dependências precisarem ser isoladas.

## Critérios de aceitação

O plano estará concluído quando:

- `uv run python -m tools.garbage_collector check` funcionar em um repositório
  válido;
- configurações inválidas produzirem mensagens claras;
- exceções válidas forem mantidas ativas até sua remoção explícita;
- ExecPlans antigos forem identificados conforme a configuração;
- inventário e relatório forem gravados nos diretórios previstos;
- resultados forem determinísticos;
- todos os testes passarem com um único comando;
- Ruff e demais validadores passarem;
- nenhum arquivo fora das saídas permitidas for modificado;
- não existir caminho de exclusão automática;
- a documentação estiver atualizada.

## Validação final

Executar, adaptando os comandos à configuração efetiva:

    uv run --group dev ruff check .
    uv run --group dev ruff format --check .
    uv run --group dev pytest tests/garbage_collector/
    uv run python -m tools.garbage_collector check
    git diff --check
    git status --short

Verificar manualmente se os arquivos alterados estão no escopo, se nenhum
artefato foi removido, movido ou renomeado, se os códigos de saída correspondem
às condições documentadas, se relatórios apenas sugerem revisão e se alterações
estruturais adicionais foram registradas em ExecPlan ou ADR, quando aplicável.

Registrar no resultado da validação final:

- comando executado;
- resultado (`pass` ou `fail`);
- mensagem de erro, quando houver;
- arquivos modificados;
- confirmação de que nenhum arquivo fora dos destinos permitidos foi alterado;
- confirmação de que não houve exclusão, movimentação ou renomeação automática.
