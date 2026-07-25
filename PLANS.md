# Planos de Execução do Codex (ExecPlans)

Este documento descreve os requisitos de um plano de execução ("ExecPlan"), um documento de projeto que um agente de programação pode seguir para entregar uma funcionalidade ou alteração de sistema em funcionamento. Considere que o leitor é totalmente iniciante neste repositório: ele possui apenas a árvore de trabalho atual e o único arquivo de ExecPlan fornecido. Não há memória de planos anteriores nem contexto externo.

## Como usar ExecPlans e PLANS.md

Ao escrever uma especificação executável (ExecPlan), siga o `PLANS.md` _à risca_. Se ele não estiver no seu contexto, atualize sua memória lendo o arquivo `PLANS.md` completo. Leia e releia o material-fonte com atenção para produzir uma especificação precisa. Ao criar uma especificação, comece pelo esqueleto e desenvolva-o à medida que realizar sua investigação.

Ao implementar uma especificação executável (ExecPlan), não peça ao usuário os “próximos passos”; siga diretamente para o próximo marco. Mantenha todas as seções atualizadas e adicione ou divida itens da lista em cada ponto de interrupção para registrar de modo afirmativo o progresso realizado e os próximos passos. Resolva ambiguidades de forma autônoma e faça commits com frequência.

Ao discutir uma especificação executável (ExecPlan), registre as decisões em um log dentro da especificação para referência futura; deve ser inequivocamente claro por que qualquer alteração na especificação foi feita. ExecPlans são documentos vivos, e deve ser sempre possível retomar o trabalho usando _apenas_ o ExecPlan, sem depender de outro material.

Ao investigar um projeto com requisitos desafiadores ou incertezas relevantes, use marcos para implementar provas de conceito, “implementações de brinquedo” e outros experimentos que permitam validar a viabilidade da proposta do usuário. Leia o código-fonte das bibliotecas, localizando-o ou obtendo-o quando necessário; pesquise em profundidade e inclua protótipos que orientem uma implementação completa.

## Requisitos

REQUISITOS INEGOCIÁVEIS:

* Todo ExecPlan deve ser completamente autossuficiente. Autossuficiente significa que, em seu estado atual, ele contém todo o conhecimento e todas as instruções necessários para que uma pessoa iniciante tenha sucesso.
* Todo ExecPlan é um documento vivo. As pessoas que contribuem devem revisá-lo conforme o progresso ocorre, descobertas são feitas e decisões de projeto são finalizadas. Cada revisão deve continuar completamente autossuficiente.
* Todo ExecPlan deve permitir que uma pessoa totalmente iniciante implemente a funcionalidade de ponta a ponta, sem conhecimento prévio deste repositório.
* Todo ExecPlan deve produzir um comportamento comprovadamente funcional, não apenas alterações de código que “cumpram uma definição”.
* Todo termo técnico deve ser definido em linguagem simples; caso contrário, não o utilize.

Propósito e intenção vêm primeiro. Comece explicando, em algumas frases, por que o trabalho importa da perspectiva de quem usa o sistema: o que essa pessoa poderá fazer depois da alteração que não podia fazer antes e como poderá verificar que funciona. Em seguida, oriente o leitor pelos passos exatos para alcançar esse resultado, incluindo o que editar, o que executar e o que deve ser observado.

O agente que executará o plano consegue listar arquivos, lê-los, pesquisá-los, executar o projeto e rodar testes. Ele não conhece nenhum contexto anterior e não pode deduzir o que você quis dizer a partir de marcos prévios. Repita toda premissa da qual você depender. Não aponte para blogs ou documentos externos; quando um conhecimento for necessário, incorpore-o ao plano com suas próprias palavras. Se um ExecPlan se basear em um ExecPlan anterior e esse arquivo estiver versionado no repositório, incorpore-o por referência. Se não estiver, inclua todo o contexto relevante daquele plano.

## Formatação

O formato e o envoltório são simples e rígidos. Cada ExecPlan deve consistir em um único bloco de código delimitado e rotulado como `md`, começando e terminando com três crases. Não aninhe blocos de código adicionais delimitados por três crases. Quando precisar mostrar comandos, transcrições, diffs ou código, apresente-os como blocos indentados dentro desse único bloco. Use indentação para dar clareza, em vez de blocos de código internos, evitando encerrar o bloco de código do ExecPlan prematuramente. Use duas linhas em branco após cada título; use `#`, `##` e assim por diante; e empregue a sintaxe correta de listas ordenadas e não ordenadas.

Ao escrever um ExecPlan em um arquivo Markdown (`.md`) cujo conteúdo seja _somente_ aquele único ExecPlan, omita as três crases externas.

Escreva em prosa simples. Prefira frases a listas. Evite checklists, tabelas e enumerações longas, exceto quando a brevidade prejudicar a clareza. Checklists são permitidos apenas na seção `Progresso`, onde são obrigatórios. As seções narrativas devem priorizar a prosa.

## Diretrizes

Autossuficiência e linguagem simples são fundamentais. Se introduzir uma expressão que não faça parte da linguagem cotidiana (como “daemon”, “middleware”, “gateway RPC” ou “grafo de filtros”), defina-a imediatamente e explique novamente como ela se manifesta neste repositório — por exemplo, nomeando os arquivos ou comandos nos quais aparece. Não diga “como definido anteriormente” ou “de acordo com o documento de arquitetura”. Inclua no próprio plano a explicação necessária, mesmo que isso gere repetição.

Evite falhas comuns. Não dependa de jargões indefinidos. Não descreva “a letra de uma funcionalidade” de forma tão restrita que o código compile, mas não faça nada útil. Não delegue decisões essenciais ao leitor. Quando houver ambiguidade, resolva-a no próprio plano e explique por que escolheu aquele caminho. Priorize explicações detalhadas sobre efeitos visíveis para quem usa o sistema e evite especificar em excesso detalhes incidentais da implementação.

Ancore o plano em resultados observáveis. Declare o que a pessoa usuária poderá fazer depois da implementação, os comandos a executar e as saídas esperadas. A aceitação deve ser formulada como um comportamento que alguém pode verificar — por exemplo: “depois de iniciar o servidor, acessar `http://localhost:8080/health` retorna HTTP 200 com o corpo `OK`” — e não como atributos internos, como “foi adicionada uma struct `HealthCheck`”. Se uma alteração for interna, explique como seu impacto ainda pode ser demonstrado, por exemplo, executando testes que falham antes e passam depois da mudança, ou mostrando um cenário que utiliza o novo comportamento.

Especifique explicitamente o contexto do repositório. Nomeie arquivos com caminhos completos relativos à raiz do repositório, nomeie funções e módulos com precisão e descreva onde novos arquivos devem ser criados. Ao alterar várias áreas, inclua um parágrafo breve de orientação explicando como elas se relacionam, para que uma pessoa iniciante possa navegar com segurança. Ao executar comandos, mostre o diretório de trabalho e a linha de comando exata. Quando os resultados dependerem do ambiente, declare as premissas e apresente alternativas razoáveis quando possível.

Seja idempotente e seguro. Escreva os passos de modo que possam ser executados diversas vezes sem causar danos ou divergências. Se um passo puder falhar pela metade, inclua como tentar novamente ou adaptar a execução. Caso seja necessária uma migração ou operação destrutiva, detalhe backups ou alternativas seguras. Prefira alterações aditivas e testáveis, que possam ser validadas durante o processo.

A validação não é opcional. Inclua instruções para executar testes, iniciar o sistema quando aplicável e observá-lo realizando algo útil. Descreva testes abrangentes para novas funcionalidades ou capacidades. Inclua saídas e mensagens de erro esperadas, para que uma pessoa iniciante possa distinguir sucesso de falha. Quando possível, mostre como provar que a mudança é eficaz além da compilação, por exemplo, por meio de um pequeno cenário de ponta a ponta, uma invocação de linha de comando ou uma transcrição de requisição e resposta HTTP. Declare os comandos de teste exatos adequados à ferramenta do projeto e como interpretar seus resultados.

Registre evidências. Quando os passos produzirem saída de terminal, diffs curtos ou logs, inclua exemplos concisos dentro do único bloco delimitado. Mantenha-os focados no que comprova o sucesso. Se for necessário incluir um patch, prefira diffs por arquivo ou pequenos trechos que o leitor possa recriar seguindo as instruções, em vez de grandes blocos de código.

## Marcos

Marcos são uma narrativa, não burocracia. Se dividir o trabalho em marcos, apresente cada um com um parágrafo breve que descreva o escopo, o que existirá ao final que não existia antes, os comandos a executar e a aceitação esperada. Mantenha a leitura como uma história: objetivo, trabalho, resultado e comprovação. Progresso e marcos são distintos: marcos contam a história; progresso acompanha o trabalho granular. Ambos devem existir. Nunca abrevie um marco apenas para ser breve e não omita detalhes que possam ser cruciais para uma implementação futura.

Cada marco deve ser verificável de forma independente e implementar incrementalmente o objetivo geral do plano de execução.

## Planos vivos e decisões de projeto

* ExecPlans são documentos vivos. Ao tomar decisões importantes de projeto, atualize o plano para registrar tanto a decisão quanto o raciocínio por trás dela. Registre todas as decisões na seção `Registro de Decisões`.
* ExecPlans devem conter e manter as seções `Progresso`, `Surpresas e Descobertas`, `Registro de Decisões` e `Resultados e Retrospectiva`. Essas seções são obrigatórias.
* Quando descobrir comportamento do otimizador, compromissos de desempenho, bugs inesperados ou semânticas de reversão/desfazer que moldaram sua abordagem, registre essas observações na seção `Surpresas e Descobertas`, com pequenas evidências — idealmente, saída de testes.
* Se mudar de direção no meio da implementação, documente o motivo no `Registro de Decisões` e reflita as implicações em `Progresso`. Os planos são guias tanto para a próxima pessoa a contribuir quanto listas de verificação para você.
* Ao concluir uma tarefa importante ou o plano completo, escreva uma entrada em `Resultados e Retrospectiva` resumindo o que foi alcançado, o que resta e os aprendizados.

# Marcos de prototipagem e implementações paralelas

É aceitável — e com frequência recomendado — incluir marcos explícitos de prototipagem quando eles reduzem o risco de uma alteração maior. Exemplos: adicionar um operador de baixo nível a uma dependência para validar a viabilidade, ou explorar duas ordens de composição enquanto mede os efeitos no otimizador. Mantenha os protótipos aditivos e testáveis. Identifique claramente o escopo como “prototipagem”; descreva como executar e observar os resultados; e declare os critérios para promover ou descartar o protótipo.

Prefira alterações aditivas de código seguidas de remoções que mantenham os testes passando. Implementações paralelas — por exemplo, manter um adaptador ao lado de um caminho antigo durante uma migração — são adequadas quando reduzem riscos ou permitem que os testes continuem passando durante uma alteração grande. Descreva como validar ambos os caminhos e como retirar um deles com segurança por meio de testes. Ao trabalhar com várias bibliotecas novas ou áreas de funcionalidade, considere criar experimentos que avaliem a viabilidade de cada capacidade _separadamente_, comprovando que a biblioteca externa se comporta como esperado e implementa, de forma isolada, as funcionalidades necessárias.

## Esqueleto de um bom ExecPlan

    # <Descrição curta e orientada à ação>

    Este ExecPlan é um documento vivo. As seções `Progresso`, `Surpresas e Descobertas`, `Registro de Decisões` e `Resultados e Retrospectiva` devem ser mantidas atualizadas durante a execução do trabalho.

    Se o arquivo PLANS.md estiver versionado no repositório, indique aqui seu caminho a partir da raiz do repositório e informe que este documento deve ser mantido de acordo com PLANS.md.

    ## Propósito / Visão geral

    Explique, em algumas frases, o que alguém ganha após esta alteração e como pode verificar que ela funciona. Declare o comportamento visível para a pessoa usuária que será habilitado.

    ## Progresso

    Use uma lista com caixas de seleção para resumir as etapas granulares. Cada ponto de interrupção deve ser documentado aqui, mesmo que seja necessário dividir uma tarefa parcialmente concluída em duas partes (“concluído” e “restante”). Esta seção deve sempre refletir o estado real e atual do trabalho.

    - [x] (2025-10-01 13:00Z) Exemplo de etapa concluída.
    - [ ] Exemplo de etapa não concluída.
    - [ ] Exemplo de etapa parcialmente concluída (concluído: X; restante: Y).

    Use timestamps para medir a taxa de progresso.

    ## Surpresas e Descobertas

    Documente comportamentos inesperados, bugs, otimizações ou percepções obtidas durante a implementação. Forneça evidências concisas.

    - Observação: …
      Evidência: …

    ## Registro de Decisões

    Registre cada decisão tomada durante a execução do plano no formato:

    - Decisão: …
      Justificativa: …
      Data/Autor: …

    ## Resultados e Retrospectiva

    Resuma os resultados, as lacunas e os aprendizados em marcos importantes ou ao término. Compare o resultado com o propósito original.

    ## Contexto e Orientação

    Descreva o estado atual relevante para esta tarefa como se o leitor não soubesse nada. Nomeie os arquivos e módulos principais usando seus caminhos completos. Defina qualquer termo não óbvio que você utilizar. Não faça referência a planos anteriores.

    ## Plano de Trabalho

    Descreva, em prosa, a sequência de edições e adições. Para cada edição, nomeie o arquivo e o local — função ou módulo — e o que deve ser inserido ou alterado. Mantenha a descrição concreta e mínima.

    ## Etapas Concretas

    Declare os comandos exatos a executar e onde executá-los, incluindo o diretório de trabalho. Quando um comando gerar saída, mostre uma pequena transcrição esperada para comparação. Esta seção deve ser atualizada durante a execução do trabalho.

    ## Validação e Aceitação

    Descreva como iniciar ou exercitar o sistema e o que deve ser observado. Formule a aceitação como comportamento, com entradas e saídas específicas. Quando houver testes, escreva: “execute <comando de teste do projeto> e espere <N> testes aprovados; o novo teste <nome> falha antes da alteração e passa depois dela”.

    ## Idempotência e Recuperação

    Se as etapas puderem ser repetidas com segurança, declare isso. Se alguma etapa for arriscada, forneça uma forma segura de tentar novamente ou reverter. Mantenha o ambiente limpo após a conclusão.

    ## Artefatos e Notas

    Inclua as transcrições, diffs ou trechos mais importantes. Mantenha-os concisos e focados no que comprova o sucesso.

    ## Interfaces e Dependências

    Seja prescritivo. Nomeie as bibliotecas, os módulos e os serviços a utilizar e explique por quê. Especifique os tipos, traits/interfaces e assinaturas de função que devem existir ao fim do marco. Prefira nomes e caminhos estáveis, como `crate::module::function` ou `package.submodule.Interface`. Exemplo:

    Em `crates/foo/planner.rs`, defina:

        pub trait Planner {
            fn plan(&self, observed: &Observed) -> Vec<Action>;
        }

Se seguir as orientações acima, um único agente sem estado — ou uma pessoa iniciante — poderá ler seu ExecPlan do início ao fim e produzir um resultado funcional e observável. Esse é o padrão: AUTOSSUFICIENTE, GUIADO PARA INICIANTES E FOCADO NO RESULTADO.

Ao revisar um plano, garanta que as alterações estejam refletidas de forma abrangente em todas as seções, incluindo as seções do documento vivo. Ao final do plano, escreva uma nota descrevendo a alteração e o motivo dela. ExecPlans devem descrever não apenas o que será feito, mas também o porquê de quase tudo.
