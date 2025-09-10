# Tutorial: Deploy do Telethon Cleaner no Railway (passo a passo)

Este tutorial mostra como publicar o repositório https://github.com/johnlen7/excluir-dados-bot-msg.git no Railway, configurar variáveis de ambiente e usar o painel para limpar mensagens de serviço em um grupo do Telegram.

Pré-requisitos
- Conta no Railway (https://railway.app) conectada ao seu GitHub.
- Acesso ao repositório: https://github.com/johnlen7/excluir-dados-bot-msg.git
- API ID / API HASH do Telegram (crie em https://my.telegram.org/apps).
- Opcional: uma String Session já gerada (evita login por código repetido).

Como criar API ID e API HASH (passo a passo)
1. Acesse https://my.telegram.org e clique em "Sign in".
2. Insira o seu número de telefone com DDI (ex: +5511999999999) — use a mesma conta que pretende usar no painel.
3. O site vai enviar um código para o seu aplicativo Telegram (no celular ou desktop). Abra o app Telegram, copie o código e cole no site para confirmar o login.
4. Depois de logado, clique em "API development tools" ou "Apps".
5. Preencha os campos solicitados (app title, short name e descrição curta) e clique para criar a aplicação.
6. O site exibirá seu "App api_id" (um número) e "App api_hash" (uma string). Anote esses valores — eles são obrigatórios para o painel.
7. Observação: o código enviado pelo my.telegram.org expira rapidamente; se o tempo estourar, solicite um novo código.

Resumo dos passos
1. Conectar o GitHub ao Railway e criar um novo projeto a partir do repo.
2. Configurar o root do projeto / comando de start e variáveis de ambiente.
3. Fazer deploy e abrir o painel público.
4. Login com API ID/API HASH + telefone ou colar uma String Session.
5. Testar com Dry-run = Sim e depois executar com Dry-run = Não.
6. Ao terminar, apagar/desligar o serviço por segurança.

Passo 1 — Criar projeto no Railway
1. Entre em https://railway.app e faça login.
2. Clique em "New Project" → "Deploy from GitHub".
3. Conecte sua conta GitHub (se ainda não estiver conectada) e autorize Railway a acessar seus repositórios.
4. Procure e selecione o repositório: johnlen7/excluir-dados-bot-msg.
5. Escolha o branch `main`.

Passo 2 — Configurar diretório raiz e comando de start
1. Se o projeto estiver em uma subpasta no repositório, configure o "Root Directory" (por exemplo `telethon_cleaner`). Caso os arquivos (`app.py`, `requirements.txt`, `Procfile`) estejam na raiz do repo, deixe em `/`.
2. Em "Build & Start", defina o comando de start como:

```text
python app.py
```

3. Verifique se existe um `requirements.txt` no repo. O Railway instalará dependências automaticamente.

Passo 3 — Variáveis de ambiente importantes
No painel do Railway, abra Settings → Variables e adicione:
- PORT = 8080 (opcional — Railway já seta um PORT, mas definir 8080 é seguro)
- PANEL_SECRET = <uma-string-secreta-qualquer> (opcional, usado pelo SessionMiddleware)
- SESSION_STRING = <sua_string_session_aqui> (opcional — se fornecida, o app tentará reconectar sem pedir código)

Observação: não coloque sua String Session em repositórios públicos. Se usar Railway, trate a variável como segredo e remova o serviço quando terminar.

Passo 4 — Deploy e logs
1. Salve as configurações e clique em Deploy.
2. Acompanhe os logs no Railway — se aparecer erro "python: can't open file '/app/telethon_cleaner/app.py'", verifique o Root Directory e o comando de start (use `python app.py` no diretório correto).

Passo 5 — Usar o painel
1. Abra a URL pública do serviço (Railway fornece um domínio temporário).
2. Tela de Login:
   - Opção A (sem session): preencha `API ID`, `API HASH` e `Telefone` (com DDI, ex +5511999999999) e clique "Enviar código". Insira o código recebido no app Telegram e (se houver) a senha 2FA.
   - Opção B (recomendada para deploy curto): cole a `String Session` no formulário de import e clique "Importar Session". Isso conecta diretamente sem código.
3. Após login, o painel mostrará a String Session (copie e guarde se precisar).

Passo 6 — Limpeza (usar com cuidado)
1. No formulário de Limpeza:
   - Chat: insira `-100...` (ID numérico), `@username`, `https://t.me/...` (link) ou nome do grupo.
   - Desde/Até: use os seletores de data/hora para escolher o intervalo.
   - Limite: número máximo de mensagens a escanear (padrão 5000).
   - Batch: quantas mensagens apagar por chamada (padrão 100).
   - Dry-run: escolha `Sim` para apenas simular e ver quantas mensagens *seriam* apagadas, `Não` para executar as exclusões reais.

Recomendações de uso
- Sempre rode primeiro com Dry-run = Sim. Verifique o campo "Matched" no resultado.
- Quando tiver certeza, rode com Dry-run = Não para apagar.
- Assim que terminar, remova o serviço do Railway (Delete Project) para não manter um painel público.

Resolução de problemas comuns
- Erro "Cannot find any entity corresponding to ...": verifique se a conta usada está no grupo; prefira usar o ID `-100...` ou link t.me/c/… para grupos privados.
- Erro "Session inválida": gere uma nova String Session localmente (veja abaixo) e importe.
- Erro de caminho "can't open file '/app/telethon_cleaner/app.py'": ajuste o Root Directory ou use `python telethon_cleaner/app.py` como start command quando o projeto estiver na pasta `telethon_cleaner`.

Gerar String Session localmente (opcional, mais seguro)
1. Crie um ambiente virtual e instale dependências:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Execute um script simples para obter a session (substitua API ID/API HASH):

```python
from telethon import TelegramClient
from telethon.sessions import StringSession

api_id = 123456
api_hash = 'seu_api_hash_aqui'

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print('String Session:', client.session.save())
```

3. O Telethon pedirá telefone/código e depois imprimirá a String Session. Cole essa string no Railway (variável `SESSION_STRING`) ou no campo de import do painel.

Segurança final
- Trate API HASH e String Session como segredos — quem tiver acesso pode controlar sua conta.
- Remova o serviço do Railway quando a tarefa terminar e delete as variáveis de ambiente.

Se quiser, eu posso gerar um texto pronto para colar no campo de Variables do Railway ou ajustar o Procfile/start command conforme a estrutura real do seu repo (me diga se os arquivos estão na raiz ou dentro de `telethon_cleaner`).
