# Regras de Negócio do Elevador

## 1. Contexto

- O sistema representa um elevador residencial.
- O prédio possui 18 andares, incluindo o térreo.
- O elevador atende somente esse prédio.

## 2. Solicitações individuais

- Cada usuário possui uma solicitação individual com origem, destino e
  direção.
- Uma solicitação com origem no térreo representa que o usuário deseja subir.
- Uma solicitação com origem acima do térreo representa que o usuário deseja
  descer até o térreo.
- Duas pessoas podem possuir o mesmo andar de origem ou destino, mas suas
  solicitações continuam independentes e não são agrupadas automaticamente.
- Cada solicitação permanece registrada até que sua pessoa seja atendida.

## 3. Fases da rodada

- Cada rodada possui uma fase de subida seguida por uma fase de descida.
- A subida possui entre um e seis usuários, todos com origem no térreo e
  destinos independentes entre os andares 1 e 17.
- A descida usa entre um e seis usuários novos, independentes dos passageiros
  da subida.
- Os usuários da descida possuem origens independentes entre os andares 1 e 17
  e destino no térreo.
- A descida somente pode ser sorteada depois do último desembarque da subida.
- A CLI deve apresentar cada solicitação da descida antes do seu primeiro
  evento de atendimento.
- A aleatoriedade de usuários e andares não altera a ordem dos eventos nem as
  regras determinísticas de direção.

## 4. Capacidade

- O elevador possui capacidade máxima de seis pessoas.
- O elevador não pode iniciar um deslocamento com mais de seis pessoas.
- Quando houver mais pessoas aguardando do que vagas disponíveis, apenas as
  pessoas que couberem poderão entrar.
- As pessoas que não entrarem devem permanecer na fila de espera de seu andar.
- A fila de espera deverá ser atendida posteriormente.

## 5. Embarque durante o trajeto

- O elevador pode buscar pessoas durante o trajeto de entrega dos passageiros
  que já estão dentro dele.
- O embarque durante o trajeto somente pode ocorrer se houver capacidade e se
  a direção da solicitação for compatível com o deslocamento.
- A coleta de novos passageiros não deve impedir a entrega dos passageiros que
  já estão dentro do elevador.

## 6. Prioridades de atendimento

- Quando houver pessoas dentro do elevador, a prioridade será levá-las aos
  seus respectivos andares de destino.
- Durante esse trajeto, o elevador poderá atender solicitações que estejam no
  caminho, desde que possua capacidade disponível.
- Quando não houver pessoas dentro do elevador, a prioridade será a origem
  pendente mais próxima.
- Distâncias iguais serão desempatadas pela ordem FIFO das solicitações.
- Pessoas que permanecerem em uma fila continuam sendo solicitações pendentes
  daquele andar.

## 7. Estado de espera

- Quando não houver passageiros dentro do elevador e nenhuma solicitação
  pendente, o elevador deverá permanecer parado.
- O elevador deverá aguardar no último andar em que realizou um atendimento.
- O elevador não deve retornar automaticamente ao térreo entre as fases ou
  entre rodadas.

## 8. Tempo de deslocamento

- O elevador leva um segundo para percorrer a distância entre dois andares
  consecutivos.
- Portanto, um deslocamento de três andares leva três segundos.
- A abertura da porta leva um segundo.
- O fechamento da porta leva um segundo.
- O embarque e o desembarque não acrescentam tempo ao atendimento.
- A espera configurável da CLI não faz parte do tempo simulado.

## 9. Limites de operação

- O elevador somente pode se deslocar entre os andares existentes no prédio.
- Nenhum passageiro pode selecionar um andar inferior ao térreo ou superior ao
  último andar.
- O elevador deve parar exatamente nos andares solicitados pelos passageiros.
