import os
import asyncio
import re
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from jinja2 import Environment, FileSystemLoader, select_autoescape

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl import types as tl
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from telethon.utils import resolve_id


app = FastAPI(title="Telethon Cleaner")
app.add_middleware(SessionMiddleware, secret_key=os.getenv("PANEL_SECRET", "temp-secret"))

BASE_DIR = os.path.dirname(__file__)
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"]) ,
)


class State:
    client: Optional[TelegramClient] = None
    api_id: Optional[int] = None
    api_hash: Optional[str] = None
    phone: Optional[str] = None
    session_str: Optional[str] = None
    code_sent: bool = False
    authorized: bool = False
    last_error: Optional[str] = None


STATE = State()
# Se houver uma session serializada em env, carregue para reutilizar entre reinícios
env_session = os.getenv("SESSION_STRING")
if env_session:
    STATE.session_str = env_session


def render(name: str, **ctx) -> HTMLResponse:
    tpl = env.get_template(name)
    return HTMLResponse(tpl.render(**ctx))


def parse_iso(dt: str) -> Optional[datetime]:
    if not dt:
        return None
    try:
        if dt.endswith("Z"):
            dt = dt[:-1] + "+00:00"
        return datetime.fromisoformat(dt)
    except Exception:
        return None


def is_service_join_leave(msg) -> bool:
    if isinstance(msg, tl.MessageService):
        act = msg.action
        return isinstance(act, (
            tl.MessageActionChatAddUser,
            tl.MessageActionChatJoinedByLink,
            tl.MessageActionChatDeleteUser,
        ))
    return False


async def resolve_chat_entity(client: TelegramClient, chat: str):
    """Resolve diversas formas de entrada de chat para uma entity do Telethon.

    Aceita:
    - @username
    - Links t.me/@user, t.me/user, t.me/c/<id>/...
    - ID numérico (ex.: -1001234567890)
    - Nome/título do grupo (busca entre diálogos)
    """
    s = (chat or "").strip()
    if not s:
        raise ValueError("Chat vazio.")

    lower = s.lower()
    # Links t.me
    if "t.me/" in lower:
        try:
            path = s.split("t.me/", 1)[1].strip("/")
            if path.startswith("c/"):
                digits = ''.join(ch for ch in path[2:] if ch.isdigit())
                if not digits:
                    raise ValueError("Link t.me/c inválido")
                s = f"-100{digits}"
            else:
                username = path.split('/')[0]
                return await client.get_entity(username)
        except Exception:
            pass

    # @username
    if s.startswith("@"):
        return await client.get_entity(s[1:])

    # Numérico (inclui -100...)
    if s.lstrip("-").isdigit():
        try:
            pid = int(s)
            peer_cls, peer_id = resolve_id(pid)
            peer_obj = peer_cls(peer_id)
            return await client.get_entity(peer_obj)
        except Exception:
            # fallback (user IDs positivos podem resolver direto)
            return await client.get_entity(int(s))

    # Busca por nome/título nos diálogos
    s_cf = s.casefold()
    found = None
    async for dlg in client.iter_dialogs():
        name = (dlg.name or "").strip()
        if name.casefold() == s_cf:
            found = dlg.entity
            break
        if not found and s_cf in name.casefold():
            found = found or dlg.entity
    if found:
        return found

    raise ValueError(f"Não achei chat correspondente a: {chat}")


async def ensure_client(api_id: int, api_hash: str, session_str: Optional[str]) -> TelegramClient:
    if STATE.client:
        return STATE.client
    client = TelegramClient(StringSession(session_str) if session_str else "user", api_id, api_hash)
    await client.connect()
    STATE.client = client
    return client


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return render(
        "index.html",
        code_sent=STATE.code_sent,
        authorized=STATE.authorized,
        last_error=STATE.last_error,
        session_str=STATE.session_str,
    )


@app.post("/send_code")
async def send_code(
    api_id: str = Form(...), api_hash: str = Form(...), phone: str = Form(...), session_input: str = Form("")
):
    try:
        STATE.api_id = int(api_id)
        STATE.api_hash = api_hash.strip()
        STATE.phone = phone.strip()
        STATE.last_error = None

        # Se o usuário colou uma String Session, tente reutilizar sem enviar código
        if session_input:
            STATE.session_str = session_input.strip()
            try:
                client = await ensure_client(STATE.api_id, STATE.api_hash, STATE.session_str)
                if await client.is_user_authorized():
                    STATE.authorized = True
                    STATE.session_str = client.session.save()
                    STATE.code_sent = False
                    return RedirectResponse("/", status_code=303)
                # se não autorizado, vamos enviar código abaixo
            except Exception as e:
                STATE.last_error = f"Session inválida ou falha ao conectar: {e}"

        client = await ensure_client(STATE.api_id, STATE.api_hash, STATE.session_str)
        await client.send_code_request(STATE.phone)
        STATE.code_sent = True
        return RedirectResponse("/", status_code=303)
    except Exception as e:
        STATE.last_error = f"Erro ao enviar código: {e}"
        return RedirectResponse("/", status_code=303)


@app.post("/confirm_code")
async def confirm_code(code: str = Form(""), password: str = Form("")):
    try:
        if not (STATE.api_id and STATE.api_hash and STATE.phone):
            STATE.last_error = "Preencha API ID/API HASH/Phone e envie o código primeiro."
            return RedirectResponse("/", status_code=303)
        client = await ensure_client(STATE.api_id, STATE.api_hash, STATE.session_str)
        try:
            await client.sign_in(phone=STATE.phone, code=code.strip())
        except SessionPasswordNeededError:
            if not password:
                STATE.last_error = "Conta requer senha 2FA. Forneça a senha e reenvie."
                return RedirectResponse("/", status_code=303)
            await client.sign_in(password=password)
        except PhoneCodeInvalidError:
            STATE.last_error = "Código inválido."
            return RedirectResponse("/", status_code=303)

        if await client.is_user_authorized():
            STATE.authorized = True
            STATE.session_str = client.session.save()
            STATE.last_error = None
        else:
            STATE.last_error = "Não autorizado."
        return RedirectResponse("/", status_code=303)
    except Exception as e:
        STATE.last_error = f"Falha no login: {e}"
        return RedirectResponse("/", status_code=303)


@app.post("/cleanup")
async def cleanup(
    chat: str = Form(...),
    since: str = Form(""),
    until: str = Form(""),
    limit: str = Form("5000"),
    batch: str = Form("100"),
    dry_run: str = Form("0"),
):
    summary: Dict[str, Any] = {"matched": 0, "attempted": 0, "deleted_ok": 0, "errors": {}}
    try:
        if not STATE.authorized:
            STATE.last_error = "Faça login antes de limpar."
            return render("index.html", code_sent=STATE.code_sent, authorized=STATE.authorized, last_error=STATE.last_error, session_str=STATE.session_str, summary=summary)

        client = await ensure_client(STATE.api_id, STATE.api_hash, STATE.session_str)
        entity = await resolve_chat_entity(client, chat)
        s = parse_iso(since)
        u = parse_iso(until)
        try:
            lim = max(1, min(100000, int(limit)))
        except Exception:
            lim = 5000
        try:
            bs = max(1, min(1000, int(batch)))
        except Exception:
            bs = 100
        is_dry = dry_run == "1"

        ids = []
        async for msg in client.iter_messages(entity, limit=lim):
            if s and msg.date and msg.date < s:
                continue
            if u and msg.date and msg.date > u:
                continue
            if is_service_join_leave(msg):
                ids.append(msg.id)

        summary["matched"] = len(ids)
        if not is_dry:
            for i in range(0, len(ids), bs):
                chunk = ids[i : i + bs]
                summary["attempted"] += len(chunk)
                try:
                    await client.delete_messages(entity, chunk, revoke=True)
                    summary["deleted_ok"] += len(chunk)
                except Exception as e:
                    key = str(e.__class__.__name__).lower()
                    summary["errors"][key] = summary["errors"].get(key, 0) + len(chunk)

        return render("index.html", code_sent=STATE.code_sent, authorized=STATE.authorized, last_error=None, session_str=STATE.session_str, summary=summary)
    except Exception as e:
        STATE.last_error = f"Erro na limpeza: {e}"
        return render("index.html", code_sent=STATE.code_sent, authorized=STATE.authorized, last_error=STATE.last_error, session_str=STATE.session_str, summary=summary)


@app.post("/reset")
async def reset():
    try:
        if STATE.client:
            try:
                await STATE.client.disconnect()
            except Exception:
                pass
        STATE.client = None
        STATE.api_id = None
        STATE.api_hash = None
        STATE.phone = None
        STATE.session_str = None
        STATE.code_sent = False
        STATE.authorized = False
        STATE.last_error = None
    finally:
        return RedirectResponse("/", status_code=303)


@app.get("/health")
async def health():
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
