# Arquitetura

## Módulos

- `src/elevator_vibe_code/models.py`: valores imutáveis e invariantes do
  domínio.
- `src/elevator_vibe_code/generation.py`: criação de rodadas válidas por meio
  do contrato `RoundGenerator`.
- `src/elevator_vibe_code/elevator.py`: motor determinístico de atendimento e
  produção de eventos.
- `src/elevator_vibe_code/cli.py`: orquestração e apresentação da demonstração
  em linha de comando.
- `tests/unit/`: testes do comportamento da aplicação.
- `tools/`: ferramentas determinísticas de manutenção do repositório.
- `docs/`: documentação operacional, padrões e regras de negócio.
- `docs/plan_proposals/`: propostas iniciais que registram a intenção de projetos
  ou funcionalidades antes de sua execução.

## Convenção de Nomes

Use `snake_case` para diretórios e arquivos auxiliares do repositório,
incluindo `.py`, `.md` de apoio, `.yml` e equivalentes. As únicas exceções em
`UPPERCASE` são `AGENTS.md`, `ARCHITECTURE.md`, `PLANS.md` e todos os arquivos
`README.md`. Ao renomear qualquer caminho, atualize na mesma alteração todas as
referências textuais e operacionais para manter o repositório coerente.

## Dependências Permitidas

O código de domínio não deve importar módulos de `tools/`. Ferramentas podem
ler documentação e metadados do repositório, mas não devem conter regras de
negócio. Integrações externas devem ser encapsuladas no pacote da aplicação
quando uma funcionalidade concreta as exigir.

## Composição da Aplicação

A CLI solicita uma rodada ao gerador, entrega os modelos validados ao motor e
formata os eventos e snapshots devolvidos pelo atendimento. Os módulos se
comunicam somente pelos contratos públicos de `models.py` e
`generation.py`; regras operacionais permanecem no motor e regras de
apresentação permanecem na CLI.

Uma alteração que atravesse essas responsabilidades deve manter testes
isolados de cada módulo e ao menos um teste determinístico de composição. O
teste de composição usa as implementações reais, não acessa rede ou serviços
externos e comprova que os contratos continuam compatíveis.
