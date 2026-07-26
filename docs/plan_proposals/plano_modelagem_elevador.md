# Proposta: modelagem do elevador com acompanhamento pela CLI

## Resumo

Criar `docs/plan_proposals/plano_modelagem_elevador.md` propondo uma simulação em rodadas sucessivas. Cada rodada terá uma chamada de subida e outra de descida, com um a seis usuários aleatórios nomeados pelo Faker.

A CLI exibirá cronologicamente o deslocamento por cada andar, direção, abertura e fechamento das portas e os nomes das pessoas que entram e saem.

## Modelagem e interfaces

- Representar `Floor`, `Passenger`, `Direction`, `ElevatorCall`, `ServiceRound`, eventos e snapshots com tipos de domínio imutáveis e explicitamente anotados.
- Cada `Passenger` terá identificador, nome, origem, destino e direção.
- Cada rodada terá:
  - uma fila FIFO de subida no térreo, com destinos aleatórios entre `1` e `17`;
  - uma fila FIFO de descida em um andar superior aleatório, com destino no térreo;
  - entre um e seis usuários em cada fila, sorteados independentemente.
- Encapsular `Faker==40.32.0` em `FakerPassengerGenerator`, usando locale `pt_BR`.
- Permitir a injeção de um gerador previsível nos testes, mantendo aleatoriedade real na CLI.
- Expor `Elevator` com:
  - `start_round(service_round)`;
  - `step()`;
  - `run_until_idle()`;
  - `snapshot()`.
- Aceitar uma nova rodada somente quando não houver pessoas na cabine ou nas filas.
- Limitar a cabine a seis pessoas e preservar a ordem FIFO.
- Priorizar destinos dos passageiros embarcados. Coletas durante o trajeto não poderão provocar uma inversão antecipada da direção.
- Manter o elevador no último andar atendido ao ficar ocioso.

## Eventos e regras da CLI

Definir eventos tipados para:

- andar percorrido;
- chegada a um andar de atendimento;
- abertura da porta;
- passageiros que saíram;
- passageiros que entraram;
- fechamento da porta;
- mudança de direção;
- elevador ocioso.

Aplicar as seguintes regras:

- Percorrer um andar consecutivo consome um segundo.
- Abrir a porta consome um segundo.
- Fechar a porta consome um segundo.
- Embarque e desembarque não acrescentam tempo.
- A porta abre somente quando pelo menos uma pessoa efetivamente entra ou sai.
- Se a cabine estiver cheia e ninguém desembarcar, uma fila encontrada no trajeto permanece pendente sem abertura da porta.
- Em uma parada, a ordem dos eventos será:
  1. chegada ao andar;
  2. porta abrindo;
  3. passageiros saindo;
  4. passageiros entrando;
  5. porta fechando;
  6. atualização da direção.
- Passageiros devem sair antes da entrada de novos passageiros.
- Cada andar percorrido deve produzir uma linha, inclusive quando o elevador não parar.
- Toda linha deve informar tempo acumulado, andar atual, direção e evento.
- Linhas de embarque e desembarque devem listar os nomes das pessoas na ordem FIFO.
- Durante o deslocamento, a direção será `SUBINDO` ou `DESCENDO`.
- Durante portas, embarques e desembarques, a linha preservará a direção de chegada.
- Depois do fechamento, uma eventual inversão será registrada por um evento próprio.
- Ao terminar a rodada, a direção será `PARADO`.

Formato esperado:

```text
[00:01] Andar 1 | SUBINDO  | Passando
[00:02] Andar 2 | SUBINDO  | Chegada
[00:03] Andar 2 | SUBINDO  | Porta abrindo
[00:03] Andar 2 | SUBINDO  | Saíram: Ana Souza
[00:03] Andar 2 | SUBINDO  | Entraram: Carlos Lima, Maria Alves
[00:04] Andar 2 | SUBINDO  | Porta fechando
[00:04] Andar 2 | DESCENDO | Direção alterada
```

Disponibilizar:

```bash
python -m elevator_vibe_code demo
python -m elevator_vibe_code demo --rounds 3
```

Ao final de cada rodada, imprimir andar final, tempo total, passageiros atendidos e situação das filas.

Atualizar `docs/business_rules/regras_elevador.md` para registrar que abertura e fechamento consomem um segundo cada, substituindo a regra anterior que excluía o tempo das portas.

## Testes e aceitação

Adicionar testes em `tests/unit/` cobrindo:

- duas chamadas e duas filas por rodada;
- geração de um a seis usuários em cada fila;
- nomes não vazios produzidos pelo gerador;
- origens, destinos e direções válidos;
- embarque FIFO e capacidade máxima;
- passagem registrada em cada andar;
- abertura de porta apenas com embarque ou desembarque efetivo;
- ausência de abertura quando a cabine cheia passa por uma fila;
- ordem entre abertura, saída, entrada e fechamento;
- nomes corretos nos eventos de entrada e saída;
- direção presente em todos os eventos;
- registro da inversão de direção;
- um segundo por andar, um segundo para abrir e um para fechar;
- ausência de tempo adicional para entrada e saída;
- permanência no último andar atendido;
- rejeição de uma nova rodada enquanto a atual estiver ativa;
- rodadas sucessivas depois do estado ocioso;
- equivalência entre `step()` e `run_until_idle()`;
- saída cronológica e código zero da CLI.

Os testes usarão um gerador fake nomeado e cenários predeterminados. A CLI continuará realmente aleatória.

Validar com:

```bash
uv run --group dev ruff check .
uv run --group dev ruff format --check .
uv run --group dev mypy
uv run --group dev pytest
uv run python -m tools.validators.check_exec_plans
```

## Premissas

- O prédio possui os andares `0` a `17`.
- A capacidade máxima é seis pessoas.
- Cada rodada contém exatamente uma chamada de subida e uma de descida.
- Não entram novas chamadas durante uma rodada.
- A aleatoriedade afeta somente a criação dos usuários e chamadas; a movimentação permanece determinística.
- A CLI é uma apresentação dos eventos produzidos pelo domínio, não contém regras próprias de movimentação.
- Não serão incluídos persistência, rede ou interface gráfica.
- Depois de aprovada, a proposta será convertida em ExecPlan em `docs/exec_plans/active/`.
