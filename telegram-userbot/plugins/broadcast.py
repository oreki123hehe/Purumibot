import asyncio
from pyrogram.enums import ChatType
from core import app
import config
import db
from utils import cmd, get_args, send_payload

state = {'stop': False, 'running': False}

async def _group_targets(client):
    blocked = {int(item) for item in db.data.get('blacklist', [])}
    targets = []
    async for dialog in client.get_dialogs():
        chat = dialog.chat
        if chat.id in blocked:
            continue
        if chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
            targets.append(chat.id)
    return targets

@app.on_message(cmd('gcast', 'bc'))
async def gcast(client, message):
    if state['running']:
        return await message.edit('⚠️ Broadcast sedang berjalan. Gunakan .bcstop untuk menghentikannya.')
    text = get_args(message)
    reply = message.reply_to_message
    source = (reply.chat.id, reply.id) if reply else None
    if not text and not source:
        return await message.edit('Gunakan .gcast <teks> atau balas pesan dengan .gcast.')
    state.update(stop=False, running=True)
    try:
        await message.edit('🔎 Mengumpulkan grup dari dialog akun...')
        targets = await _group_targets(client)
        if not targets:
            return await message.edit('Tidak ada grup target. Pastikan akun sudah bergabung ke grup.')
        sent = failed = 0
        for index, chat_id in enumerate(targets, 1):
            if state['stop']:
                break
            try:
                await send_payload(client, chat_id, text or None, source)
                sent += 1
            except Exception:
                failed += 1
            if index % 5 == 0:
                try:
                    await message.edit(f'📢 Broadcast berjalan: {index}/{len(targets)}\n✅ {sent} | ❌ {failed}')
                except Exception:
                    pass
            await asyncio.sleep(max(3.0, config.BC_DELAY))
        status = 'dihentikan' if state['stop'] else 'selesai'
        await message.edit(f'📢 Broadcast {status}\n✅ Berhasil: {sent}\n❌ Gagal: {failed}\n🎯 Total grup: {len(targets)}')
    finally:
        state['running'] = False
        state['stop'] = False

@app.on_message(cmd('bcstop'))
async def bcstop(_, message):
    if not state['running']:
        return await message.edit('Tidak ada broadcast yang berjalan.')
    state['stop'] = True
    await message.edit('🛑 Permintaan berhenti diterima.')

def _target_id(message):
    arg = get_args(message)
    try:
        return int(arg) if arg else message.chat.id
    except ValueError:
        return None

@app.on_message(cmd('addbl'))
async def addbl(_, message):
    chat_id = _target_id(message)
    if chat_id is None:
        return await message.edit('ID chat tidak valid.')
    blocked = db.data.setdefault('blacklist', [])
    if chat_id not in blocked:
        blocked.append(chat_id)
        db.save()
    await message.edit(f'🚫 Chat {chat_id} ditambahkan ke blacklist broadcast.')

@app.on_message(cmd('delbl'))
async def delbl(_, message):
    chat_id = _target_id(message)
    blocked = db.data.setdefault('blacklist', [])
    if chat_id in blocked:
        blocked.remove(chat_id)
        db.save()
        return await message.edit(f'✅ Chat {chat_id} dihapus dari blacklist.')
    await message.edit('Chat tersebut tidak ada di blacklist.')

@app.on_message(cmd('listbl'))
async def listbl(_, message):
    blocked = db.data.setdefault('blacklist', [])
    lines = '\n'.join(str(chat_id) for chat_id in blocked) if blocked else '(kosong)'
    await message.edit('🚫 Blacklist broadcast\n' + lines)
