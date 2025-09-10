# Telethon Cleaner — tutorial passo a passo

Este repositório contém um painel Web minimalista (FastAPI + Telethon) para executar uma limpeza única de mensagens de serviço (entradas/saídas) em um grupo do Telegram usando uma conta de usuário (userbot).

Importante: o painel NÃO tem autenticação. Use apenas localmente ou em um serviço temporário, execute a tarefa e depois desligue ou remova o serviço.

Sumário rápido:
- Criar API ID/API HASH em https://my.telegram.org
- Iniciar o painel e abrir o link público
- Fazer login com seu telefone (receber código) e autorizar
- Rodar limpeza (use Dry-run primeiro)

Passo a passo detalhado
1) Criar API ID e API HASH
  - Acesse https://my.telegram.org e faça login com seu número de telefone (o mesmo que será usado no painel).
  - Clique em "API development tools" / "Apps".
  - Preencha um nome (p.ex. "telethon-cleaner"), short name e descrição mínima.
  - Após criar, anote o "App api_id" (um número) e o "App api_hash" (string). Guarde esses valores — serão usados no painel.

2) Preparar o serviço (Railway / Heroku / local)
  - Recomendação rápida (local): crie um venv com Python 3.9+ e instale dependências:

    ```powershell
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    python app.py
    ```

  - Em serviços como Railway/Heroku: aponte o deploy para a pasta do projeto e use o comando de start `python app.py`. Defina `PORT` se necessário.

3) Abrir o painel e fazer login
  - Abra o link do serviço (ou http://localhost:8080 se estiver rodando localmente).
  - Em "Login": preencha `API ID`, `API HASH` e `Telefone` (com DDI, ex: +5511999999999), clique em "Enviar código".
  - Você receberá um código no app Telegram. Insira o código no formulário. Se sua conta tiver 2FA, informe a senha.
  - Após autorizado, o painel mostrará a String Session. Copie e guarde se quiser reutilizar sem precisar do código novamente.

4) Preparar a limpeza
  - No campo "Chat" aceite:
    - ID numérico do grupo (ex: -1002630087787)
    - @username do grupo (ex: @meugrupo)
    - link t.me (ex: https://t.me/meugrupo ou https://t.me/c/123456789/1)
    - nome exato do grupo (ou parte do nome; preferência por username/ID para precisão)
  - Opcional: preencha "Desde" e "Até" em formato ISO8601 (ex: 2024-01-01T00:00:00Z) para filtrar período.
  - "Limite" = número máximo de mensagens a escanear (padrão 5000).
  - "Batch" = quantas mensagens apagar por chamada (padrão 100).

5) Dry-run: entender a opção
  - Dry-run = Sim (recomendado primeiro): o painel só escaneia e mostra quantas mensagens seriam apagadas (summary.matched). NÃO apaga nada. Use para checar que o alvo está correto.
  - Dry-run = Não: o painel executa a exclusão real em lotes. Use apenas quando tiver certeza do alvo e ter checado com dry-run.

6) Executar e finalizar
  - Rode primeiro com Dry-run = Sim. Verifique o resultado (Matched/Attempted/Deleted OK/Errors).
  - Se tudo correto, escolha Dry-run = Não e execute para apagar.
  - Assim que terminar, apague ou desligue o serviço para não manter acesso exposto.

Dicas e segurança
- A conta usada precisa estar no grupo e ter permissão para apagar mensagens. Se estiver usando como userbot, use sua própria conta e garanta que ela seja admin ou tenha permissão de apagar.
- Prefira usar o ID `-100...` ou o @username para evitar ambiguidades.
- Guarde a String Session com segurança se quiser reutilizar o login localmente; não a exponha publicamente.

Problemas comuns
- "Cannot find any entity corresponding to ...": verifique o formato do chat (use ID, username ou link t.me) e se a conta está no grupo.
- Erro de autorização: confirme que o código/2FA está correto.

Licença e limpeza
- Use apenas uma vez e remova o serviço/repósitorio quando terminar. Este painel foi feito para execução única e não é seguro mantê-lo público permanentemente.
# Telethon Cleaner (Painel Railway)

Painel simples (sem senha) para executar uma única vez a limpeza de mensagens de serviço antigas (entrada/saída) em um grupo, usando Telethon (userbot).

## Deploy na Railway
- Crie um novo serviço no mesmo repositório apontando a pasta `telethon_cleaner` como root (ou configure o comando de start).
- Variáveis opcionais: `PORT` (padrão 8080), `PANEL_SECRET` (para sessão do formulário).
- Start command: `python telethon_cleaner/app.py`

## Uso
1. Abra o painel público do serviço (sem senha) e preencha API ID, API HASH e telefone com DDI.
2. Clique em "Enviar código" e, em seguida, informe o código (e 2FA se necessário).
3. Ao logar, será exibida a String Session — copie caso deseje reutilizar.
4. Informe o chat (ID `-100...` ou `@username`), intervalos (opcionais), limite e batch.
5. Rode primeiro em Dry-run; depois execute a limpeza.
6. Ao terminar, desligue o serviço na Railway para segurança.

## Segurança
Este painel não tem autenticação — use SOMENTE para uma execução controlada e desligue após o uso. Não exponha em produção de forma permanente.
"# excluir-dados-bot-msg" 
