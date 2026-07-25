# Garbage Collector

O Garbage Collector identifica material do repositório que precisa de revisão
humana. Ele nunca exclui, move ou renomeia candidatos.

Execute uma varredura somente leitura:

```bash
uv run python -m tools.garbage_collector scan
```

Para atualizar o inventário atual, criar um histórico e gerar o relatório
diário:

```bash
uv run python -m tools.garbage_collector check
```

Também estão disponíveis os subcomandos `inventory`, que grava somente os
inventários, e `report`, que grava somente o relatório. Todos aceitam
`--project-root`, `--rules-file`, `--exceptions-file` e
`--fail-on {error,warning}`. Sem `--fail-on`, candidatos não causam falha.

Os códigos de saída são:

- `0`: configuração válida e limiar não atingido;
- `1`: limiar de severidade atingido;
- `2`: argumentos, configuração, raiz ou Git inválidos;
- `3`: falha ao gravar uma saída permitida.

Regras declarativas ficam em `rules/default-rules.yml`. O campo opcional
`tracked_only: true` restringe uma regra a arquivos versionados. Exceções
ficam em `exceptions/active-exceptions.yml` e exigem `path`, `reason`, `owner`
e `removal_condition`; elas permanecem ativas até sua remoção explícita.

As únicas saídas permitidas são `inventory/inventory.yml`, arquivos novos em
`inventory/history/` e relatórios em `reports/`.
