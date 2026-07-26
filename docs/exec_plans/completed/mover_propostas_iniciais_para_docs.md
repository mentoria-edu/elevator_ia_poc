# Mover propostas iniciais para docs

Este ExecPlan é um documento vivo. As seções `Progresso`, `Surpresas e Descobertas`, `Registro de Decisões` e `Resultados e Retrospectiva` devem ser mantidas atualizadas durante a execução do trabalho.

Este documento deve ser mantido de acordo com `PLANS.md`.

## Propósito / Visão geral

Quem consulta a documentação encontrará as propostas iniciais junto das demais categorias documentais, em `docs/plan_proposals/`, sem confundi-las com os planos de execução em `docs/exec_plans/`. A entrega poderá ser verificada pela ausência do diretório anterior na raiz, pela presença dos três documentos em seu novo local e pelo validador de ExecPlans aceitando a estrutura.

## Progresso

- [x] (2026-07-25 00:00Z) Lidos `ARCHITECTURE.md`, `PLANS.md`, os índices e o ExecPlan concluído que ainda documenta o caminho raiz.
- [x] (2026-07-25 00:00Z) Movidos o README e os dois documentos para `docs/plan_proposals/`, preservando as somas SHA-256 das propostas.
- [x] (2026-07-25 00:00Z) Atualizados os índices e o ExecPlan concluído para o novo caminho.
- [x] (2026-07-25 00:00Z) Verificadas referências, integridade dos arquivos movidos e a estrutura de ExecPlans; o validador retornou `ExecPlans: estrutura válida.` e este plano está pronto para arquivamento.

## Surpresas e Descobertas

- Observação: a execução por `uv` não pôde criar seu arquivo temporário no cache fora da área de escrita isolada.
  Evidência: o primeiro comando retornou `Read-only file system` em `/home/leoadelmo/.cache/uv/`; a validação será repetida com a permissão necessária para esse cache.

## Registro de Decisões

- Decisão: manter somente `docs/plan_proposals/` como localização das propostas iniciais.
  Justificativa: propostas são documentação e devem ficar sob `docs/`, enquanto ExecPlans continuam em sua categoria específica `docs/exec_plans/`.
  Data/Autor: 2026-07-25 / Codex

## Resultados e Retrospectiva

Os três documentos foram movidos para `docs/plan_proposals/`; os dois documentos de proposta mantiveram as somas SHA-256 originais. `ARCHITECTURE.md`, `README.md`, `docs/README.md` e o ExecPlan concluído passaram a indicar a localização final. A busca de referências confirmou que os índices usam `docs/plan_proposals/` na raiz e `plan_proposals/` apenas no contexto de `docs/`. O comando `uv run python -m tools.validators.check_exec_plans` foi aprovado e imprimiu `ExecPlans: estrutura válida.`.

## Contexto e Orientação

`docs/plan_proposals/` contém `README.md`, `plano_estrutura_projeto.md` e `plano_implementacao_garbage_collector.md`. O README define proposta como o registro da intenção inicial de uma funcionalidade; uma proposta aprovada torna-se um ExecPlan em `docs/exec_plans/active/`. `ARCHITECTURE.md`, `README.md` e `docs/README.md` são os índices que orientam quem navega pelo repositório. O ExecPlan concluído `docs/exec_plans/completed/centralizar_propostas_iniciais.md` descreve a mesma localização final para permanecer historicamente coerente.

## Plano de Trabalho

Criar `docs/plan_proposals/` e mover para ela os três arquivos existentes, sem mudar o conteúdo das duas propostas. Alterar `ARCHITECTURE.md` e `README.md` para usar o caminho completo `docs/plan_proposals/`; em `docs/README.md`, listar a categoria pelo caminho relativo `plan_proposals/`. Revisar todas as menções no ExecPlan concluído para que descrevam `docs/plan_proposals/`, inclusive título, decisões, estrutura e contrato documental. Depois, pesquisar por referências obsoletas, comparar as somas SHA-256 das duas propostas com os valores obtidos antes da movimentação e executar o validador. Atualizar este plano com os resultados e movê-lo para `docs/exec_plans/completed/`.

## Etapas Concretas

No diretório raiz `/home/leoadelmo/elevator_vibe_code`, mover a pasta e editar os quatro documentos de índice/histórico. Executar:

    find docs/plan_proposals -maxdepth 1 -type f -printf '%f\\n' | sort
    rg -n --hidden --glob '!.git/**' --glob '!.venv/**' 'docs/plan_proposals|`plan_proposals/'
    sha256sum docs/plan_proposals/plano_estrutura_projeto.md docs/plan_proposals/plano_implementacao_garbage_collector.md
    uv run python -m tools.validators.check_exec_plans

O primeiro comando deve listar exatamente três arquivos. A busca não deve mostrar o caminho raiz obsoleto. As duas somas devem ser, respectivamente, `2e9743b177f19e64951c61b97d114616f89f9ffd5f0a4f42c71837a823432123` e `cf848236871a96ab19e98815e7190425620d594a3c9fba38c4cce5d3015d9ff6`. O validador deve imprimir `ExecPlans: estrutura válida.` e encerrar com código zero.

## Validação e Aceitação

Após a mudança, uma pessoa pode abrir `docs/README.md`, encontrar a categoria `plan_proposals/` e abrir seus três documentos; `README.md` e `ARCHITECTURE.md` também a direcionam para `docs/plan_proposals/`. O diretório anterior não existe na raiz. As duas propostas preservam suas somas SHA-256 anteriores à migração e o validador aceita os planos ativo e concluídos antes deste plano ser arquivado, e os concluídos depois do arquivamento.

## Idempotência e Recuperação

A migração é documental. Se for interrompida, identificar qual das duas pastas existe e completar apenas o movimento pendente, mantendo uma única cópia de cada arquivo. Os arquivos das propostas não devem ser editados: a comparação de SHA-256 detecta qualquer alteração acidental. As edições de índices podem ser reaplicadas sem criar duplicatas.

## Artefatos e Notas

A árvore final esperada é:

    docs/plan_proposals/
    ├── README.md
    ├── plano_estrutura_projeto.md
    └── plano_implementacao_garbage_collector.md

## Interfaces e Dependências

Não há interfaces de código, bibliotecas ou serviços novos. A única ferramenta de validação é o módulo local `tools.validators.check_exec_plans`, executado por `uv run python`, que verifica a estrutura e o formato dos ExecPlans em `docs/exec_plans/active/` e `docs/exec_plans/completed/`.

Nota de alteração (2026-07-25): criado para registrar a migração das propostas iniciais da raiz para `docs/`, mantendo os índices e o histórico documental consistentes.
