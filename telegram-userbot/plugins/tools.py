import os
import sys
import time
from pyrogram import filters
from core import app
import db
from utils import cmd, get_args

_cooldown = {}


@app.on_message(cmd("id"))
async def id_cmd(_, message):
    text = f"💬 Chat ID: `{message.chat.id}`"
    reply = message.reply_to_message
    if reply and reply.from_user:
        text += f"\n👤 User ID: `{reply.from_user.id}`"
    await message.edit(text)


@app.on_message(cmd("join"))
async def join_cmd(client, message):
    arg = get_args(message)
    if not arg:
        return await message.edit("Gunakan: `.join <link/@username>`")
    try:
        chat = await client.join_chat(arg)
        await message.edit(f"✅ Bergabung ke **{chat.title or chat.id}** (`{chat.id}`)")
    except Exception as exc:
        await message.edit(f"❌ Gagal join: `{type(exc).__name__}`")


@app.on_message(cmd("leave") & filters.group)
async def leave_cmd(client, message):
    await message.edit("👋 Keluar dari grup ini...")
    await client.leave_chat(message.chat.id)


@app.on_message(cmd("restart"))
async def restart_cmd(_, message):
    await message.edit("♻️ Restart...")
    os.execv(sys.executable, [sys.executable] + sys.argv)


@app.on_message(cmd("afk"))
async def afk_cmd(_, message):
    reason = get_args(message)
    if reason.lower() == "off":
        db.data["afk"] = None
        db.save()
        return await message.edit("✅ Mode AFK dimatikan.")
    db.data["afk"] = {"since": time.time(), "reason": reason or "Sedang tidak aktif"}
    db.save()
    await message.edit(f"😴 Mode AFK aktif: {db.data['afk']['reason']}")


@app.on_message(filters.incoming & (filters.private | filters.mentioned) & ~filters.bot, group=1)
async def afk_reply(_, message):
    afk = db.data.get("afk")
    if not afk:
        return
    now = time.time()
    if now - _cooldown.get(message.chat.id, 0) < 300:
        return
    _cooldown[message.chat.id] = now
    minutes = int((now - afk["since"]) // 60)
    await message.reply(f"😴 Pemilik akun sedang AFK ({minutes} menit)\nAlasan: {afk['reason']}")
