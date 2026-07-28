# Atualizar regras de negócio do elevador

Este ExecPlan é um documento vivo. As seções `Progresso`, `Surpresas e Descobertas`, `Registro de Decisões` e `Resultados e Retrospectiva` devem ser mantidas atualizadas durante a execução do trabalho.

Este documento deve ser mantido de acordo com `PLANS.md`.

## Propósito / Visão geral

Quem consulta as regras de negócio do elevador precisa encontrar uma versão consolidada, sem conflito entre a regra inicial e as regras refinadas. Depois desta alteração, `docs/business_rules/regras_elevador.md` descreve explicitamente chamadas externas, capacidade, fila de espera, embarque durante trajeto, prioridades, estado de espera, tempo de deslocamento e limites de operação.

## Progresso

- [x] (2026-07-26 00:00Z) Comparada a versão inicial de `docs/business_rules/regras_elevador.md` com as novas regras fornecidas.
- [x] (2026-07-26 00:00Z) Identificada a contradição da versão inicial sobre buscar chamadas externas apenas quando o elevador está vazio.
- [x] (2026-07-26 00:00Z) Substituído o conteúdo de `docs/business_rules/regras_elevador.md` pela versão consolidada.
- [x] (2026-07-26 00:00Z) Validada a estrutura de ExecPlans com `uv run python -m tools.validators.check_exec_plans`.
- [x] (2026-07-26 00:00Z) Arquivar este plano em `docs/exec_plans/completed/atualizar_regras_elevador.md`.

## Surpresas e Descobertas

- Observação: a regra inicial dizia que o elevador só prioriza buscar pessoas nos andares chamados quando está vazio, mas a nova regra permite embarque durante o trajeto se houver capacidade e se isso não impedir as entregas em andamento.
  Evidência: a versão consolidada cria a seção `Embarque durante o trajeto` e detalha essa exceção operacional.

## Registro de Decisões

- Decisão: substituir o conteúdo anterior de `docs/business_rules/regras_elevador.md` pela versão consolidada.
  Justificativa: manter duas listas de regras criaria duplicidade e risco de conflito para futuras implementações.
  Data/Autor: 2026-07-26 / Codex.

- Decisão: manter `docs/business_rules/README.md` sem alteração nesta atualização.
  Justificativa: o README já aponta para `regras_elevador.md`, que continua sendo o documento de referência.
  Data/Autor: 2026-07-26 / Codex.

## Resultados e Retrospectiva

O documento `docs/business_rules/regras_elevador.md` foi substituído pela versão consolidada com oito seções. A validação de ExecPlans imprimiu `ExecPlans: estrutura válida.` e a busca pela restrição antiga de busca apenas quando vazio não retornou ocorrências.

## Contexto e Orientação

O documento `docs/business_rules/regras_elevador.md` foi criado para registrar regras de negócio do elevador residencial. A versão inicial tinha contexto, uma lista de dez regras, prioridades operacionais e parâmetros fixos. A pessoa usuária forneceu uma versão mais detalhada com oito seções numeradas e regras adicionais sobre chamadas externas, filas, embarque durante trajeto e limites de operação.

Esta tarefa não altera código Python. O objetivo é atualizar a fonte normativa de negócio para que uma futura implementação tenha regras completas e sem contradição.

## Plano de Trabalho

Substituir o conteúdo de `docs/business_rules/regras_elevador.md` pela versão consolidada com o título `Regras de Negócio do Elevador` e as oito seções numeradas fornecidas pela pessoa usuária. Preservar o sentido das regras novas, com ajustes mínimos de formatação para Markdown.

Depois de atualizar o documento, executar o validador de ExecPlans. Se a estrutura estiver válida, atualizar este plano com o resultado e mover o arquivo para `docs/exec_plans/completed/atualizar_regras_elevador.md`.

## Etapas Concretas

No diretório `/home/lvaz/projetos/elevator_ia_poc`, editar `docs/business_rules/regras_elevador.md` e executar:

    uv run python -m tools.validators.check_exec_plans

A saída esperada é:

    ExecPlans: estrutura válida.

## Validação e Aceitação

A entrega é aceita quando `docs/business_rules/regras_elevador.md` contém as oito seções da regra consolidada, não mantém a restrição antiga de buscar chamadas externas apenas quando o elevador estiver vazio, e o validador de ExecPlans retorna código zero.

## Idempotência e Recuperação

A alteração é documental. Se a atualização for interrompida, reabrir `docs/business_rules/regras_elevador.md`, confirmar se as oito seções consolidadas estão presentes e concluir somente o trecho faltante. Não há migração de dados nem alteração destrutiva.

## Artefatos e Notas

Artefatos produzidos: `docs/business_rules/regras_elevador.md` atualizado e este plano arquivado em `docs/exec_plans/completed/atualizar_regras_elevador.md`.

## Interfaces e Dependências

Não há API, dependência ou módulo Python novo. A única validação planejada é `uv run python -m tools.validators.check_exec_plans`.
