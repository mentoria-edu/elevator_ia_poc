# Documentar regras de negócio do elevador

Este ExecPlan é um documento vivo. As seções `Progresso`, `Surpresas e Descobertas`, `Registro de Decisões` e `Resultados e Retrospectiva` devem ser mantidas atualizadas durante a execução do trabalho.

Este documento deve ser mantido de acordo com `PLANS.md`.

## Propósito / Visão geral

Quem consulta o repositório precisa encontrar as regras de negócio do elevador residencial em um documento próprio, antes de qualquer implementação de código. A mudança estará concluída quando `docs/business_rules/regras_elevador.md` existir, listar todas as regras informadas pela pessoa usuária e `docs/business_rules/README.md` apontar para esse documento.

## Progresso

- [x] (2026-07-26 00:00Z) Confirmada a branch base `feat/padronizando_nomes_estrutura` e o worktree limpo.
- [x] (2026-07-26 00:00Z) Criada a branch `feat/ELEVATOR_BUSINESS_RULES`.
- [x] (2026-07-26 00:00Z) Criado `docs/business_rules/regras_elevador.md` com as regras de negócio do elevador.
- [x] (2026-07-26 00:00Z) Atualizado `docs/business_rules/README.md`.
- [x] (2026-07-26 00:00Z) Validada a estrutura de ExecPlans com `uv run python -m tools.validators.check_exec_plans`.
- [x] (2026-07-26 00:00Z) Arquivar este plano em `docs/exec_plans/completed/documentar_regras_elevador.md`.

## Surpresas e Descobertas

- Observação: a pasta `docs/business_rules/` já existia e continha apenas o índice `README.md`.
  Evidência: a inspeção inicial listou somente `README.md` nessa pasta.

## Registro de Decisões

- Decisão: registrar as regras em `docs/business_rules/regras_elevador.md`.
  Justificativa: regras de negócio pertencem a `docs/business_rules/`, conforme `AGENTS.md` e a estrutura atual do repositório.
  Data/Autor: 2026-07-26 / Codex.

- Decisão: não criar código Python nesta tarefa.
  Justificativa: a demanda é registrar regras de negócio para orientar futuras implementações, não implementar a lógica do elevador.
  Data/Autor: 2026-07-26 / Codex.

## Resultados e Retrospectiva

A regra de negócio do elevador foi registrada em `docs/business_rules/regras_elevador.md`, e `docs/business_rules/README.md` passou a apontar para esse documento. A validação de ExecPlans imprimiu `ExecPlans: estrutura válida.` e retornou código zero antes do arquivamento.

## Contexto e Orientação

O repositório usa `docs/business_rules/` para documentos de regras de negócio em linguagem de domínio. Atualmente essa pasta contém `README.md`, mas não possui um documento com as regras do elevador. Não há necessidade de alterar código Python nesta tarefa.

As regras fornecidas descrevem um elevador residencial em um prédio de 18 andares, com um botão externo por andar, capacidade máxima de 6 pessoas e prioridades operacionais para chamadas externas e pessoas embarcadas.

## Plano de Trabalho

Criar `docs/business_rules/regras_elevador.md` com seções curtas: contexto, regras, prioridades operacionais e parâmetros fixos. O texto deve preservar o sentido das regras informadas pela pessoa usuária e usar redação clara de negócio, sem transformar o documento em algoritmo técnico.

Atualizar `docs/business_rules/README.md` para indicar que as regras do elevador estão documentadas em `regras_elevador.md`. Ao final, validar a estrutura dos ExecPlans com o validador local e mover este arquivo para `docs/exec_plans/completed/documentar_regras_elevador.md`.

## Etapas Concretas

No diretório `/home/lvaz/projetos/elevator_ia_poc`, criar ou atualizar os arquivos documentais e executar:

    uv run python -m tools.validators.check_exec_plans

O comando deve imprimir:

    ExecPlans: estrutura válida.

## Validação e Aceitação

A entrega é aceita quando `docs/business_rules/regras_elevador.md` existe, contém todas as regras informadas pela pessoa usuária, `docs/business_rules/README.md` aponta para o documento e o validador de ExecPlans retorna código zero.

## Idempotência e Recuperação

As alterações são documentais. Se a execução for interrompida, verificar a presença de `docs/business_rules/regras_elevador.md`, conferir o README e concluir apenas a etapa faltante. Não há migração de dados nem alteração destrutiva.

## Artefatos e Notas

Artefatos produzidos: `docs/business_rules/regras_elevador.md`, `docs/business_rules/README.md` atualizado e este plano arquivado em `docs/exec_plans/completed/documentar_regras_elevador.md`.

## Interfaces e Dependências

Não há API, dependência ou módulo Python novo. A única ferramenta de validação prevista é `tools.validators.check_exec_plans`, executada via `uv run python`.
