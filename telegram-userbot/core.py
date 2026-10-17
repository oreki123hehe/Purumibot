import os
from pyrogram import Client
import config

os.makedirs("data", exist_ok=True)

app = Client(
    name="userbot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    session_string=config.SESSION_STRING or None,
    workdir="data",
)

try:
    from pytgcalls import PyTgCalls
    call = PyTgCalls(app)
except Exception:
    call = None
