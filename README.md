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
uv sync --locked
```

Para desenvolver, sincronize também o grupo local de ferramentas e execute as
validações:

```bash
uv sync --locked --group dev
uv run --group dev ruff check .
uv run --group dev ruff format --check .
uv run --group dev mypy
uv run --group dev pytest
uv run python -m tools.validators.check_exec_plans
```

Para comprovar a integração entre geração, modelos, motor e CLI, execute:

```bash
uv run python -m elevator_vibe_code demo --rounds 2 --step-delay 2
```

A demonstração lista cada solicitação da subida e, após concluir essa fase,
lista os novos usuários e origens da descida. O delay entre os passos é de 2
segundos por padrão. Use `--step-delay 0`
para executar a demonstração sem espera.

O pacote principal fica em `src/elevator_vibe_code/`. Consulte
`ARCHITECTURE.md` para os limites de módulos e `AGENTS.md` para o fluxo de
contribuição. As intenções iniciais de implementação ficam em
`docs/plan_proposals/`; planos de execução em andamento e concluídos ficam em
`docs/exec_plans/`.
