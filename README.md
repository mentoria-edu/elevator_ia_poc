# Elevator Vibe Code

Base Python para a prova de conceito Elevator IA. O projeto usa o layout
`src/` e mantém documentação, testes e ferramentas operacionais separados.

## Ambiente Python

Instale o [uv](https://docs.astral.sh/uv/getting-started/installation/) e a
versão de Python fixada pelo projeto:

```bash
uv python install 3.14.5
```

Para instalar somente o projeto e suas dependências de produção, execute:

```bash
uv sync
```

Para desenvolver, sincronize também o grupo local de ferramentas e execute as
validações:

```bash
uv sync --group dev
uv run --group dev ruff check .
uv run --group dev ruff format --check .
uv run --group dev mypy
uv run --group dev pytest
uv run python -m tools.validators.check_exec_plans
```

O pacote principal fica em `src/elevator_vibe_code/`. Consulte
`ARCHITECTURE.md` para os limites de módulos e `AGENTS.md` para o fluxo de
contribuição. As intenções iniciais de implementação ficam em
`docs/plan-proposals/`; planos de execução em andamento e concluídos ficam em
`docs/exec-plans/`.
