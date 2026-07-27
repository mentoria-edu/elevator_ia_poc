# Proposta: chamadas individuais e fases sequenciais de subida e descida

## Resumo

Alterar o modelo atual do elevador, no qual cada fase possui uma chamada
agregada em um único andar. Cada usuário passará a representar uma solicitação
individual, com andar de origem sorteado independentemente quando aplicável.

A fase de subida será concluída antes que a fase de descida seja criada. No
início da descida, a CLI apresentará os novos usuários e os andares em que
deverá buscá-los. A movimentação continuará determinística; somente pessoas e
andares serão aleatórios.

## Regras de negócio

- A fase de subida terá entre um e seis usuários.
- Cada usuário da subida terá nome aleatório, origem no térreo e destino
  aleatório entre os andares `1` e `17`.
- A CLI exibirá cada usuário da subida e seu andar de destino antes do primeiro
  evento de deslocamento.
- A fase de descida será iniciada somente depois que o último usuário da subida
  desembarcar.
- No início da descida serão sorteados entre um e seis usuários novos,
  independentes dos passageiros da subida.
- Cada usuário da descida terá nome aleatório, origem aleatória entre `1` e
  `17` e destino no térreo.
- A CLI exibirá cada usuário da descida e seu andar de origem antes do primeiro
  evento de atendimento da descida.
- O sorteio de cada usuário será independente. Dois usuários podem receber o
  mesmo andar, mas continuarão sendo solicitações individuais, sem agrupamento
  automático em uma chamada compartilhada.
- A descida seguirá as mesmas regras operacionais da subida: capacidade máxima
  de seis pessoas, filas FIFO, embarque, desembarque, portas, deslocamento e
  atendimento completo das solicitações.
- A aleatoriedade não alterará a ordem dos eventos nem as regras de direção do
  motor.

## Modelagem e interfaces

Substituir a representação singular `upward_call`/`downward_call` por coleções
ordenadas de solicitações individuais. Cada solicitação deverá preservar o
`Passenger` completo: identificador, nome, origem, destino e direção. Os
modelos deverão continuar imutáveis e validar os limites de andar, a direção e
a origem/destino compatíveis.

O gerador deverá expor operações separadas para as duas fases, mantendo a
injeção de um gerador fake nos testes:

- gerar as solicitações de subida;
- gerar as solicitações de descida.

A operação de descida não poderá ser chamada durante a geração ou apresentação
da subida. O protocolo deverá deixar explícito que a segunda geração acontece
somente após o último desembarque da primeira fase.

O motor deverá processar uma fase por vez. O fluxo público deverá permitir:

1. iniciar a fase de subida com suas solicitações;
2. executar `step()` até todos os passageiros da subida desembarcarem;
3. iniciar a fase de descida com as solicitações recém-geradas;
4. executar `step()` até o elevador ficar ocioso;
5. consultar `snapshot()` para confirmar cabine e filas vazias.

`run_until_idle()` deverá continuar disponível quando fizer sentido e produzir
os mesmos eventos que chamadas sucessivas de `step()` dentro de uma fase. O
motor deverá iniciar a descida no andar em que terminou a subida e não deverá
retornar automaticamente ao térreo antes de buscar os passageiros da descida.

## Fluxo da CLI

Antes da subida, a saída deverá identificar cada solicitação individual e seu
destino:

    Subida:
    - Ana Souza | chamada no andar 00 | destino 07
    - Carlos Lima | chamada no andar 00 | destino 12

Depois do evento de desembarque do último passageiro da subida, a CLI deverá
gerar e imprimir a nova lista antes de iniciar os eventos da descida:

    Descida:
    - Maria Alves | chamada no andar 05 | destino 00
    - João Silva | chamada no andar 11 | destino 00

Os eventos de entrada e saída continuarão listando nomes na ordem FIFO. O
resumo final continuará informando andar final, tempo simulado, total de
usuários atendidos e situação das filas. O tempo simulado não deverá incluir
qualquer atraso de apresentação da CLI.

## Regras de negócio a atualizar

Atualizar `docs/business_rules/regras_elevador.md` para registrar:

- que cada usuário possui uma solicitação individual e um andar de origem;
- que andares repetidos não são agrupados automaticamente;
- que a subida e a descida são fases sequenciais da mesma rodada;
- que a descida usa usuários novos e só é sorteada após o último desembarque
  da subida;
- que a descida mantém destino no térreo e usa origens superiores aleatórias;
- que a CLI deve apresentar a lista da descida antes de atendê-la.

## Testes e aceitação

Adicionar ou adaptar testes em `tests/unit/` para comprovar:

- geração de um a seis usuários em cada fase;
- destinos individuais aleatórios e válidos na subida;
- origens individuais aleatórias e válidas na descida;
- origem no térreo para todos os passageiros da subida;
- destino no térreo para todos os passageiros da descida;
- andares repetidos aceitos como solicitações independentes;
- nomes da descida diferentes dos passageiros da subida no cenário
  determinístico;
- ausência de chamada ao gerador de descida antes do desembarque final da
  subida;
- ordem observável entre o último desembarque, a lista da descida e o primeiro
  evento da descida;
- exibição do andar associado a cada usuário na CLI;
- capacidade máxima, filas FIFO e passageiros restantes atendidos;
- equivalência entre execução por `step()` e `run_until_idle()` em cada fase;
- término com elevador ocioso, cabine vazia e filas vazias;
- execução sem rede usando geradores fake e sementes determinísticas.

As validações esperadas após a conversão desta proposta em ExecPlan são:

    uv run --group dev ruff check .
    uv run --group dev ruff format --check .
    uv run --group dev mypy
    uv run --group dev pytest
    uv run python -m tools.validators.check_exec_plans

## Escopo e premissas

Incluem-se nesta proposta os modelos de domínio, o gerador de pessoas, o motor,
a CLI, as regras de negócio e os testes relacionados às duas fases. Não fazem
parte dela persistência, rede, interface gráfica ou alteração do algoritmo de
sorteio para eliminar duplicatas.

O prédio continua possuindo os andares `0` a `17`, a capacidade máxima continua
sendo seis pessoas e o térreo continua sendo o andar `0`. A proposta aprovada
deverá ser convertida em um ExecPlan em `docs/exec_plans/active/`, que definirá
as assinaturas finais e o plano de migração dos contratos atuais antes de
qualquer implementação de código.
