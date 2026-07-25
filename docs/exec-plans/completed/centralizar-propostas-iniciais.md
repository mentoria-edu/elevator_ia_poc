# Centralizar propostas iniciais em plan-proposals

Este ExecPlan é um documento vivo. As seções `Progresso`, `Surpresas e Descobertas`, `Registro de Decisões` e `Resultados e Retrospectiva` devem ser mantidas atualizadas durante a execução do trabalho.

Este documento deve ser mantido de acordo com `PLANS.md`.

## Propósito / Visão geral

As pessoas que consultam o repositório poderão localizar propostas iniciais de implementação em um único diretório na raiz, sem confundi-las com planos de execução. A mudança estará concluída quando os dois documentos de proposta existentes estiverem em `plan-proposals/`, a finalidade da pasta estiver documentada e os índices do repositório apontarem para ela.

## Progresso

- [x] (2026-07-25 00:00Z) Identificada a separação atual entre propostas na raiz e ExecPlans em `docs/exec-plans/`.
- [x] (2026-07-25 00:00Z) Criada a documentação da nova categoria e atualizados os índices.
- [x] (2026-07-25 00:00Z) Movidas as duas propostas existentes para `plan-proposals/`.
- [x] (2026-07-25 00:00Z) Executada a validação de ExecPlans; falta apenas arquivar este plano.

## Surpresas e Descobertas

- Observação: o validador do repositório verifica somente arquivos Markdown em `docs/exec-plans/active/` e `docs/exec-plans/completed/`.
  Evidência: `tools/validators/check_exec_plans.py` define apenas esses dois diretórios em `EXEC_PLAN_DIRECTORIES`.

## Registro de Decisões

- Decisão: criar `plan-proposals/` na raiz e mover para ela os dois documentos de proposta existentes.
  Justificativa: centraliza documentos de intenção inicial e preserva sua distinção dos ExecPlans operacionais.
  Data/Autor: 2026-07-25 / Codex

- Decisão: documentar a nova categoria em um README próprio, em `ARCHITECTURE.md` e no `README.md` principal.
  Justificativa: a pasta terá responsabilidade recorrente e deve ser descoberta tanto pela visão arquitetural quanto pela visão geral do projeto.
  Data/Autor: 2026-07-25 / Codex

## Resultados e Retrospectiva

A categoria `plan-proposals/` foi criada com um README que a diferencia de
ExecPlans. As duas propostas existentes foram centralizadas nela e os índices
arquitetural e principal passaram a apontar para a nova localização. O
validador de ExecPlans foi aprovado com Python 3.14.4.

As verificações completas de qualidade não foram executadas porque o ambiente
não possui os comandos `ruff`, `pytest` ou `python` disponíveis. O comando
`python3 -m pytest` confirmou que o módulo `pytest` também não está instalado.

## Contexto e Orientação

O repositório usa `docs/exec-plans/active/` para planos em andamento e `docs/exec-plans/completed/` para planos concluídos. Esses documentos são ExecPlans e seguem a convenção detalhada em `PLANS.md`. As propostas iniciais não são instruções executáveis: elas registram a intenção de um projeto ou funcionalidade antes de um plano de execução ser escrito.

No estado inicial, `PLANO-ESTRUTURA-PROJETO.md` está na raiz do repositório e `PLANO-IMPLEMENTACAO-GARBAGE-COLLECTOR.md` também está disponível na raiz como arquivo ainda não versionado. `ARCHITECTURE.md` lista as responsabilidades principais e o `README.md` apresenta a estrutura para colaboradores.

## Plano de Trabalho

Criar `plan-proposals/README.md` com a definição de proposta inicial e o encaminhamento de propostas aprovadas para `docs/exec-plans/active/`. Atualizar `ARCHITECTURE.md` e `README.md` para listar essa categoria e diferenciá-la de ExecPlans. Mover os dois arquivos de proposta para `plan-proposals/` sem modificar seus nomes ou conteúdos. Depois de validar a estrutura de ExecPlans, atualizar as seções de progresso e resultados deste arquivo e movê-lo para `docs/exec-plans/completed/`.

## Etapas Concretas

No diretório raiz do repositório, criar a documentação e mover os arquivos de proposta. Em seguida, executar:

    python -m tools.validators.check_exec_plans

O comando deve imprimir `ExecPlans: estrutura válida.` e retornar código zero. Por fim, arquivar este arquivo em `docs/exec-plans/completed/`.

## Validação e Aceitação

A pessoa colaboradora deve encontrar `PLANO-ESTRUTURA-PROJETO.md` e `PLANO-IMPLEMENTACAO-GARBAGE-COLLECTOR.md` dentro de `plan-proposals/`, junto com um README que explica sua finalidade. O README principal e a arquitetura devem direcionar à nova pasta e indicar que ExecPlans continuam em `docs/exec-plans/`. O validador deve aceitar os diretórios de ExecPlans e o plano arquivado.

## Idempotência e Recuperação

As alterações são somente documentais. Caso uma movimentação seja interrompida, verificar quais arquivos já estão em `plan-proposals/` e concluir apenas as pendências, sem criar cópias duplicadas. Não há migração de dados nem alteração destrutiva.

## Artefatos e Notas

O resultado observável esperado é a estrutura:

    plan-proposals/
    ├── README.md
    ├── PLANO-ESTRUTURA-PROJETO.md
    └── PLANO-IMPLEMENTACAO-GARBAGE-COLLECTOR.md

## Interfaces e Dependências

Não há interfaces de código, dependências novas ou alterações de comportamento da aplicação. A mudança mantém o contrato documental existente: `docs/exec-plans/` contém apenas ExecPlans, enquanto `plan-proposals/` contém propostas iniciais.
