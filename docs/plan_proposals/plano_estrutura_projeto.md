# Especificação inicial da estrutura do projeto

## Objetivo

Inicializar um projeto Python com uma estrutura pequena, previsível e adequada
ao uso do Codex. A estrutura deve separar instruções operacionais, arquitetura,
planejamento, documentação, código, testes e ferramentas auxiliares.

Substitua `<package>` pelo nome normalizado do pacote Python do projeto.

## Estrutura a criar

```text
projeto/
├── AGENTS.md
├── ARCHITECTURE.md
├── PLANS.md
├── README.md
├── pyproject.toml
├── .gitignore
│
├── docs/
│   ├── README.md
│   │
│   ├── standards/
│   │   ├── README.md
│   │   ├── code_style.md
│   │   ├── testing.md
│   │   ├── logging.md
│   │   └── documentation.md
│   │
│   ├── exec_plans/
│   │   ├── README.md
│   │   ├── active/
│   │   └── completed/
│   │
│   ├── business_rules/
│   │   └── README.md
│   │
│   └── garbage_collector/
│       ├── README.md
│       ├── schedule.md
│       ├── rules/
│       │   └── default_rules.yml
│       ├── inventory/
│       │   ├── inventory.yml
│       │   └── history/
│       ├── reports/
│       │   ├── README.md
│       │   └── .gitkeep
│       └── exceptions/
│           └── active_exceptions.yml
│
├── src/
│   └── <package>/
│       └── __init__.py
│
├── tests/
│   ├── unit/
│   └── garbage_collector/
│
└── tools/
    ├── __init__.py
    ├── README.md
    ├── validators/
    │   ├── __init__.py
    │   ├── README.md
    │   └── check_exec_plans.py
    └── garbage_collector/
        ├── __init__.py
        ├── __main__.py
        ├── README.md
        ├── scan.py
        ├── inventory.py
        └── report.py
```

## Instruções de criação

1. Crie os diretórios e arquivos exibidos na árvore.
2. Crie arquivos `README.md` curtos nos diretórios de documentação e de
   ferramentas. Cada um deve explicar o propósito do diretório e indicar seus
   arquivos principais.
3. Configure `src/<package>/` como o pacote principal da aplicação e mantenha
   `tools/` e seus subdiretórios Python como pacotes importáveis.
4. Não crie código de domínio, integrações externas ou regras de negócio
   fictícias durante a inicialização. Os módulos devem ser adicionados quando
   houver uma funcionalidade definida.
5. Mantenha os diretórios vazios que precisam ser versionados com `.gitkeep`
   ou um `README.md`, quando necessário.

## Responsabilidades

| Elemento | Responsabilidade |
|---|---|
| `AGENTS.md` | Instruções operacionais para Codex e demais colaboradores; deve ser curto e apontar para os documentos detalhados. |
| `ARCHITECTURE.md` | Mapa da arquitetura, responsabilidades dos módulos e dependências permitidas. |
| `PLANS.md` | Convenção para redigir e atualizar ExecPlans. |
| `README.md` | Visão geral do projeto, instalação, comandos principais e forma de uso. |
| `pyproject.toml` | Metadados do projeto, dependências e configurações de ferramentas Python. |
| `docs/standards/` | Padrões de código, testes, logging e documentação. |
| `docs/exec_plans/` | ExecPlans em andamento e concluídos. |
| `docs/business_rules/` | Regras do domínio descritas em linguagem de negócio. |
| `docs/garbage_collector/` | Configuração, inventário, exceções, agenda e relatórios da manutenção do repositório. |
| `src/<package>/` | Implementação da aplicação. |
| `tests/unit/` | Testes unitários do comportamento da aplicação. |
| `tests/garbage_collector/` | Testes das ferramentas do Garbage Collector. |
| `tools/validators/` | Validadores determinísticos de convenções e documentos. |
| `tools/garbage_collector/` | Varredura, inventário e geração de relatórios de manutenção. |

## Convenções operacionais

### Instruções e arquitetura

- `AGENTS.md` orienta o trabalho no repositório; não deve duplicar documentos
  de referência extensos.
- `ARCHITECTURE.md` define onde cada responsabilidade deve ficar e as fronteiras
  entre módulos.
- Regras verificáveis automaticamente devem ser configuradas nas ferramentas,
  não apenas descritas em Markdown.

### Documentação

- Registre regras de negócio em `docs/business_rules/` e implemente-as nos
  módulos apropriados de `src/<package>/`.
- Registre convenções em `docs/standards/`.
- Use `docs/exec_plans/active/` para planos em execução e mova-os para
  `docs/exec_plans/completed/` após a conclusão.

### Testes

- Use somente `tests/unit/` e `tests/garbage_collector/` na estrutura inicial.
- Cada mudança de comportamento deve incluir ou atualizar testes unitários
  pertinentes.

### Garbage Collector

- O Garbage Collector identifica candidatos à revisão, atualiza o inventário e
  gera relatórios.
- Regras de varredura ficam em `docs/garbage_collector/rules/`.
- Exceções ativas ficam em `docs/garbage_collector/exceptions/`.
- Relatórios ficam em `docs/garbage_collector/reports/`.

## Critérios de aceitação

- A árvore de diretórios corresponde à estrutura definida neste documento.
- O pacote `src/<package>/` e os pacotes em `tools/` possuem `__init__.py`.
- `uv run python -m tools.garbage_collector` é o ponto de entrada das ferramentas de
  manutenção.
- Os documentos de raiz e os `README.md` de diretórios especializados possuem
  uma descrição concisa de sua finalidade.
- A configuração de ferramentas está centralizada em `pyproject.toml`.

## Evolução da estrutura

Adicione novos diretórios somente quando houver uma responsabilidade clara e
uma necessidade recorrente. Antes de criar uma categoria adicional, registre:

- o problema que ela resolve;
- por que os locais existentes não são suficientes;
- quais arquivos ela conterá;
- como seu conteúdo será validado.
