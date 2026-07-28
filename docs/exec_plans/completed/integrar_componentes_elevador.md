# Integrar os componentes e endurecer as verificações do elevador

Este ExecPlan é um documento vivo. As seções `Progresso`, `Surpresas e
Descobertas`, `Registro de Decisões` e `Resultados e Retrospectiva` devem ser
mantidas atualizadas durante a execução do trabalho.

Este documento deve ser mantido de acordo com `PLANS.md`.

## Propósito / Visão geral

Depois desta alteração, a demonstração da linha de comando será comprovada
como uma composição real da geração de passageiros, dos modelos de domínio e
do motor do elevador. A verificação estática não esconderá mais imports
ausentes na CLI, e uma única execução do Pytest funcionará de modo estável
neste ambiente. A integração poderá ser observada executando duas rodadas pela
CLI e vendo chamadas, eventos cronológicos, filas vazias e resumos finais.

## Progresso

- [x] (2026-07-27 22:01Z) Auditados os módulos, os três ExecPlans independentes,
  a proposta temporária, as configurações e as validações existentes.
- [x] (2026-07-27 22:01Z) Criado este ExecPlan para o workflow de integração.
- [x] (2026-07-27 22:10Z) Endurecidos Mypy e Pytest e removida a supressão
  temporária da CLI.
- [x] (2026-07-27 22:10Z) Substituídos dados simulados permissivos por modelos
  e fakes tipados.
- [x] (2026-07-27 22:10Z) Adicionado e aprovado o cenário integrado de duas
  rodadas.
- [x] (2026-07-27 22:10Z) Atualizadas arquitetura, padrões de testes e
  instruções de ambiente.
- [x] (2026-07-27 22:10Z) Executadas todas as validações e a demonstração real.
- [x] (2026-07-27 22:12Z) Registrada a integração nos três ExecPlans
  anteriores e arquivado este plano.

## Surpresas e Descobertas

- Observação: a CLI desativa `import-not-found` e `import-untyped` para o
  arquivo inteiro.
  Evidência: a terceira linha de `src/elevator_vibe_code/cli.py` mantém uma
  diretiva Mypy criada quando geração, modelos e motor ainda não existiam.

- Observação: o ambiente virtual contém as ferramentas de desenvolvimento,
  mas não contém Faker, apesar de a dependência constar no projeto e no
  lockfile.
  Evidência: Mypy e Pytest falham no import de `faker`, e a demonstração
  termina com `ModuleNotFoundError`.

- Observação: o modo padrão de captura do Pytest falha antes da coleta, mas
  `--capture=sys` chega à coleta completa.
  Evidência: o primeiro comando termina com `FileNotFoundError` no arquivo
  temporário de captura; o segundo coleta 100 testes antes de encontrar o
  ambiente sem Faker.

- Observação: as implementações reais de CLI, modelos e motor já funcionam
  juntas quando recebem uma rodada determinística.
  Evidência: uma execução exploratória de duas rodadas terminou com código
  zero, eventos ordenados, filas vazias e elevador ocioso.

- Observação: o executável uv estava instalado, mas fora do `PATH` da sessão.
  Evidência: `/root/.local/bin/uv sync --locked --group dev` reconciliou o
  ambiente sem alterar o lockfile e instalou Faker 40.32.0, após o que Mypy,
  Pytest e a demonstração passaram.

## Registro de Decisões

- Decisão: manter as APIs públicas existentes e concentrar a integração em
  configuração, testes e documentação.
  Justificativa: os contratos congelados são compatíveis e a composição real
  já funciona; a lacuna está na comprovação e nas verificações.
  Data/Autor: 2026-07-27 / Codex.

- Decisão: usar Mypy estrito com rejeição explícita de tipos `Any` originados
  de imports não acompanhados.
  Justificativa: remover somente a diretiva da CLI não impediria outra
  dependência ausente de contaminar silenciosamente os tipos.
  Data/Autor: 2026-07-27 / Codex.

- Decisão: configurar `--capture=sys`, mostrar avisos e manter cobertura sem
  percentual bloqueante.
  Justificativa: o comando oficial precisa ser repetível, avisos não devem ser
  ocultados e não há meta de cobertura aprovada para esta integração.
  Data/Autor: 2026-07-27 / Codex.

- Decisão: não criar GitHub Actions nem um novo diretório de testes.
  Justificativa: a proteção solicitada é local e um teste de composição em
  `tests/unit/test_cli.py` é suficiente para o comportamento da aplicação.
  Data/Autor: 2026-07-27 / Codex.

## Resultados e Retrospectiva

O workflow integrou geração, modelos, motor e CLI sem alterar suas APIs
públicas. A CLI não contém mais supressão global de imports, o Mypy estrito
aprovou os 31 arquivos analisados e o comando único do Pytest aprovou 106
testes com 97% de cobertura. Ruff, formatação, lockfile e o validador de
ExecPlans também foram aprovados.

A demonstração real executou duas rodadas, imprimiu chamadas e eventos em
ordem, encerrou cada resumo com as duas filas zeradas e terminou com código
zero. A busca de supressões encontrou somente os dois `type: ignore` pontuais
preexistentes, necessários para construir valores deliberadamente
incompatíveis em testes sob Mypy estrito.

## Contexto e Orientação

O pacote `src/elevator_vibe_code/` contém quatro responsabilidades. `models.py`
define os valores imutáveis e seus invariantes; `generation.py` usa Faker para
criar uma rodada válida; `elevator.py` movimenta o elevador e produz eventos;
`cli.py` apresenta chamadas, eventos e resumos. O ponto de entrada
`__main__.py` chama `main()`.

As três partes foram implementadas em branches independentes. Por isso, os
testes da CLI usam objetos `Mock`, o motor registrou bloqueio por ausência dos
modelos e a CLI desativou erros de import do Mypy. Depois do merge, essas
convenções deixaram de ser necessárias. A proposta temporária
`docs/plan_proposals/organizacao_implementacao_elevador.md` congela os
contratos compartilhados, mas declara que não prevê integração e não deve ser
versionada.

O projeto exige Python 3.14.5, usa uv para reconciliar `pyproject.toml` e
`uv.lock`, e executa Ruff, Mypy, Pytest e o validador de ExecPlans como
verificações obrigatórias. O teste integrado não usa rede: ele injeta uma
instância semeada de Faker, usa modelos verdadeiros, conserva uma instância
real de `Elevator` e captura a saída em `StringIO`.

## Plano de Trabalho

Primeiro, atualizar `pyproject.toml` para executar o Pytest com captura por
`sys`, deixar avisos visíveis e aplicar o preset estrito do Mypy junto com
`disallow_any_unimported`. Remover a diretiva de supressão de
`src/elevator_vibe_code/cli.py` e corrigir a ordenação de imports deixada pelo
merge em `tests/unit/test_elevator.py`.

Depois, revisar `tests/unit/test_cli.py`. Eventos, passageiros, chamadas,
rodadas e snapshots serão instâncias dos modelos reais. A orquestração isolada
usará fakes nomeados com assinaturas explícitas, enquanto `patch` ficará
restrito às fábricas privadas. Um teste adicional usará
`FakerPassengerGenerator`, `Elevator` e `main()` reais durante duas rodadas e
verificará a saída e o estado ocioso final.

Em seguida, atualizar `ARCHITECTURE.md`, `docs/standards/testing.md` e
`README.md` para substituir o estado inicial obsoleto, documentar testes de
composição e sincronizar o ambiente pelo lockfile. Sincronizar o ambiente e
corrigir qualquer erro real revelado pelas verificações estritas.

Por fim, executar a suíte completa e a demonstração. Quando todas as
verificações passarem, mover este documento para
`docs/exec_plans/completed/integrar_componentes_elevador.md` e acrescentar uma
seção `Integração posterior` aos três planos independentes, sem modificar seu
relato histórico.

## Etapas Concretas

No diretório `/home/lvaz/projetos/elevator_ia_poc`, executar:

    uv sync --locked --group dev
    uv lock --check
    uv run --group dev ruff check .
    uv run --group dev ruff format --check .
    uv run --group dev mypy
    uv run --group dev pytest
    uv run python -m tools.validators.check_exec_plans
    uv run python -m elevator_vibe_code demo --rounds 2
    git diff --check

Se `uv` não estiver no `PATH`, disponibilizar o executável antes de sincronizar
o ambiente; não instalar dependências manualmente na `.venv`, pois isso
ocultaria divergência em relação ao lockfile.

## Validação e Aceitação

O novo teste de composição deve executar duas rodadas com geração semeada,
motor real e CLI real. Ele deve observar código de saída zero, dois cabeçalhos
de rodada, eventos de entrada e saída, dois resumos com filas zeradas e uma
instância do elevador ociosa, sem pessoas na cabine ou nas filas.

Mypy deve analisar `src`, `tools` e `tests` em modo estrito sem supressão
global de imports. Ruff, sua verificação de formato, o lockfile, a suíte
completa, o validador de ExecPlans e `git diff --check` devem terminar com
código zero. A demonstração deve imprimir duas rodadas completas e encerrar
normalmente.

Uma busca final deve confirmar que não existem `mypy: disable-error-code`,
`noqa`, `skip`, `xfail` ou `no cover` novos. Os dois `type: ignore` pontuais já
existentes somente podem permanecer se o modo estrito confirmar que são
necessários para construir entradas deliberadamente incompatíveis em testes.

## Idempotência e Recuperação

`uv sync --locked --group dev` pode ser repetido e reconciliará a `.venv` sem
alterar o lockfile. Testes, linters e validadores somente criam caches
ignorados. Se uma validação falhar, manter este plano em `active/`, registrar a
descoberta e corrigir a causa antes do arquivamento. Os arquivos temporários da
proposta e seu `Zone.Identifier` devem permanecer intocados.

## Artefatos e Notas

Os artefatos funcionais são a configuração mais estrita, a CLI sem supressão e
os testes tipados e integrados. Os artefatos documentais são a arquitetura,
o padrão de testes, o README, este ExecPlan e as notas posteriores nos três
ExecPlans independentes.

## Interfaces e Dependências

As assinaturas públicas de `RoundGenerator`, `FakerPassengerGenerator`,
`Elevator`, `format_event()` e `main()` permanecem inalteradas. Faker 40.32.0
continua sendo a única dependência de produção usada na geração; Mypy, Pytest,
pytest-cov, Ruff e os stubs de PyYAML permanecem no grupo `dev`. Não há nova
biblioteca nem integração externa.

Nota de alteração (2026-07-27): criado para substituir as convenções de
isolamento das três entregas independentes por um workflow local, tipado,
repetível e comprovado de integração.
