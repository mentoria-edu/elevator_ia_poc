# Padrões de Documentação

Documente decisões, contratos e regras que ajudem a alterar o projeto com
segurança. Mantenha textos próximos à responsabilidade descrita e remova
informações obsoletas na mesma alteração que modifica o comportamento.

Use linguagem objetiva. Regras de negócio devem ser escritas em
`docs/business_rules/`; instruções operacionais pertencem a `AGENTS.md`.

Use `snake_case` para nomes de diretórios e arquivos auxiliares, incluindo
`.py`, `.md` de apoio, `.yml` e equivalentes. Preservam `UPPERCASE` apenas
`AGENTS.md`, `ARCHITECTURE.md`, `PLANS.md` e todos os arquivos `README.md`.
Quando um nome mudar, atualize todas as referências textuais e operacionais na
mesma alteração.
