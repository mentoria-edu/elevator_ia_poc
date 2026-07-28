# Padrões de logging

Os logs devem ajudar na investigação de falhas e na observabilidade sem
substituir mensagens destinadas diretamente ao usuário.

## Regras

- Use logs estruturados em JSON para depuração e observabilidade.
- Inclua contexto suficiente para correlacionar a operação, sem registrar
  segredos ou dados sensíveis.
- Use níveis de log coerentes com a gravidade do evento.
- Registre exceções com contexto e preserve a causa original.
- Evite logs duplicados para o mesmo evento.

## Saída para usuários

- A saída de comandos CLI destinada ao usuário deve ser texto simples.
- Mensagens de CLI devem ser objetivas e indicar a ação necessária quando
  houver falha.
- Não misture JSON de observabilidade com a saída normal de uma CLI, salvo se
  isso for uma opção explícita do comando.

## Dados sensíveis

Nunca registre:

- senhas;
- tokens;
- chaves de API;
- credenciais;
- dados pessoais desnecessários.

