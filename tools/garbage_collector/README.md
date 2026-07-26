# Garbage Collector

Ferramenta determinística de manutenção do repositório. Execute
`uv run python -m tools.garbage_collector --help` para consultar a interface.

`configuration.py` valida regras e exceções; `scan.py` enumera caminhos sem
gravar; `inventory.py` e `report.py` produzem somente as saídas documentadas.
Os critérios pertencem ao YAML em `docs/garbage_collector/rules/`, não aos
identificadores das regras no código.
