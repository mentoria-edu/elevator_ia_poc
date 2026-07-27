# Implementar modelos e geração de rodadas do elevador

Este ExecPlan é um documento vivo. As seções `Progresso`, `Surpresas e
Descobertas`, `Registro de Decisões` e `Resultados e Retrospectiva` devem ser
mantidas atualizadas durante a execução do trabalho.

Este documento deve ser mantido de acordo com `PLANS.md`.

## Propósito / Visão geral

Depois desta alteração, o pacote `elevator_vibe_code` poderá representar
andares, passageiros, chamadas, rodadas, eventos e snapshots com objetos
imutáveis e validações explícitas. Também poderá criar uma rodada aleatória
com uma chamada de subida e uma de descida por meio do Faker em português do
Brasil. O comportamento será demonstrado por testes unitários determinísticos
que rejeitam estados inválidos e verificam todas as restrições das rodadas
geradas.

## Progresso

- [x] (2026-07-27 21:01Z) Confirmado que `dev` e `origin/dev` apontavam para
  `2d516cc` e criada a branch `feat/modelos_geracao_elevador`.
- [x] (2026-07-27 21:01Z) Registrado este ExecPlan na pasta de planos ativos.
- [x] (2026-07-27 21:07Z) Implementados e testados os modelos imutáveis do
  domínio; os 26 testes do módulo foram aprovados.
- [x] (2026-07-27 21:12Z) Adicionado Faker 40.32.0 e implementada a geração de
  rodadas; os 5 testes do módulo foram aprovados.
- [x] (2026-07-27 21:15Z) Executadas as validações integrais; 75 testes foram
  aprovados com o fallback de captura documentado.
- [x] (2026-07-27 21:15Z) Registrados os resultados e movido este plano para
  `completed/`.

## Surpresas e Descobertas

- Observação: a execução comum do Pytest no ambiente desta tarefa falhou ao
  encerrar a captura por arquivo com `FileNotFoundError`, embora a coleta e os
  testes estejam íntegros.
  Evidência: o comando padrão reproduziu a falha depois da implementação, e
  `uv run --group dev pytest --capture=sys` aprovou os 75 testes.

- Observação: a adição de Faker 40.32.0 incluiu `tzdata` 2026.3 no lockfile.
  Evidência: `uv lock` informou os dois pacotes adicionados.

## Registro de Decisões

- Decisão: manter o documento temporário de organização não rastreado.
  Justificativa: o próprio documento declara que não pertence à documentação
  oficial e a entrega o utiliza apenas como fonte temporária.
  Data/Autor: 2026-07-27 / Codex.

- Decisão: usar `ValueError` nas violações dos invariantes dos modelos.
  Justificativa: os erros representam valores incompatíveis com o domínio e
  devem informar o valor recebido e a expectativa.
  Data/Autor: 2026-07-27 / Codex.

- Decisão: aceitar uma instância opcional de `faker.Faker` no gerador.
  Justificativa: a instância padrão mantém aleatoriedade real e a injeção
  permite testes repetíveis com `seed_instance`, sem rede.
  Data/Autor: 2026-07-27 / Codex.

## Resultados e Retrospectiva

Os modelos imutáveis, seus invariantes e a geração de rodadas com Faker em
`pt_BR` foram implementados sem incluir motor ou CLI. A suíte final reuniu 75
testes aprovados e obteve 100% de cobertura em `models.py`, 94% em
`generation.py` e 98% no pacote da aplicação. Ruff, o formatador, Mypy, o
lockfile, o validador de ExecPlans e `git diff --check` também foram aprovados.

O único bloqueio observado foi externo ao código: o modo padrão de captura do
Pytest perdeu seu arquivo temporário neste ambiente. A alternativa
`--capture=sys` validou toda a suíte. O documento temporário de organização
permaneceu não rastreado e nenhum arquivo pertencente ao motor, à CLI ou às
regras de negócio foi alterado.

## Contexto e Orientação

O pacote da aplicação fica em `src/elevator_vibe_code/` e ainda contém apenas
seu inicializador. Os testes da aplicação pertencem a `tests/unit/`. O
`pyproject.toml` exige Python 3.14.5 ou superior, mantém dependências de
produção em `[project].dependencies` e usa o lockfile `uv.lock`.

Uma rodada de serviço possui duas chamadas. A chamada de subida começa no
térreo, andar 0, e leva de uma a seis pessoas a destinos entre 1 e 17. A
chamada de descida começa em um único andar entre 1 e 17 e leva de uma a seis
pessoas ao térreo. FIFO significa que a ordem em que as pessoas são criadas é
a mesma ordem em que aparecem no tuple da chamada.

## Plano de Trabalho

Criar `src/elevator_vibe_code/models.py` com as constantes
`GROUND_FLOOR_NUMBER`, `TOP_FLOOR_NUMBER` e `ELEVATOR_CAPACITY`, os enums
`Direction` e `EventKind` e as dataclasses `Floor`, `Passenger`,
`ElevatorCall`, `ServiceRound`, `ElevatorEvent` e `ElevatorSnapshot`. Usar
`frozen=True` e `slots=True` em todas as dataclasses, além de `order=True` em
`Floor`. Validar em `__post_init__` os limites dos andares, as duas formas
permitidas de viagem, capacidade e coerência de chamadas, composição de uma
rodada e uso de passageiros nos eventos.

Criar `tests/unit/test_models.py` para observar valores públicos,
imutabilidade, ordenação e aceitação ou rejeição de cada invariante.

Adicionar `faker==40.32.0` às dependências de produção e regenerar `uv.lock`
com uv. Criar `src/elevator_vibe_code/generation.py` com o protocolo
`RoundGenerator` e `FakerPassengerGenerator`. A implementação usa
`Faker("pt_BR")` por padrão, aceita uma instância injetada, sorteia as
quantidades separadamente e devolve tuples na ordem de criação. Criar
`tests/unit/test_generation.py` com Faker semeado para provar repetibilidade e
as restrições de várias rodadas sem depender de nomes específicos.

Ao final, formatar somente os novos arquivos quando necessário, executar toda
a suíte de qualidade e mover este documento para
`docs/exec_plans/completed/implementar_modelos_geracao_elevador.md`.

## Etapas Concretas

Trabalhar em `/home/kuuhaku/repos/elevator_ia_poc` e executar:

    uv lock
    uv lock --check
    uv run --group dev ruff check .
    uv run --group dev ruff format --check .
    uv run --group dev mypy
    uv run --group dev pytest
    uv run python -m tools.validators.check_exec_plans
    git diff --check

Se o erro ambiental de captura do Pytest reaparecer, repetir a comprovação com:

    uv run --group dev pytest --capture=sys

## Validação e Aceitação

Os testes de modelos devem demonstrar que andares -1 e 18 são rejeitados;
somente viagens do térreo para cima ou de cima para o térreo são aceitas;
chamadas sempre possuem entre uma e seis pessoas coerentes; e cada rodada
contém a chamada de subida e a de descida esperadas. Eventos que não sejam de
entrada ou saída devem rejeitar passageiros.

Os testes de geração devem demonstrar que duas instâncias semeadas produzem a
mesma rodada, que cada fila contém entre uma e seis pessoas, que nomes e
identificadores não são vazios e que todas as origens, destinos e direções são
válidos. Todas as validações listadas nas etapas concretas devem terminar com
código zero, salvo a falha ambiental de captura já documentada, que deve ser
contornada por `--capture=sys`.

## Idempotência e Recuperação

As adições são independentes e os comandos uv podem ser repetidos com
segurança. `uv.lock` nunca deve ser editado manualmente: em caso de falha,
corrigir `pyproject.toml` e executar `uv lock` novamente. Nenhum arquivo
temporário de organização deve ser adicionado ao Git.

## Artefatos e Notas

Os artefatos funcionais são `models.py`, `generation.py` e seus dois módulos
de teste. `pyproject.toml` e `uv.lock` registram Faker 40.32.0. Este ExecPlan é
o único artefato de processo adicional.

## Interfaces e Dependências

`elevator_vibe_code.models` expõe as três constantes, `Floor`, `Direction`,
`Passenger`, `ElevatorCall`, `ServiceRound`, `EventKind`, `ElevatorEvent` e
`ElevatorSnapshot`. `elevator_vibe_code.generation` expõe:

    class RoundGenerator(Protocol):
        def generate_round(self) -> ServiceRound:
            ...

    class FakerPassengerGenerator:
        def __init__(self, faker_instance: Faker | None = None) -> None:
            ...

        def generate_round(self) -> ServiceRound:
            ...

Faker 40.32.0 é a única dependência nova e fica encapsulada no módulo de
geração.

## Integração posterior

Nota de alteração (2026-07-27): depois desta entrega independente, foi
executado um novo workflow de integração documentado pelo ExecPlan
`integrar_componentes_elevador.md`, arquivado em
`docs/exec_plans/completed/integrar_componentes_elevador.md`. O workflow
sincronizou Faker 40.32.0 pelo lockfile, tornou `--capture=sys` parte do
comando padrão do Pytest e comprovou o gerador semeado com modelos, motor e CLI
reais. O registro acima permanece como evidência histórica das restrições
existentes na branch independente.
