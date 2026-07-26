# Regras de Negócio do Elevador

## 1. Contexto

- O sistema representa um elevador residencial.
- O prédio possui 18 andares, incluindo o térreo.
- O elevador atende somente esse prédio.

## 2. Chamadas externas

- Cada andar possui apenas um botão externo para chamar o elevador.
- Uma chamada realizada no térreo representa que o passageiro deseja subir.
- Uma chamada realizada em qualquer andar acima do térreo representa que o passageiro deseja descer.
- As chamadas devem permanecer registradas até que todas as pessoas daquele andar sejam atendidas.

## 3. Capacidade

- O elevador possui capacidade máxima de seis pessoas.
- O elevador não pode iniciar um deslocamento com mais de seis pessoas.
- Quando houver mais pessoas aguardando do que vagas disponíveis, apenas as pessoas que couberem poderão entrar.
- As pessoas que não conseguirem entrar devem permanecer em uma fila de espera no respectivo andar.
- A fila de espera deverá ser atendida posteriormente.

## 4. Embarque durante o trajeto

- O elevador pode buscar pessoas durante o trajeto de entrega dos passageiros que já estão dentro dele.
- O embarque durante o trajeto somente poderá ocorrer se houver capacidade disponível.
- A coleta de novos passageiros não deve impedir a entrega dos passageiros que já estão dentro do elevador.

## 5. Prioridades de atendimento

- Quando houver pessoas dentro do elevador, a prioridade será levá-las aos seus respectivos andares de destino.
- Durante esse trajeto, o elevador poderá atender chamadas externas que estejam no caminho, desde que possua capacidade disponível.
- Quando não houver pessoas dentro do elevador, a prioridade será atender os andares que possuem chamadas pendentes.
- Pessoas que ficaram em uma fila de espera continuam sendo consideradas uma chamada pendente daquele andar.

## 6. Estado de espera

- Quando não houver passageiros dentro do elevador e nenhuma chamada pendente, o elevador deverá permanecer parado.
- O elevador deverá aguardar no último andar em que realizou um atendimento.
- O elevador não deve retornar automaticamente ao térreo.

## 7. Tempo de deslocamento

- O elevador leva um segundo para percorrer a distância entre dois andares consecutivos.
- Portanto, um deslocamento de três andares leva três segundos.
- O tempo de abertura e fechamento das portas ainda não faz parte da regra de deslocamento.

## 8. Limites de operação

- O elevador somente pode se deslocar entre os andares existentes no prédio.
- Nenhum passageiro pode selecionar um andar inferior ao térreo ou superior ao último andar.
- O elevador deve parar exatamente nos andares solicitados pelos passageiros.
