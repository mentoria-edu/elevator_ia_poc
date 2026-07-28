# Adicionar delay configurável entre steps da demonstração

Este ExecPlan é um documento vivo. As seções `Progresso`, `Surpresas e
Descobertas`, `Registro de Decisões` e `Resultados e Retrospectiva` devem ser
mantidas atualizadas durante a execução do trabalho. Este documento deve ser
mantido de acordo com `PLANS.md`, localizado na raiz do repositório.

## Propósito / Visão geral

Atualmente, a demonstração executa toda a rodada antes de imprimir os eventos,
fazendo a saída aparecer rápido demais para acompanhamento humano. Depois desta
alteração, a pessoa poderá executar a demonstração com
`uv run python -m elevator_vibe_code demo --rounds 2 --step-delay 2` e observar
uma pausa configurável entre os passos do elevador. O tempo exibido nos eventos
continuará sendo o tempo simulado pelo motor, sem incorporar a espera real da
apresentação.

## Progresso

- [x] (2026-07-27 22:46Z) Investigados arquitetura, implementação da CLI,
  testes, documentação e padrões do repositório.
- [x] (2026-07-27 22:46Z) Definida com a pessoa usuária a interface
  `--step-delay`, com padrão de 2 segundos e valores decimais não negativos.
- [x] (2026-07-27 22:50Z) Implementadas a validação do argumento e a execução
  passo a passo.
- [x] (2026-07-27 22:53Z) Adaptados os testes unitários e de composição.
- [x] (2026-07-27 22:58Z) Atualizado o exemplo de uso; Ruff, Ruff Format, Mypy,
  Pytest com 115 testes e o validador de ExecPlans passaram.
- [x] (2026-07-27 22:58Z) Executada com sucesso a demonstração real de duas
  rodadas com `--step-delay 2`.
- [x] (2026-07-27 22:58Z) Registrados os resultados e concluído este ExecPlan.

## Surpresas e Descobertas

- Observação: a CLI usa `Elevator.run_until_idle()`, que devolve todos os
  eventos somente após concluir a rodada.
  Evidência: `src/elevator_vibe_code/cli.py` itera diretamente sobre o retorno
  completo desse método, embora `Elevator.step()` já exponha lotes por passo.

- Observação: a sessão não possuía `uv` no `PATH`, embora o executável já
  estivesse instalado no ambiente.
  Evidência: os comandos iniciais retornaram código 127; as mesmas validações
  passaram usando `/home/lvaz/.local/bin/uv`.

## Registro de Decisões

- Decisão: aceitar exclusivamente `--step-delay`, sem alias com sublinhado.
  Justificativa: esta é a interface final solicitada pela pessoa usuária e
  segue a convenção usual de opções longas de linha de comando.
  Data/Autor: 2026-07-27 / Codex e pessoa usuária.

- Decisão: aceitar somente números decimais finitos maiores ou iguais a zero,
  usar 2 segundos por padrão e tratar zero como espera desativada.
  Justificativa: valores fracionários permitem ajustar a demonstração; rejeitar
  infinitos e `nan` evita erros tardios em `time.sleep`.
  Data/Autor: 2026-07-27 / Codex e pessoa usuária.

- Decisão: aguardar entre chamadas de `Elevator.step()`, mantendo juntos todos
  os eventos retornados por uma mesma chamada.
  Justificativa: eventos de atendimento no mesmo andar são simultâneos no
  modelo e não devem receber atrasos artificiais entre suas linhas.
  Data/Autor: 2026-07-27 / Codex e pessoa usuária.

## Resultados e Retrospectiva

A CLI passou a avançar o motor com `step()`, imprimir cada lote antes da pausa
e aguardar 2 segundos por padrão somente quando existe outro passo. A opção
`--step-delay` aceita decimais finitos não negativos, zero desativa a espera e
o nome com sublinhado é rejeitado. O README registra o comando atualizado.

Ruff, Ruff Format, Mypy, o validador de ExecPlans e os 115 testes passaram. A
demonstração real de duas rodadas com delay de 2 segundos terminou com código
zero, resumos completos e filas vazias, sem alterar o tempo simulado do motor.

## Contexto e Orientação

`src/elevator_vibe_code/elevator.py` contém o motor determinístico.
`Elevator.step()` executa um atendimento local ou avança no máximo um andar e
retorna os eventos desse passo. `src/elevator_vibe_code/cli.py` contém o parser,
a orquestração e a apresentação da demonstração. Hoje seu protocolo privado
declara `run_until_idle()` e `main()` imprime o lote completo retornado pelo
motor. `tests/unit/test_cli.py` usa um elevador fake para observar essa
orquestração e contém um teste de composição com as implementações reais.
`README.md` contém o comando público usado para demonstrar a integração.

O delay pertence somente à apresentação. Portanto, nenhuma regra ou assinatura
do motor será alterada. Uma função de espera recebida por parâmetro nomeado em
`main()` permitirá que os testes observem as pausas sem esperar em tempo real.

## Plano de Trabalho

Em `src/elevator_vibe_code/cli.py`, adicionar um conversor de argumento que
aceite `float` finito não negativo e configurar `--step-delay` com padrão
`2.0`. Substituir no protocolo privado `run_until_idle()` por `step()`. Extrair
uma rotina pequena que chame `step()`, imprima o lote retornado, consulte o
snapshot e, se o motor ainda estiver ativo, libere o buffer e invoque a função
de espera. A rotina deve retornar o snapshot terminal para o resumo, evitando
espera após o último passo. `main()` receberá uma função compatível com
`Callable[[float], None]`, usando `time.sleep` por padrão, e não a chamará
quando o delay for zero.

Em `tests/unit/test_cli.py`, adaptar `FakeElevator` para entregar um lote por
`step()` e snapshots terminais ou intermediários. Injetar funções de espera
fakes para manter os testes rápidos. Adicionar cenários que comprovem o padrão,
decimais, zero, rejeição de valores inválidos e do nome `--step_delay`, ordem
da impressão em relação à pausa e ausência de pausa após o passo terminal.
Preservar os testes de múltiplas rodadas e de composição real.

Em `README.md`, atualizar o comando da demonstração para incluir
`--step-delay 2` e explicar brevemente o padrão e como desativar a pausa.

## Etapas Concretas

No diretório `/home/lvaz/projetos/elevator_ia_poc`, editar os arquivos citados
e executar:

    uv run --group dev ruff check .
    uv run --group dev ruff format --check .
    uv run --group dev mypy
    uv run --group dev pytest
    uv run python -m tools.validators.check_exec_plans
    uv run python -m elevator_vibe_code demo --rounds 2 --step-delay 0

O último comando usa zero durante a validação automatizada para concluir
imediatamente. A interface com delay real será comprovada pelos testes da
função de espera injetada; uma execução manual pode substituir zero por dois.

## Validação e Aceitação

Os testes devem comprovar que dois passos causam exatamente uma espera, que o
lote do primeiro passo já foi escrito quando a espera acontece e que o passo
terminal é seguido imediatamente pelo resumo. Sem `--step-delay`, a função de
espera deve receber `2.0`; com `--step-delay 0.5`, deve receber `0.5`; com zero,
não deve ser chamada. Valores negativos, `nan`, infinitos, texto e a opção
incorreta `--step_delay` devem causar `SystemExit` com código 2.

A suíte de composição deve continuar terminando duas rodadas com elevador
ocioso, cabine e filas vazias. Os resumos devem preservar o tempo simulado,
independentemente do delay configurado. Todos os comandos de qualidade devem
terminar com código zero.

## Idempotência e Recuperação

As edições e validações podem ser repetidas sem efeitos externos. Nenhuma
migração, rede ou exclusão de dados é necessária. O arquivo não rastreado
`docs/plan_proposals/organizacao_implementacao_elevador.md` pertence à pessoa
usuária e não será alterado.

## Artefatos e Notas

A demonstração esperada será iniciada por:

    uv run python -m elevator_vibe_code demo --rounds 2 --step-delay 2

Cada lote de eventos de um passo aparecerá junto, seguido por aproximadamente
dois segundos de espera somente quando houver outro passo na mesma rodada.

## Interfaces e Dependências

Não serão adicionadas dependências externas. `math.isfinite` validará o número,
e `time.sleep` implementará a espera padrão. Ao final, a interface será:

    elevator_vibe_code demo [--rounds N] [--step-delay SEGUNDOS]

`SEGUNDOS` será um `float` finito maior ou igual a zero, com padrão `2.0`.
`main()` manterá os parâmetros existentes e acrescentará um parâmetro nomeado
`sleeper: Callable[[float], None]`, cujo padrão será `time.sleep`.
