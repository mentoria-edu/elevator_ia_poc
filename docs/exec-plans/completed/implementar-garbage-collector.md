# Implementar o Garbage Collector do repositório

Este ExecPlan é um documento vivo. As seções `Progresso`, `Surpresas e Descobertas`, `Registro de Decisões` e `Resultados e Retrospectiva` devem ser mantidas atualizadas durante a execução do trabalho.

Este documento deve ser mantido de acordo com `PLANS.md`.

## Propósito / Visão geral

Quem mantém o repositório poderá executar uma ferramenta local para identificar arquivos que merecem revisão, registrar o estado encontrado e produzir um relatório legível sem permitir exclusão ou movimentação automática. A entrega estará comprovada quando a interface `uv run python -m tools.garbage_collector` oferecer os subcomandos `scan`, `inventory`, `report` e `check`, configurações inválidas forem rejeitadas com mensagens claras, os resultados forem determinísticos e somente inventários e relatórios puderem ser gravados.

## Progresso

- [x] (2026-07-25 00:00Z) Lidos a proposta, a arquitetura, os padrões e a estrutura inicial da ferramenta.
- [x] (2026-07-25 00:00Z) Decididos o parser YAML, o contrato da CLI, o agendamento manual e a geração dos primeiros artefatos.
- [x] (2026-07-25 18:00Z) Adicionados PyYAML e seus stubs tipados; implementados modelos e configuração.
- [x] (2026-07-25 18:00Z) Implementadas a varredura segura, o inventário, o relatório e a CLI.
- [x] (2026-07-25 18:00Z) Atualizadas regras e documentação acionável para usar uv.
- [x] (2026-07-25 18:05Z) Criados 40 testes novos; o conjunto completo aprovou 44 testes, Ruff e Mypy.
- [x] (2026-07-25 18:05Z) Executado o `check` real, que analisou 62 arquivos, não encontrou candidatos e gerou somente inventário, histórico e relatório.
- [x] (2026-07-25 18:10Z) Aprovados Ruff, formatação, Mypy, 44 testes, validador de ExecPlans, lockfile, varredura real e `git diff --check`; plano pronto para arquivamento.

## Surpresas e Descobertas

- Observação: a proposta inicial declara uma regra `expired-exception`, mas também proíbe qualquer campo de expiração e define que exceções permanecem ativas indefinidamente.
  Evidência: as seções “Validação das exceções”, “Regras iniciais” e “Exceções” da proposta descrevem contratos incompatíveis.

- Observação: a estrutura já reserva os módulos `scan.py`, `inventory.py` e `report.py`, porém eles contêm apenas docstrings e o ponto de entrada atual apenas informa que não existem regras.
  Evidência: os arquivos em `tools/garbage_collector/` não implementam varredura ou persistência.

- Observação: PyYAML não distribui anotações reconhecidas pelo Mypy usado no projeto.
  Evidência: a primeira análise retornou `Library stubs not installed for "yaml"`; `types-PyYAML==6.0.12.20260518` resolveu a verificação.

- Observação: registrar a raiz absoluta tornaria inventário e relatório diferentes entre clones equivalentes.
  Evidência: a primeira execução incluiu `/home/leoadelmo/elevator_vibe_code`; a serialização final usa `.` para representar a raiz selecionada.

## Registro de Decisões

- Decisão: usar `PyYAML==6.0.3` com `safe_load` e `safe_dump`.
  Justificativa: a versão possui suporte ao Python 3.14 e evita manter um parser YAML próprio.
  Data/Autor: 2026-07-25 / Codex

- Decisão: remover a regra `expired-exception` do conjunto inicial.
  Justificativa: exceções com prazo são inválidas e exceções válidas só expiram por remoção explícita; portanto, a regra nunca poderia receber uma entrada válida.
  Data/Autor: 2026-07-25 / Codex

- Decisão: manter a execução recorrente manual nesta primeira versão.
  Justificativa: entrega a ferramenta e seus controles de segurança sem introduzir persistência ou permissões em um workflow remoto.
  Data/Autor: 2026-07-25 / Codex

- Decisão: usar Git para enumerar arquivos rastreados e não ignorados.
  Justificativa: `git ls-files` respeita a configuração do repositório e permite distinguir regras aplicáveis somente a arquivos versionados.
  Data/Autor: 2026-07-25 / Codex

- Decisão: representar a raiz analisada como `.` nas saídas versionáveis.
  Justificativa: o caminho continua significando a raiz selecionada por `--project-root` sem registrar uma localização específica da máquina.
  Data/Autor: 2026-07-25 / Codex

## Resultados e Retrospectiva

Os quatro subcomandos, a configuração declarativa, a integração Git, os modelos tipados e os escritores protegidos foram implementados. O conjunto completo aprovou 44 testes. A execução real de `check` analisou 62 arquivos, encontrou zero candidatos e gerou `inventory.yml`, um histórico e o relatório diário; a varredura final analisou 64 arquivos e também encontrou zero candidatos.

Ruff, a verificação de formatação, Mypy, Pytest, o validador de ExecPlans, `uv lock --check` e `git diff --check` foram aprovados. O Pytest emitiu apenas o aviso esperado de que não coletou cobertura em `src/`, pois esta entrega modifica a ferramenta em `tools/` e a configuração existente mede exclusivamente o pacote da aplicação.

## Contexto e Orientação

O Garbage Collector é uma ferramenta de manutenção em `tools/garbage_collector/`; não faz parte do domínio da aplicação em `src/elevator_vibe_code/`. Suas configurações e saídas ficam em `docs/garbage-collector/`, e seus testes pertencem a `tests/garbage_collector/`. “Candidato” significa um caminho que uma regra marcou para revisão humana, nunca uma autorização para remoção. O projeto usa Python 3.14.5 e todos os comandos Python e de qualidade devem ser executados por `uv`.

As regras são carregadas de `docs/garbage-collector/rules/default-rules.yml`. Exceções ativas ficam em `docs/garbage-collector/exceptions/active-exceptions.yml`. O inventário atual fica em `docs/garbage-collector/inventory/inventory.yml`, cópias históricas ficam em `inventory/history/` e relatórios Markdown ficam em `reports/`.

## Plano de Trabalho

Adicionar PyYAML às dependências de produção. Criar modelos imutáveis e tipados para as configurações e resultados, um carregador que acumula erros de validação e uma abstração de Git para enumerar caminhos. Implementar as regras como combinações de critérios declarados no YAML, sem decisões baseadas em identificadores de regra. Em seguida, criar escritores protegidos para inventário e relatório e conectar tudo a uma CLI com quatro subcomandos e códigos de saída estáveis.

Atualizar as regras iniciais, os READMEs, a agenda manual e as propostas acionáveis para usar comandos `uv`. Adicionar testes observáveis para configurações válidas e inválidas, limites temporais, caminhos, exceções, determinismo, destinos de escrita e CLI. Por fim, executar o `check` no repositório real, revisar os artefatos gerados, executar todas as verificações do projeto e arquivar este ExecPlan.

## Etapas Concretas

No diretório `/home/leoadelmo/elevator_vibe_code`, executar durante a implementação:

    uv add "PyYAML==6.0.3"
    uv run --group dev ruff format .
    uv run --group dev ruff check .
    uv run --group dev ruff format --check .
    uv run --group dev mypy
    uv run --group dev pytest
    uv run python -m tools.validators.check_exec_plans
    uv lock --check
    uv run python -m tools.garbage_collector scan
    uv run python -m tools.garbage_collector check
    git diff --check
    git status --short

Todos os comandos de validação devem retornar código zero. O `scan` não deve alterar arquivos. O `check` deve alterar somente o inventário atual, criar um histórico e criar o relatório diário.

## Validação e Aceitação

Uma configuração válida deve produzir candidatos ordenados e mensagens simples. YAML ausente ou inválido, campos incorretos, caminhos inseguros e integração Git inválida devem retornar código 2 sem varredura. `--fail-on warning` e `--fail-on error` devem retornar código 1 quando o limiar correspondente for alcançado; sem a opção, candidatos não tornam a execução inválida.

Os testes devem provar que `scan` não grava, `inventory` grava somente inventário e histórico, `report` grava somente relatório e `check` grava os três. Uma fotografia dos arquivos fora desses destinos deve permanecer idêntica após cada comando. A execução real deve gerar artefatos legíveis que apenas recomendam revisão.

## Idempotência e Recuperação

Configuração e varredura são somente leitura. O inventário atual e o relatório diário podem ser regenerados atomicamente. Históricos usam criação exclusiva e nunca substituem um arquivo existente; uma colisão deve produzir erro explícito. Se uma execução for interrompida, remover apenas um arquivo temporário confirmado dentro de um diretório permitido e repetir o comando. Nenhum fluxo usa exclusão, movimentação ou renomeação de material inspecionado.

## Artefatos e Notas

A interface final será:

    uv run python -m tools.garbage_collector scan
    uv run python -m tools.garbage_collector inventory
    uv run python -m tools.garbage_collector report
    uv run python -m tools.garbage_collector check

Os códigos de saída serão 0 para sucesso, 1 para limiar de candidatos, 2 para argumentos, configuração, raiz ou Git inválidos e 3 para falha ao gravar uma saída permitida.

## Interfaces e Dependências

A dependência de produção será `PyYAML==6.0.3`, acompanhada no grupo de desenvolvimento por `types-PyYAML==6.0.12.20260518`. A CLI aceitará `--project-root`, `--rules-file`, `--exceptions-file` e `--fail-on {error,warning}` em todos os subcomandos. `scan` apenas varre; `inventory` também grava o inventário atual e histórico; `report` também grava o relatório; `check` executa todas as saídas.

Os modelos públicos da ferramenta usarão `dataclasses` e enums. O relógio e o provedor de caminhos Git serão protocolos injetáveis, permitindo testes determinísticos sem rede. Não haverá API nova no pacote da aplicação.

Nota de alteração (2026-07-25): criado a partir da proposta `docs/plan-proposals/PLANO-IMPLEMENTACAO-GARBAGE-COLLECTOR.md`, incorporando o fluxo obrigatório com uv e resolvendo a incompatibilidade entre exceções permanentes e a regra de expiração.
