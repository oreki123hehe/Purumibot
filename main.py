import os
import time
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from yt_dlp import YoutubeDL

API_ID = 33599996
API_HASH = "d029d0d0e3738e12168a2903be7bfe4b"
STRING_SESSION = os.getenv("STRING_SESSION", "")

if STRING_SESSION:
    app = Client("purumi_ubot", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)
else:
    app = Client("main", api_id=API_ID, api_hash=API_HASH)

# Sistem Anti-Crash untuk inisialisasi Voice Chat
try:
    from pytgcalls import PyTgCalls
    call_py = PyTgCalls(app)
    VC_MODE = True
except Exception as e:
    print(f"Modul Voice Chat gagal dimuat: {e}")
    VC_MODE = False

@app.on_message(filters.command(["menu", "help"], prefixes=".") & filters.me)
async def menu_command(client, message: Message):
    menu_text = (
        "<b>⚡ PURUMI UBOT BETA ⚡</b>\n\n"
        "Daftar Perintah Aktif:\n"
        "🏓 <code>.ping</code> — Cek status & latensi bot\n"
        "🆔 <code>.id</code> — Cek ID Telegram target\n"
        "📥 <code>.save</code> — Bypass & amankan media privat\n"
        "📢 <code>.bc [pesan]</code> — Broadcast ke semua grup\n"
        "🎵 <code>.play [judul]</code> — Putar musik di VC\n"
        "⏹️ <code>.stop</code> — Berhentikan pemutar musik VC\n"
        "👀 <code>.sangmata</code> — Cek riwayat nama target\n"
        "📋 <code>.menu</code> — Menampilkan menu ini\n\n"
        f"🧪 <i>Status Bot: Online 24/7</i>\n"
        f"🔊 <i>Status VC: {'AKTIF ✅' if VC_MODE else 'TIDAK DIDUKUNG SERVER ❌'}</i>"
    )
    await message.edit(menu_text)

@app.on_message(filters.command("ping", prefixes=".") & filters.me)
async def ping_command(client, message: Message):
    start_time = time.time()
    m = await message.edit("🏓 Pinging...")
    end_time = time.time()
    latency = round((end_time - start_time) * 1000, 2)
    await m.edit(
        f"<b>Purumi UBot Beta Pong! 🏓</b>\n"
        f"⏱️ Latensi: <code>{latency} ms</code>\n"
        f"🟢 Status: <b>Online & Stabil (24/7)</b>"
    )

@app.on_message(filters.command("id", prefixes=".") & filters.me)
async def get_target_id(client, message: Message):
    chat = message.chat
    target_user = None
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            target_user = await client.get_users(message.command[1])
        except Exception:
            pass
    if target_user:
        await message.edit(f"🆔 **ID Target:**\n• Nama: {target_user.first_name}\n• ID: <code>{target_user.id}</code>")
    else:
        await message.edit(f"🆔 **ID Chat Ini:**\n• Judul: {chat.title if chat.title else chat.first_name}\n• ID: <code>{chat.id}</code>")

@app.on_message(filters.command("save", prefixes=".") & filters.me)
async def save_restricted_media(client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.media:
        await message.edit("❌ Balas ke pesan media terkunci!")
        return
    await message.edit("📥 Mem-bypass media...")
    try:
        await client.forward_chats('me', message.reply_to_message.id)
        await message.edit("✅ Media diteruskan ke Saved Messages!")
    except Exception:
        await message.edit("❌ Gagal bypass.")

@app.on_message(filters.command("bc", prefixes=".") & filters.me)
async def broadcast_groups(client, message: Message):
    if len(message.command) < 2:
        await message.edit("❌ Format salah! Gunakan: `.bc [pesan]`")
        return
    msg_text = message.text.split(None, 1)[1]
    await message.edit("⏳ Memulai siaran...")
    success, fail = 0, 0
    async for dialog in client.get_dialogs():
        if dialog.chat.type in ["supergroup", "group", "channel"]:
            try:
                await client.send_message(dialog.chat.id, msg_text)
                success += 1
                await asyncio.sleep(1.5)
            except Exception:
                fail += 1
    await message.reply(f"✅ **Broadcast Selesai!**\n- Sukses: {success}\n- Gagal: {fail}")

def search_music(query):
    ydl_opts = {'format': 'bestaudio/best', 'noplaylist': True, 'quiet': True}
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            if 'entries' in info and len(info['entries']) > 0:
                item = info['entries'][0]
                return item['url'], item.get('title', 'Unknown Title')
        except Exception:
            pass
    return None, None

@app.on_message(filters.command("play", prefixes=".") & filters.me)
async def play_voice_chat(client, message: Message):
    if not VC_MODE:
        await message.edit("❌ Server GitHub Actions tidak mendukung Voice Chat. Bot tidak dapat memutar musik.")
        return
    if len(message.command) < 2:
        await message.edit("❌ Masukkan judul lagu!")
        return
    query = message.text.split(None, 1)[1]
    await message.edit(f"🔍 Mencari: `{query}`...")
    stream_url, title = search_music(query)
    if not stream_url:
        await message.edit("❌ Lagu tidak ditemukan.")
        return
    try:
        await call_py.play(message.chat.id, stream_url)
        await message.edit(f"🎶 **[BETA] Memutar:**\n`{title}`")
    except Exception as e:
        await message.edit(f"❌ Gagal memutar VC: {str(e)}")

@app.on_message(filters.command("stop", prefixes=".") & filters.me)
async def stop_voice_chat(client, message: Message):
    if not VC_MODE:
        return
    try:
        await call_py.leave_group_call(message.chat.id)
        await message.edit("⏹ Pemutaran dihentikan.")
    except Exception:
        pass

@app.on_message(filters.command("sangmata", prefixes=".") & filters.me)
async def sangmata_tracker(client, message: Message):
    if not message.reply_to_message:
        await message.edit("❌ Balas ke pesan target!")
        return
    target_user = message.reply_to_message.from_user
    if not target_user:
        return
    await message.edit(f"👀 Mengecek riwayat nama untuk `{target_user.first_name}`...")
    try:
        await client.send_message("@SangMata_BOT", f"{target_user.id}")
        await asyncio.sleep(3)
        async for msg in client.get_chat_history("@SangMata_BOT", limit=3):
            if msg.text and str(target_user.id) in msg.text:
                await message.edit(f"📋 **Sangmata:**\n\n{msg.text}")
                return
        await message.edit("⚠️ Cek pesan masuk dari `@SangMata_BOT`.")
    except Exception:
        await message.edit("❌ Gagal mengecek SangMata.")

if __name__ == "__main__":
    print("Mulai menghidupkan Purumi UBot BETA...")
    if VC_MODE:
        call_py.run()
    else:
        app.run()
        
