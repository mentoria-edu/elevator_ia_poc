# Repository Guidelines

## Estrutura

O código da aplicação fica em `src/elevator_vibe_code/`; os testes ficam em
`tests/unit/` e `tests/garbage_collector/`. Ferramentas de manutenção ficam em
`tools/`, e a documentação organizada fica em `docs/`. Não crie diretórios de
domínio sem uma responsabilidade recorrente e documentada.

## Fluxo de Trabalho

Leia `ARCHITECTURE.md` antes de incluir módulos e registre planos ativos em
`docs/exec-plans/active/`. Mova um plano concluído para `completed/`. Regras de
negócio pertencem a `docs/business-rules/`, não a instruções de agentes.

## Qualidade

Use Python 3.14.5+ e anotações nos pontos públicos. Nomes devem ser específicos
e em `snake_case`; classes usam `PascalCase`. Formate e valide antes de abrir
uma alteração:

```bash
uv run --group dev ruff check .
uv run --group dev ruff format --check .
uv run --group dev mypy
uv run --group dev pytest
uv run python -m tools.validators.check_exec_plans
```

Consulte `docs/standards/` para os padrões completos de código, testes,
logging e documentação. Mudanças de comportamento exigem testes observáveis;
testes não devem depender de rede ou serviços externos.

## Alterações e Revisão

Faça commits pequenos, no imperativo e com escopo claro, por exemplo
`Add floor request validation`. Pull requests devem explicar a mudança, indicar
os comandos de validação executados e vincular a demanda correspondente.
Não registre segredos, tokens ou dados pessoais em código, documentação ou
logs.
