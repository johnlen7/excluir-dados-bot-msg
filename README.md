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
