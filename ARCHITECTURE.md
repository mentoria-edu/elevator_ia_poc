# Arquitetura

## Módulos

- `src/elevator_vibe_code/`: implementação da aplicação e regras de domínio.
- `tests/unit/`: testes do comportamento da aplicação.
- `tools/`: ferramentas determinísticas de manutenção do repositório.
- `docs/`: documentação operacional, padrões e regras de negócio.
- `docs/plan_proposals/`: propostas iniciais que registram a intenção de projetos
  ou funcionalidades antes de sua execução.

## Convenção de Nomes

Use `snake_case` para diretórios e arquivos auxiliares do repositório,
incluindo `.py`, `.md` de apoio, `.yml` e equivalentes. As únicas exceções em
`UPPERCASE` são `AGENTS.md`, `ARCHITECTURE.md`, `PLANS.md` e todos os arquivos
`README.md`. Ao renomear qualquer caminho, atualize na mesma alteração todas as
referências textuais e operacionais para manter o repositório coerente.

## Dependências Permitidas

O código de domínio não deve importar módulos de `tools/`. Ferramentas podem
ler documentação e metadados do repositório, mas não devem conter regras de
negócio. Integrações externas devem ser encapsuladas no pacote da aplicação
quando uma funcionalidade concreta as exigir.

## Estado Inicial

Ainda não há módulos de domínio. Adicione-os em `src/elevator_vibe_code/`
somente junto com uma responsabilidade definida, documentação relevante e
testes unitários.
