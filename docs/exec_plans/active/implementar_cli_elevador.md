# Implementar a CLI do elevador de forma independente

Este ExecPlan é um documento vivo. As seções `Progresso`, `Surpresas e Descobertas`, `Registro de Decisões` e `Resultados e Retrospectiva` devem ser mantidas atualizadas durante a execução do trabalho.

Este documento deve ser mantido de acordo com `PLANS.md`.

## Propósito / Visão geral

Depois desta alteração, uma pessoa poderá acompanhar pela linha de comando as chamadas e os eventos produzidos por uma simulação do elevador. A interface aceitará `demo` para uma rodada e `demo --rounds N` para várias rodadas, imprimirá os passageiros em ordem e encerrará cada rodada com um resumo.

Esta parte será desenvolvida sem incorporar as implementações de modelos, geração ou motor atribuídas a outras pessoas. Os testes substituirão essas dependências por objetos configurados com `unittest.mock`, permitindo validar isoladamente os argumentos, a orquestração e a apresentação.

## Progresso

- [x] (2026-07-27 00:46Z) Investigados a arquitetura, os padrões e os contratos públicos da CLI.
- [x] (2026-07-27 00:46Z) Criado este ExecPlan com a estratégia de isolamento.
- [x] (2026-07-27 00:56Z) Implementada e testada a formatação dos oito tipos de evento.
- [x] (2026-07-27 01:12Z) Implementados e testados argumentos e uma rodada isolada.
- [ ] Implementar e testar rodadas sucessivas e seus resumos.
- [ ] Expor o ponto de entrada do pacote e executar todas as validações.
- [ ] Arquivar este plano em `docs/exec_plans/completed/implementar_cli_elevador.md`.

## Surpresas e Descobertas

- Observação: o commit-base ainda não contém `models.py`, `generation.py` nem `elevator.py`.
  Evidência: em 2026-07-27, `src/elevator_vibe_code/` continha somente `__init__.py`.

- Observação: o executável `uv` não está disponível no ambiente de implementação.
  Evidência: `uv run python -m tools.validators.check_exec_plans` encerrou com código 127 e `/bin/bash: uv: command not found`; somente `python3` e `pytest` foram encontrados no `PATH`.

- Observação: `Mock(name=...)` define o nome interno do mock, não o atributo de domínio `.name`.
  Evidência: os testes de passageiros passaram depois que `passenger.name` foi configurado explicitamente; 13 testes da CLI estão aprovados.

## Registro de Decisões

- Decisão: carregar modelos somente para análise estática e importar as implementações concretas dentro de fábricas privadas.
  Justificativa: `cli.py` precisa ser importável nos testes isolados mesmo antes de as outras partes existirem.
  Data/Autor: 2026-07-27 / Codex.

- Decisão: usar `unittest.mock.Mock` e `patch` nos testes da CLI.
  Justificativa: os mocks observam as interações da camada de apresentação sem reproduzir regras do motor.
  Data/Autor: 2026-07-27 / Codex.

## Resultados e Retrospectiva

A implementação ainda não começou. Ao final, esta seção registrará os comportamentos entregues, as validações executadas e a dependência restante para executar o comando real.

## Contexto e Orientação

O código da aplicação está em `src/elevator_vibe_code/`, e seus testes unitários ficam em `tests/unit/`. Esta tarefa cria `src/elevator_vibe_code/cli.py`, `src/elevator_vibe_code/__main__.py` e `tests/unit/test_cli.py`. Ela não cria nem altera arquivos das outras partes.

Os contratos compartilhados definem `ElevatorEvent` com tempo acumulado, andar, direção, tipo do evento e passageiros; `RoundGenerator` com `generate_round()`; e `Elevator` com `start_round()`, `run_until_idle()` e `snapshot()`. Uma rodada contém chamadas de subida e descida, e cada chamada contém andar, direção e passageiros.

`format_event()` terá a assinatura `format_event(event: ElevatorEvent) -> str`. `main()` terá os parâmetros `argv`, `generator` e `output`, permitindo controlar argumentos, geração e saída nos testes. O motor será criado por uma fábrica privada substituída com `patch`.

## Plano de Trabalho

Primeiro, criar `cli.py` com a formatação dos oito tipos de evento. O texto seguirá `[MM:SS] Andar NN | DIREÇÃO | Descrição`; entrada e saída acrescentarão os nomes na ordem recebida.

Depois, adicionar o analisador de argumentos e as fábricas tardias. `demo` executará uma rodada por padrão. `--rounds` aceitará somente inteiros positivos. Antes de cada rodada, a CLI imprimirá as duas chamadas. Em seguida, iniciará o motor, imprimirá os eventos retornados e produzirá um resumo a partir dos snapshots.

Para várias rodadas, a mesma instância do elevador será reutilizada. A duração individual será a diferença entre o tempo do snapshot anterior ao início e o tempo do snapshot final. O total atendido será a quantidade de passageiros das duas chamadas, e os tamanhos das filas virão do snapshot final.

Por fim, criar `__main__.py`, concluir as validações e mover este plano para `completed/`.

## Etapas Concretas

No diretório `/home/lvaz/projetos/elevator_ia_poc`, validar cada estágio com:

    uv run --group dev ruff check src/elevator_vibe_code/cli.py tests/unit/test_cli.py
    uv run --group dev ruff format --check src/elevator_vibe_code/cli.py tests/unit/test_cli.py
    uv run --group dev mypy
    uv run --group dev pytest tests/unit/test_cli.py
    uv run python -m tools.validators.check_exec_plans

Ao concluir, executar também:

    uv run --group dev pytest

Quando as outras partes estiverem disponíveis, a demonstração real poderá ser observada com:

    uv run python -m elevator_vibe_code demo
    uv run python -m elevator_vibe_code demo --rounds 3

## Validação e Aceitação

Os testes devem comprovar que os oito tipos de evento são formatados, que nomes preservam a ordem recebida, que `demo` executa uma rodada, que `demo --rounds 3` executa exatamente três rodadas na mesma instância e que valores inválidos de `--rounds` causam `SystemExit` com código 2.

A saída deve apresentar chamadas antes dos eventos e um resumo depois deles. Os testes devem usar `StringIO`, `Mock`, `patch`, `side_effect` e verificações de chamadas. Nenhum teste pode importar Faker ou executar o motor real.

A entrega isolada é aceita quando Ruff, mypy, `tests/unit/test_cli.py` e o validador de ExecPlans retornarem código zero. A suíte completa também deve continuar aprovada.

## Idempotência e Recuperação

As alterações são aditivas e podem ser reaplicadas com segurança. Se um estágio falhar, corrigir somente os arquivos daquele estágio e repetir seus comandos. Nenhuma migração, exclusão de dados ou serviço externo está envolvido.

## Artefatos e Notas

Os únicos arquivos de produto permitidos são `src/elevator_vibe_code/cli.py`, `src/elevator_vibe_code/__main__.py` e `tests/unit/test_cli.py`. Este ExecPlan é o único arquivo adicional de processo.

## Interfaces e Dependências

Em `src/elevator_vibe_code/cli.py`, expor:

    def format_event(event: ElevatorEvent) -> str:
        ...

    def main(
        argv: Sequence[str] | None = None,
        *,
        generator: RoundGenerator | None = None,
        output: TextIO | None = None,
    ) -> int:
        ...

O módulo usará somente a biblioteca padrão. `_create_generator()` importará `FakerPassengerGenerator` dentro da função, e `_create_elevator()` importará `Elevator` dentro da função. Essas fábricas serão privadas e não alterarão o contrato público.
