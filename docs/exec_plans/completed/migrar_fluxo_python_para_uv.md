# Migrar o fluxo Python para uv

Este ExecPlan é um documento vivo. As seções `Progresso`, `Surpresas e Descobertas`, `Registro de Decisões` e `Resultados e Retrospectiva` devem ser mantidas atualizadas durante a execução do trabalho.

Este documento deve ser mantido de acordo com `PLANS.md`.

## Propósito / Visão geral

Quem usa o repositório poderá instalar a versão correta de Python, sincronizar um ambiente de produção ou desenvolvimento e executar todas as ferramentas com comandos uv documentados. A mudança estará completa quando o projeto tiver dependências separadas, lockfile versionado, Mypy configurado e validações aprovadas.

## Progresso

- [x] (2026-07-25 00:00Z) Inspecionadas as dependências, os comandos documentados e a disponibilidade do uv.
- [x] (2026-07-25 00:00Z) Configuradas dependências, Mypy e comandos uv.
- [x] (2026-07-25 00:00Z) Criados o pin de Python 3.14.5 e o lockfile com uv.
- [x] (2026-07-25 00:00Z) Sincronizados os ambientes e executadas as validações; falta apenas arquivar este plano.

## Surpresas e Descobertas

- Observação: o grupo `dev` do uv é sincronizado por padrão, mas o projeto exige que uma sincronização comum instale somente produção.
  Evidência: a configuração final usará `default-groups = []` em `[tool.uv]`.

## Registro de Decisões

- Decisão: usar `[dependency-groups].dev`, em vez de um extra publicado, para ferramentas locais de desenvolvimento.
  Justificativa: Mypy, Pytest e Ruff não são requisitos da aplicação distribuída.
  Data/Autor: 2026-07-25 / Codex

- Decisão: fixar o ambiente local em Python 3.14.5, mantendo o metadado do pacote compatível com 3.14.5 ou superior.
  Justificativa: a reprodução local é determinística sem impedir consumidores de versões posteriores compatíveis.
  Data/Autor: 2026-07-25 / Codex

## Resultados e Retrospectiva

O repositório passou a usar uv para gerenciar o Python 3.14.5, o ambiente
virtual e as dependências. O grupo de produção permanece vazio, enquanto o
grupo local `dev` instala Ruff, Mypy, Pytest e pytest-cov em versões fixadas.
Uma sincronização de produção removeu as 14 ferramentas transitivas e de
desenvolvimento; a sincronização com `--group dev` as reinstalou.

As validações foram aprovadas: `uv lock --check`, Ruff, o formatador Ruff,
Mypy, Pytest (4 testes) e o validador de ExecPlans.

## Contexto e Orientação

O projeto é um pacote Python em `src/elevator_vibe_code/`, com ferramentas em `tools/` e testes em `tests/`. Antes desta alteração, `pyproject.toml` exigia Python 3.11 ou superior, declarava as ferramentas de teste e lint como extra `dev` e não possuía configuração de Mypy, lockfile ou pin de interpretador.

O uv cria e sincroniza `.venv/` a partir de `pyproject.toml` e `uv.lock`. O grupo `dev` contém somente ferramentas de desenvolvimento. O Mypy é um verificador estático: ele analisa anotações de tipo sem executar a aplicação.

## Plano de Trabalho

Atualizar `pyproject.toml` para exigir Python 3.14.5 ou superior, separar dependências de produção e desenvolvimento, fixar as versões das ferramentas e configurar Mypy. Criar `.python-version` com o uv e gerar `uv.lock`. Atualizar todos os comandos Python nos documentos do repositório para usar uv e incluir Mypy no fluxo de qualidade. Sincronizar os ambientes de produção e desenvolvimento e executar as verificações. Ao final, registrar os resultados e mover este plano para `docs/exec_plans/completed/`.

## Etapas Concretas

No diretório raiz, executar:

    uv python install 3.14.5
    uv python pin 3.14.5
    uv lock
    uv sync
    uv sync --group dev
    uv lock --check
    uv run --group dev ruff check .
    uv run --group dev ruff format --check .
    uv run --group dev mypy
    uv run --group dev pytest
    uv run python -m tools.validators.check_exec_plans

Todos os comandos de validação devem terminar com código zero.

## Validação e Aceitação

Uma sincronização comum deve criar o ambiente sem as ferramentas de desenvolvimento. A sincronização com `--group dev` deve instalar as versões fixadas de Ruff, Mypy, Pytest e pytest-cov. Os comandos de qualidade documentados devem executar pelo uv e o Mypy deve analisar `src`, `tools` e `tests` sem erros.

## Idempotência e Recuperação

Os comandos uv podem ser repetidos: o lockfile e o ambiente serão reconciliados com o metadado atual. Caso a resolução falhe, corrigir as restrições incompatíveis no `pyproject.toml` e regenerar o lockfile; não editar `uv.lock` manualmente.

## Artefatos e Notas

Os novos artefatos versionados são `.python-version` e `uv.lock`. O ambiente `.venv/` é local e permanece ignorado pelo Git.

## Interfaces e Dependências

Não há alteração de APIs de aplicação. As ferramentas de desenvolvimento passam a ser `mypy==2.3.0`, `pytest==9.1.1`, `pytest-cov==7.1.0` e `ruff==0.15.22`; o backend de build passa a usar `setuptools==83.0.0`.
