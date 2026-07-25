# Elevator Vibe Code

Base Python para a prova de conceito Elevator IA. O projeto usa o layout
`src/` e mantém documentação, testes e ferramentas operacionais separados.

## Desenvolvimento

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
ruff check .
ruff format --check .
pytest
```

O pacote principal fica em `src/elevator_vibe_code/`. Consulte
`ARCHITECTURE.md` para os limites de módulos e `AGENTS.md` para o fluxo de
contribuição.
