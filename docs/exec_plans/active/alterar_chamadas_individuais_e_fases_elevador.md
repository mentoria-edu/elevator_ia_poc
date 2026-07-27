# Implementar solicitações individuais e fases sequenciais do elevador

Este ExecPlan é um documento vivo. As seções `Progresso`, `Surpresas e
Descobertas`, `Registro de Decisões` e `Resultados e Retrospectiva` devem ser
mantidas atualizadas durante a execução. Este documento segue `PLANS.md`,
localizado na raiz do repositório.

## Propósito / Visão geral

Hoje a demonstração cria antecipadamente uma rodada com uma única chamada de
subida e uma única chamada de descida. Depois desta alteração, cada pessoa será
uma solicitação individual, inclusive quando duas pessoas estiverem no mesmo
andar. A pessoa usuária verá primeiro a lista da subida; somente após o último
desembarque dessa fase verá os novos passageiros e as origens da descida.

O comportamento pode ser observado com
`uv run python -m elevator_vibe_code demo --rounds 2 --step-delay 0`. Em cada
rodada, a lista `Subida:` deve preceder seus eventos, a lista `Descida:` deve
aparecer depois do último desembarque da subida e antes do primeiro evento da
descida, e o resumo deve terminar com cabine e filas vazias.

## Progresso

- [x] (2026-07-27 23:33Z) Investigados proposta, arquitetura, padrões, regras
  de negócio, contratos, testes e estado do Git.
- [x] (2026-07-27 23:33Z) Criada a branch
  `feat/add_novas_regras_elevador` a partir de `373319c`.
- [ ] Migrar os modelos e o gerador para fases independentes.
- [ ] Adaptar o motor para solicitações com origens individuais.
- [ ] Integrar a orquestração sequencial e a apresentação na CLI.
- [ ] Atualizar regras de negócio, arquitetura e testes de composição.
- [ ] Executar todas as validações e mover este plano para `completed/`.

## Surpresas e Descobertas

- Observação: a proposta que origina o trabalho ainda não estava rastreada,
  assim como um segundo arquivo de organização que pertence a outro trabalho.
  Evidência: o estado inicial do Git mostrou ambos com `??`.

- Observação: `uv` não está no `PATH` da sessão, embora esteja instalado em
  `/home/lvaz/.local/bin/uv`.
  Evidência: a validação pelo nome retornou código 127 e a execução pelo
  caminho absoluto aprovou 115 testes.

## Registro de Decisões

- Decisão: criar a branch a partir do HEAD de `feat/step_delay_cli`.
  Justificativa: a pessoa usuária confirmou que a nova funcionalidade deve
  preservar o delay configurável recém-implementado.
  Data/Autor: 2026-07-27 / Codex e pessoa usuária.

- Decisão: representar uma fase por `ServicePhase`, contendo direção e uma
  tupla ordenada de `Passenger`.
  Justificativa: `Passenger` já preserva todos os dados de uma solicitação; um
  segundo invólucro por pessoa seria redundante, enquanto o modelo de fase
  centraliza quantidade, direção e imutabilidade.
  Data/Autor: 2026-07-27 / Codex e pessoa usuária.

- Decisão: remover os contratos antigos sem camada de compatibilidade.
  Justificativa: a proposta pede explicitamente a substituição da rodada
  pré-gerada por fases geradas e executadas separadamente.
  Data/Autor: 2026-07-27 / Codex e pessoa usuária.

- Decisão: escolher a origem pendente mais próxima e usar a ordem da
  solicitação como desempate.
  Justificativa: conserva a regra atual de proximidade, torna múltiplas origens
  determinísticas e preserva FIFO quando as distâncias são iguais.
  Data/Autor: 2026-07-27 / Codex e pessoa usuária.

## Resultados e Retrospectiva

Ainda não há resultados de implementação. Esta seção será atualizada ao final
de cada marco e na conclusão.

## Contexto e Orientação

`src/elevator_vibe_code/models.py` contém valores imutáveis, passageiros,
chamadas, rodadas, eventos e snapshots. `src/elevator_vibe_code/generation.py`
usa Faker para construir toda a rodada antecipadamente.
`src/elevator_vibe_code/elevator.py` recebe essa rodada em `start_round()` e
mantém uma fila agregada por direção. `src/elevator_vibe_code/cli.py` gera,
apresenta e inicia as duas chamadas juntas antes de avançar o motor com
`step()`.

Uma fase é um período no qual todas as solicitações possuem a mesma direção.
Na subida, toda origem é o térreo e cada destino superior é independente. Na
descida, cada origem superior é independente e todo destino é o térreo. A
quantidade de solicitações de cada fase fica entre um e seis, que é a
capacidade do elevador.

O snapshot continuará expondo `upward_waiting` e `downward_waiting`, embora
somente uma dessas filas possa estar ativa por fase. O relógio e o andar atual
pertencem ao elevador, não à fase; por isso continuam acumulados entre subida
e descida e entre rodadas.

## Plano de Trabalho

Em `models.py`, substituir `ElevatorCall` e `ServiceRound` por `ServicePhase`.
O novo modelo terá `direction` e `requests`, rejeitará direção ociosa, vazio,
mais de seis solicitações e passageiros com direção divergente. As validações
existentes de `Passenger` continuarão garantindo térreo, andar superior e
direção coerentes.

Em `generation.py`, substituir `RoundGenerator` por `PhaseGenerator`. O
protocolo e `FakerPassengerGenerator` exporão `generate_upward_phase()` e
`generate_downward_phase()`. Cada pessoa fará seu próprio sorteio de destino
ou origem; a implementação não armazenará a primeira fase para produzir a
segunda.

Em `elevator.py`, substituir `start_round()` por `start_phase()`. O motor
preencherá somente a fila correspondente à direção da fase. A consulta de
espera no andar atual filtrará passageiros pela origem individual sem
reordenar a fila. Quando a cabine estiver vazia, a próxima origem será a de
menor distância; empates respeitarão a posição na tupla. O término de cada
fase produzirá `IDLE` sem reposicionar o elevador nem zerar o relógio.

Em `cli.py`, substituir o protocolo e as referências a rodadas. Para cada
rodada solicitada, gerar e imprimir a subida, executá-la até ociosa, gerar e
imprimir a descida, executá-la e então emitir o resumo. Cada linha de
solicitação mostrará nome, origem e destino. A geração da descida ficará
depois do retorno terminal da rotina de passos, tornando a ordem observável em
testes. O delay continuará ocorrendo somente entre passos não terminais.

Atualizar os quatro arquivos em `tests/unit/` para os novos contratos e para
os cenários da proposta. Atualizar `ARCHITECTURE.md` e
`docs/business_rules/regras_elevador.md`. Adicionar ao controle de versão a
proposta que originou o trabalho, sem alterar nem adicionar o arquivo
`docs/plan_proposals/organizacao_implementacao_elevador.md`.

## Etapas Concretas

Todos os comandos partem de
`/home/lvaz/projetos/elevator_ia_poc`. Após cada marco, executar os testes
unitários afetados. Ao final, executar:

    /home/lvaz/.local/bin/uv run --group dev ruff check .
    /home/lvaz/.local/bin/uv run --group dev ruff format --check .
    /home/lvaz/.local/bin/uv run --group dev mypy
    /home/lvaz/.local/bin/uv run --group dev pytest
    /home/lvaz/.local/bin/uv run python -m tools.validators.check_exec_plans
    /home/lvaz/.local/bin/uv run python -m elevator_vibe_code demo --rounds 2 --step-delay 0

Depois de registrar os resultados, mover este arquivo de `active/` para
`completed/`. Os commits devem ser pequenos, imperativos e limitados aos
marcos desta implementação.

## Validação e Aceitação

Os testes de modelos devem demonstrar imutabilidade, limites, coerência de
direção, FIFO e andares repetidos. Os testes de geração devem demonstrar
sorteios separados, limites de andares e reprodução por semente. Os testes do
motor devem cobrir múltiplas origens, capacidade, FIFO, proximidade,
desempate, equivalência entre `step()` e `run_until_idle()` e preservação de
andar e tempo entre fases.

Os testes da CLI devem usar fakes nomeados para provar que
`generate_downward_phase()` ocorre depois do evento terminal da subida e que a
lista da descida precede seu primeiro evento. Também devem preservar os
argumentos, o delay, os resumos de múltiplas rodadas e uma composição
determinística com as implementações reais.

A aceitação final exige código zero nos seis comandos, saída demonstrando as
duas listas em ordem e snapshot terminal com cabine, fila de subida e fila de
descida vazias.

## Idempotência e Recuperação

Testes e demonstrações podem ser repetidos sem efeitos externos. A branch já
foi criada no commit correto; se uma edição falhar, ela pode ser reaplicada
sem recriar a branch. Nenhuma rede, persistência, migração ou exclusão está
envolvida. O arquivo não rastreado de organização deve permanecer intocado.

## Artefatos e Notas

A saída essencial de uma rodada terá esta forma:

    Rodada 1
    Subida:
    - Ana Souza | chamada no andar 00 | destino 07
    ... eventos da subida ...
    Descida:
    - Maria Alves | chamada no andar 05 | destino 00
    ... eventos da descida ...
    Resumo: Andar final 00 | Tempo MM:SS | Atendidos N | Filas: subida 0, descida 0

## Interfaces e Dependências

Não serão adicionadas dependências. As interfaces finais serão:

    @dataclass(frozen=True, slots=True)
    class ServicePhase:
        direction: Direction
        requests: tuple[Passenger, ...]

    class PhaseGenerator(Protocol):
        def generate_upward_phase(self) -> ServicePhase: ...
        def generate_downward_phase(self) -> ServicePhase: ...

    class Elevator:
        def start_phase(self, phase: ServicePhase) -> None: ...
        def step(self) -> tuple[ElevatorEvent, ...]: ...
        def run_until_idle(self) -> tuple[ElevatorEvent, ...]: ...
        def snapshot(self) -> ElevatorSnapshot: ...

`FakerPassengerGenerator` implementará `PhaseGenerator`. `main()` continuará
aceitando `generator`, `output` e `sleeper`, mas o tipo de `generator` passará
a ser `PhaseGenerator`.
