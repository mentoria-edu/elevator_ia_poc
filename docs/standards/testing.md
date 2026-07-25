# Padrões de testes

Os testes são sensores de comportamento e devem permitir detectar regressões
com rapidez e baixo custo de manutenção.

## Regras gerais

- Todo comportamento novo deve possuir teste.
- Toda correção de bug deve possuir um teste de regressão.
- Cada nova função deve ser testada, exceto quando sua simplicidade e contexto
  tornarem o teste redundante.
- Testes devem verificar resultados observáveis, não detalhes internos sem
  valor comportamental.

## Princípio F.I.R.S.T.

Os testes devem ser:

- **Fast**: rápidos;
- **Independent**: independentes entre si;
- **Repeatable**: repetíveis em qualquer execução equivalente;
- **Self-validating**: falham ou passam sem inspeção manual;
- **Timely**: escritos próximos da implementação do comportamento.

## I/O externo

- I/O externo deve ser isolado nos testes.
- APIs, bancos de dados e sistemas de arquivos devem ser substituídos por
  classes fake nomeadas quando possível.
- Evite stubs anônimos e mocks inline que escondam o contrato utilizado pelo
  teste.
- Testes unitários não devem depender de rede, banco real ou arquivos externos.

## Organização

```text
tests/
├── unit/
└── garbage_collector/
```

Use `tests/unit/` para o comportamento da aplicação e
`tests/garbage_collector/` para o scanner, inventário e relatórios do Garbage
Collector.

## Execução

Todos os testes devem ser executáveis com um único comando:

```bash
uv run --group dev pytest
```

O comando deve ser executado antes de concluir uma alteração.
