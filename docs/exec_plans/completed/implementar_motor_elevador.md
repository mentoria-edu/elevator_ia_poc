# Implementar o motor do elevador

Este ExecPlan é um documento vivo. As seções `Progresso`, `Surpresas e
Descobertas`, `Registro de Decisões` e `Resultados e Retrospectiva` devem ser
mantidas atualizadas durante a execução do trabalho.

Este documento deve ser mantido de acordo com `PLANS.md`.

## Propósito / Visão geral

O pacote passará a oferecer um motor determinístico para executar uma rodada
de atendimento do elevador andar por andar. Quem integrar os modelos de
domínio poderá iniciar uma rodada, avançar uma transição por vez, observar
eventos cronológicos e consultar um retrato imutável do estado. Os testes
unitários demonstrarão capacidade, filas FIFO, prioridade, tempos e ordem dos
eventos.

## Progresso

- [x] (2026-07-27 20:19Z) Lidos arquitetura, padrões, regras de negócio,
  proposta de modelagem e contratos congelados.
- [x] (2026-07-27 20:19Z) Criada a branch `feat/elevator_engine` a partir de
  `dev` e registrado este ExecPlan.
- [x] (2026-07-27 20:23Z) Implementado o motor e atualizada a regra de
  tempo das portas.
- [x] (2026-07-27 20:25Z) Adicionados 14 testes unitários observáveis para o
  motor.
- [x] (2026-07-27 20:27Z) Executadas as validações, registrados os resultados
  e arquivado este ExecPlan.

## Surpresas e Descobertas

- Observação: a branch-base ainda não contém
  `src/elevator_vibe_code/models.py`.
  Evidência: a listagem dos arquivos rastreados contém apenas
  `src/elevator_vibe_code/__init__.py` no pacote da aplicação.

- Observação: os testes do motor podem ser exercitados sem versionar uma
  duplicação dos modelos, carregando em memória as assinaturas congeladas.
  Evidência: os 14 testes de `tests/unit/test_elevator.py` passaram em 0,05
  segundo com esse contrato temporário.

- Observação: Mypy e a coleta completa do Pytest param exclusivamente no
  import do módulo de modelos ausente.
  Evidência: Mypy informou dois erros `import-untyped`, em `elevator.py` e
  `test_elevator.py`; o Pytest coletou os 44 testes anteriores e parou ao
  importar o novo teste com `ModuleNotFoundError`.

## Registro de Decisões

- Decisão: implementar somente o motor contra os imports públicos congelados,
  sem duplicar os modelos ausentes.
  Justificativa: modelos, geração, Faker, dependências e CLI pertencem a
  entregas independentes e estão explicitamente fora deste escopo.
  Data/Autor: 2026-07-27 / Codex

- Decisão: com a cabine vazia, buscar a chamada de origem mais próxima e
  desempatar em favor da chamada de subida.
  Justificativa: as regras exigem determinismo, mas não definem a prioridade
  entre duas chamadas externas à mesma distância.
  Data/Autor: 2026-07-27 / Codex

- Decisão: cada chamada de `step()` avançará no máximo um andar e, ao atender
  uma parada, retornará a sequência completa e atômica de eventos da parada.
  Justificativa: isso permite acompanhamento andar por andar sem expor estados
  intermediários de porta.
  Data/Autor: 2026-07-27 / Codex

## Resultados e Retrospectiva

O motor foi implementado com deslocamento andar por andar, paradas atômicas,
capacidade seis, filas FIFO, prioridade dos passageiros embarcados, busca
determinística de chamadas e relógio cumulativo. A regra de negócio agora
registra o custo de abertura e fechamento, e 14 testes cobrem o comportamento
novo.

Ruff, formatação, `uv lock --check`, os 44 testes preexistentes, o validador de
ExecPlans e `git diff --check` foram aprovados. Os 14 testes novos também
passaram contra os contratos congelados carregados somente em memória. A
validação integral continua bloqueada, conforme previsto para esta entrega
independente, até que `elevator_vibe_code.models` seja integrado; nenhum tipo
substituto foi adicionado à branch.

## Contexto e Orientação

O pacote da aplicação fica em `src/elevator_vibe_code/` e os testes unitários
em `tests/unit/`. O novo módulo `elevator.py` depende dos tipos imutáveis
`Floor`, `Passenger`, `ServiceRound`, `ElevatorEvent`, `ElevatorSnapshot`,
`Direction` e `EventKind`, além da constante `ELEVATOR_CAPACITY`, todos
pertencentes ao módulo independente `elevator_vibe_code.models`.

Uma rodada contém uma fila de subida no térreo e uma fila de descida em um
andar superior. FIFO significa que pessoas entram na mesma ordem em que
aparecem na chamada. Uma transição operacional é um deslocamento de no máximo
um andar, acompanhado da sequência completa de atendimento caso esse andar
seja uma parada.

## Plano de Trabalho

Criar `src/elevator_vibe_code/elevator.py` com a classe pública `Elevator`.
Copiar as filas da rodada para listas privadas, preservar a cabine dentro da
capacidade seis e devolver apenas tuplas em eventos e snapshots. Passageiros
já embarcados determinam o próximo destino; uma fila encontrada no trajeto
somente embarca na mesma direção e quando há vaga. Sem passageiros na cabine,
a origem pendente mais próxima será escolhida.

O deslocamento soma um segundo por andar. Uma parada emite chegada, soma um
segundo e emite abertura, emite saídas e entradas sem alterar o relógio, soma
um segundo e emite fechamento. Depois disso, emite uma eventual inversão e,
quando não resta trabalho, o evento ocioso. Atualizar a seção de tempo de
`docs/business_rules/regras_elevador.md` com as mesmas regras.

Criar `tests/unit/test_elevator.py` usando os contratos públicos congelados.
Os testes devem cobrir capacidade, FIFO, prioridade, coleta no trajeto, porta,
relógio, eventos, rodadas sucessivas, equivalência das APIs de execução e
imutabilidade do snapshot.

## Etapas Concretas

No diretório `/home/leoadelmo/elevator_vibe_code`, executar:

    uv run --group dev ruff check .
    uv run --group dev ruff format --check .
    uv run --group dev mypy
    uv run --group dev pytest
    uv run python -m tools.validators.check_exec_plans
    git diff --check

Ruff, o formatador, `uv lock --check`, os 44 testes preexistentes, o validador
e a verificação de diff terminaram com código zero. Mypy retornou dois erros
de importação e o Pytest completo retornou erro de coleta porque a entrega
independente de `elevator_vibe_code.models` ainda não está disponível.

## Validação e Aceitação

Com os modelos integrados, os testes devem provar que todos os andares
percorridos geram um evento, portas abrem apenas para entrada ou saída,
capacidade e FIFO são preservados e o relógio contabiliza movimento e portas.
Chamadas repetidas de `step()` devem produzir exatamente a mesma sequência de
`run_until_idle()`. Depois do evento ocioso, o elevador deve permanecer no
último andar atendido e aceitar uma nova rodada.

## Idempotência e Recuperação

As validações são somente leitura, exceto por caches ignorados. A criação dos
arquivos é aditiva e pode ser retomada consultando `Progresso`. O documento
temporário não rastreado em `docs/plan_proposals/` deve permanecer intocado.
Nenhuma operação destrutiva é necessária.

## Artefatos e Notas

A entrega altera o motor, seu teste, a regra de tempo das portas e este
ExecPlan obrigatório. Bloqueios decorrentes da ausência dos modelos serão
registrados sem ampliar o escopo.

As evidências finais são:

    Ruff: All checks passed!
    Formatação: 24 files already formatted
    Testes novos com contratos em memória: 14 passed in 0.05s
    Testes preexistentes: 44 passed in 0.22s
    ExecPlans: estrutura válida.
    Mypy: 2 import-untyped errors para elevator_vibe_code.models
    Pytest completo: ModuleNotFoundError para elevator_vibe_code.models

## Interfaces e Dependências

`elevator_vibe_code.elevator.Elevator` terá as assinaturas:

    def __init__(self, initial_floor: Floor | None = None) -> None
    def start_round(self, service_round: ServiceRound) -> None
    def step(self) -> tuple[ElevatorEvent, ...]
    def run_until_idle(self) -> tuple[ElevatorEvent, ...]
    def snapshot(self) -> ElevatorSnapshot

Não haverá nova biblioteca. O módulo usará somente a biblioteca padrão e os
contratos de `elevator_vibe_code.models`.

Nota de alteração (2026-07-27): criado para executar a entrega independente
do motor do elevador na branch solicitada e atualizado ao final com as
evidências e o bloqueio esperado de integração dos modelos.
