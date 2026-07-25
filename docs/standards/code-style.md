# Padrões de estilo de código

Este documento define convenções para manter o código legível, previsível e
fácil de modificar. O formatador padrão da linguagem é a autoridade para
formatação automática.

## Funções

- Funções devem ter, como diretriz, entre 4 e 20 linhas.
- Funções maiores devem ser divididas por responsabilidade.
- Cada função deve realizar uma única operação conceitual.
- Prefira retornos antecipados a condicionais profundamente aninhadas.
- Mantenha no máximo dois níveis de indentação sempre que possível.

O limite de linhas é uma diretriz de design, não uma regra para criar funções
artificialmente fragmentadas. Clareza e coesão têm prioridade.

## Arquivos e módulos

- Arquivos devem permanecer abaixo de 500 linhas sempre que possível.
- Cada módulo deve possuir uma responsabilidade principal.
- Prefira módulos pequenos e focados a arquivos que concentram várias regras.
- Divida arquivos grandes por responsabilidade, não apenas por quantidade de
  linhas.

## Nomes

- Use nomes específicos, descritivos e consistentes com o domínio.
- Evite nomes genéricos como `data`, `handler` e `Manager`.
- Evite nomes que escondam responsabilidades diferentes sob uma mesma classe
  ou função.
- Prefira nomes que sejam facilmente localizáveis no repositório, idealmente
  com menos de cinco ocorrências relevantes em buscas.

## Tipos

- Funções públicas e métodos devem possuir anotações de tipo explícitas.
- Evite `Any`, `dict` genérico e funções sem tipo de retorno.
- Prefira tipos específicos e estruturas nomeadas para dados importantes.
- Não use tipos primitivos genéricos quando um tipo de domínio tornar o código
  mais claro.

## Duplicação e dependências

- Não duplique lógica.
- Extraia comportamentos compartilhados para uma função ou módulo coeso.
- Injete dependências por parâmetro ou construtor.
- Evite estado global e dependências implícitas em imports.
- Bibliotecas de terceiros devem ser encapsuladas por uma interface pertencente
  ao projeto quando puderem vazar detalhes para o domínio.

## Exceções

Mensagens de exceção devem informar:

- o valor que causou o problema;
- o formato ou valor esperado;
- a causa, quando ela for conhecida.

Exemplo:

```python
raise ValueError(
    f"Número de andar inválido: {floor}. "
    "Esperado um inteiro entre 1 e 18."
)
```

## Estrutura

- Siga as convenções do framework utilizado.
- Mantenha caminhos previsíveis, como `src/`, `tests/` e `tools/`.
- Coloque cada comportamento no módulo responsável por ele.
- Não crie módulos centrais que acumulem responsabilidades sem relação.

## Formatação automática

Use as ferramentas definidas no projeto:

```bash
ruff check .
ruff format .
```

Não altere manualmente o estilo formatado pelo Ruff para atender preferências
individuais.

