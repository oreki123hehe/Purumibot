import os
import platform
import sys
import time
from pyrogram import filters
from pyrogram.enums import ChatType
from core import app, call
import config
import db
from utils import cmd, get_args, fmt_uptime

_cooldown = {}

def panel(title, body, footer='PURUMI • USERBOT TOOLS'):
    return f'╭━━〔 **{title}** 〕━━╮\n{body}\n╰━━━━━━━━━━━━━━╯\n_{footer}_'

@app.on_message(cmd('id'))
async def id_cmd(_, message):
    lines = [f'🗂 **Chat ID**  `{message.chat.id}`']
    if message.chat.title:
        lines.append(f'💬 **Nama**  {message.chat.title}')
    reply = message.reply_to_message
    if reply and reply.from_user:
        lines.extend(['', f'👤 **User**  {reply.from_user.first_name}', f'🆔 **User ID**  `{reply.from_user.id}`'])
    await message.edit(panel('IDENTIFIER', '\n'.join(lines)))

@app.on_message(cmd('status', 'dashboard'))
async def status_cmd(client, message):
    me = await client.get_me()
    groups = private = 0
    try:
        async for dialog in client.get_dialogs():
            if dialog.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
                groups += 1
            elif dialog.chat.type == ChatType.PRIVATE:
                private += 1
    except Exception:
        pass
    active_promos = sum(1 for job in db.data.get('promos', {}).values() if job.get('active'))
    music_state = 'ONLINE' if call else 'DISABLED'
    afk_state = 'ACTIVE' if db.data.get('afk') else 'OFF'
    body = (
        f'👤 **Account**   {me.first_name}\n'
        f'🟢 **Runtime**   Online\n'
        f'⏱ **Uptime**    `{fmt_uptime()}`\n'
        f'🐍 **Python**    `{platform.python_version()}`\n'
        f'🎵 **Music**     `{music_state}`\n'
        f'😴 **AFK**       `{afk_state}`\n'
        f'📣 **Promo jobs** `{active_promos}`\n'
        f'👥 **Dialogs**   `{groups} groups · {private} private`'
    )
    await message.edit(panel('SYSTEM DASHBOARD', body, 'PURUMI • LIVE STATUS'))

@app.on_message(cmd('join'))
async def join_cmd(client, message):
    arg = get_args(message)
    if not arg:
        return await message.edit(panel('JOIN CHAT', 'Gunakan: `.join <link/@username>`'))
    try:
        chat = await client.join_chat(arg)
        await message.edit(panel('JOIN SUCCESS', f'✅ **Berhasil bergabung**\n💬 {chat.title or chat.id}\n🆔 `{chat.id}`'))
    except Exception as exc:
        await message.edit(panel('JOIN FAILED', f'⚠️ Tidak dapat bergabung.\nDetail: `{type(exc).__name__}`'))

@app.on_message(cmd('leave') & filters.group)
async def leave_cmd(client, message):
    title = message.chat.title or str(message.chat.id)
    await message.edit(panel('LEAVE CHAT', f'👋 Keluar dari **{title}**...'))
    await client.leave_chat(message.chat.id)

@app.on_message(cmd('restart'))
async def restart_cmd(_, message):
    await message.edit(panel('RESTART', '♻️ Memulai ulang userbot...'))
    os.execv(sys.executable, [sys.executable] + sys.argv)

@app.on_message(cmd('afk'))
async def afk_cmd(_, message):
    reason = get_args(message)
    if reason.lower() == 'off':
        db.data['afk'] = None
        db.save()
        return await message.edit(panel('AFK MODE', '🟢 **Status:** dinonaktifkan'))
    db.data['afk'] = {'since': time.time(), 'reason': reason or 'Sedang tidak aktif'}
    db.save()
    await message.edit(panel('AFK MODE', f'🌙 **Status:** aktif\n📝 **Alasan:** {db.data[\'afk\'][\'reason\']}'))

@app.on_message(filters.incoming & (filters.private | filters.mentioned) & ~filters.bot, group=1)
async def afk_reply(_, message):
    afk = db.data.get('afk')
    if not afk:
        return
    now = time.time()
    if now - _cooldown.get(message.chat.id, 0) < 300:
        return
    _cooldown[message.chat.id] = now
    minutes = int((now - afk['since']) // 60)
    await message.reply(
        '╭━━〔 🌙 **SEDANG AFK** 〕━━╮\n'
        f'Pemilik akun sedang tidak aktif selama `{minutes}` menit.\n'
        f'📝 **Alasan:** {afk[\'reason\']}\n'
        '╰━━━━━━━━━━━━━━━━━━╯'
    )
