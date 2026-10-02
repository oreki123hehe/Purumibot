import os
import time
import asyncio
import requests
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from yt_dlp import YoutubeDL

API_ID = 33599996
API_HASH = "d029d0d0e3738e12168a2903be7bfe4b"
SUNO_API_KEY = "d92ffda3944beccca46e988984668171"

STRING_SESSION = os.getenv("STRING_SESSION", "")

if STRING_SESSION:
    app = Client("purumi_ubot", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)
else:
    app = Client("main", api_id=API_ID, api_hash=API_HASH)

call_py = PyTgCalls(app)

@app.on_message(filters.command(["menu", "help"], prefixes=".") & filters.me)
async def menu_command(client, message: Message):
    menu_text = (
        "<b>✨ PURUMI UBOT (ULTIMATE PYROGRAM) ✨</b>\n\n"
        "Daftar Perintah Aktif:\n"
        "🏓 <code>.ping</code> — Cek status & latensi bot\n"
        "🆔 <code>.id</code> — Cek ID Telegram target (reply/username)\n"
        "📥 <code>.save</code> — Bypass & amankan media privat / terkunci\n"
        "📢 <code>.bc [pesan]</code> — Broadcast pesan ke semua grup\n"
        "🎵 <code>.play [judul/link yt]</code> — Putar musik di Voice Chat\n"
        "⏹️ <code>.stop</code> — Berhentikan pemutar musik VC\n"
        "👀 <code>.sangmata</code> — Cek riwayat nama (reply target)\n"
        "🎶 <code>.suno [tema]</code> — Buat musik AI via Suno\n"
        "📋 <code>.menu</code> — Menampilkan menu ini\n\n"
        "🤖 <i>Status: Pyrogram 64-bit Online 24/7</i>"
    )
    await message.edit(menu_text)

@app.on_message(filters.command("ping", prefixes=".") & filters.me)
async def ping_command(client, message: Message):
    start_time = time.time()
    m = await message.edit("🏓 Pinging...")
    end_time = time.time()
    latency = round((end_time - start_time) * 1000, 2)
    await m.edit(
        f"<b>Purumi UBot Pyrogram Pong! 🏓</b>\n"
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
        identifier = message.command[1]
        try:
            target_user = await client.get_users(identifier)
        except Exception:
            pass
            
    if target_user:
        await message.edit(
            f"🆔 **Informasi ID Target:**\n"
            f"• Nama: {target_user.first_name}\n"
            f"• ID: <code>{target_user.id}</code>\n"
            f"• Username: @{target_user.username if target_user.username else 'Tidak ada'}"
        )
    else:
        await message.edit(
            f"🆔 **Informasi Chat Ini:**\n"
            f"• Judul/Nama: {chat.title if chat.title else chat.first_name}\n"
            f"• ID Chat: <code>{chat.id}</code>\n"
            f"• Tipe: {chat.type}"
        )

@app.on_message(filters.command("save", prefixes=".") & filters.me)
async def save_restricted_media(client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.media:
        await message.edit("❌ Balas (reply) ke pesan foto/video grup/channel privat yang terkunci!")
        return
    
    await message.edit("📥 Mem-bypass dan mengamankan media privat...")
    try:
        file_path = await message.reply_to_message.download()
        if file_path:
            await client.send_document('me', file_path, caption="📥 Berhasil mengamankan media privat.")
            if os.path.exists(file_path):
                os.remove(file_path)
            await message.edit("✅ Media privat berhasil dikirim ke Saved Messages!")
        else:
            await message.forward_chats('me', message.reply_to_message.id)
            await message.edit("✅ Media diteruskan ke Saved Messages!")
    except Exception as e:
        try:
            await client.forward_chats('me', message.reply_to_message.id)
            await message.edit("✅ Media diteruskan ke Saved Messages!")
        except Exception as err:
            await message.edit(f"❌ Gagal bypass: {str(err)}")

@app.on_message(filters.command("bc", prefixes=".") & filters.me)
async def broadcast_groups(client, message: Message):
    if len(message.command) < 2:
        await message.edit("❌ Format salah! Gunakan: `.bc [pesan]`")
        return
    
    msg_text = message.text.split(None, 1)[1]
    await message.edit("⏳ Memulai pengiriman pesan siaran...")
    
    success = 0
    fail = 0
    
    async for dialog in client.get_dialogs():
        if dialog.chat.type in ["supergroup", "group", "channel"]:
            try:
                await client.send_message(dialog.chat.id, msg_text)
                success += 1
                await asyncio.sleep(1.5)
            except Exception:
                fail += 1
                
    await message.reply(f"✅ **Broadcast Selesai!**\n- Terkirim: {success}\n- Gagal: {fail}")

def search_youtube(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)
            if 'entries' in info and len(info['entries']) > 0:
                return info['entries'][0]['url'], info['entries'][0].get('title', 'Unknown Title')
        except Exception:
            pass
    return None, None

@app.on_message(filters.command("play", prefixes=".") & filters.me)
async def play_voice_chat(client, message: Message):
    if len(message.command) < 2:
        await message.edit("❌ Masukkan judul lagu! Contoh: `.play dj remix`")
        return
        
    query = message.text.split(None, 1)[1]
    await message.edit(f"🔍 Mencari lagu: `{query}`...")
    
    stream_url, title = search_youtube(query)
    if not stream_url:
        await message.edit("❌ Lagu tidak ditemukan di YouTube.")
        return
        
    chat_id = message.chat.id
    try:
        await call_py.join_group_call(
            chat_id,
            AudioPiped(stream_url),
        )
        await message.edit(f"🎶 **Sedang Memutar di Voice Chat:**\n`{title}`")
    except Exception as e:
        await message.edit(f"❌ Gagal memutar di Voice Chat: {str(e)}")

@app.on_message(filters.command("stop", prefixes=".") & filters.me)
async def stop_voice_chat(client, message: Message):
    chat_id = message.chat.id
    try:
        await call_py.leave_group_call(chat_id)
        await message.edit("⏹️️ Pemutaran Voice Chat dihentikan.")
    except Exception as e:
        await message.edit(f"❌ Gagal menghentikan pemutaran: {str(e)}")

@app.on_message(filters.command("sangmata", prefixes=".") & filters.me)
async def sangmata_tracker(client, message: Message):
    if not message.reply_to_message:
        await message.edit("❌ Balas (reply) ke pesan target yang ingin dicek riwayat namanya!")
        return
    
    target_user = message.reply_to_message.from_user
    if not target_user:
        await message.edit("❌ Tidak dapat mendeteksi pengguna dari pesan tersebut.")
        return
        
    await message.edit(f"👀 Mengecek riwayat nama untuk `{target_user.first_name}`...")
    
    try:
        await client.send_message("@SangMata_BOT", f"{target_user.id}")
        await asyncio.sleep(3)
        
        async for msg in client.get_chat_history("@SangMata_BOT", limit=3):
            if msg.text and target_user.first_name.lower() in msg.text.lower() or str(target_user.id) in msg.text:
                await message.edit(f"📋 **Riwayat Nama / Sangmata:**\n\n{msg.text}")
                return
                
        await message.edit(f"⚠️ SangMata merespons, silakan cek pesan masuk dari `@SangMata_BOT`.")
    except Exception as e:
        await message.edit(f"❌ Gagal mengecek SangMata: {str(e)}")

@app.on_message(filters.command("suno", prefixes=".") & filters.me)
async def generate_suno_music(client, message: Message):
    if len(message.command) < 2:
        await message.edit("❌ Masukkan tema lagu! Contoh: `.suno lofi santai`")
        return
        
    query = message.text.split(None, 1)[1]
    await message.edit(f"🎵 Memproses permintaan Suno AI: `{query}`...")
    
    try:
        url = "https://api.sunoapi.org/v1/generate"
        headers = {
            "Authorization": f"Bearer {SUNO_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {"prompt": query, "instrumental": False}
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            audio_url = data.get("audio_url") or data.get("data", {}).get("audio_url")
            if audio_url:
                await client.send_audio('me', audio_url, caption=f"🎶 **Suno AI Result**\nTema: {query}")
                await message.edit("✅ Lagu berhasil dibuat dan dikirim ke Saved Messages!")
            else:
                await message.edit("✅ Permintaan Suno diproses!")
        else:
            await message.edit(f"⚠️ Server Suno status: {response.status_code}")
    except Exception as e:
        await message.edit(f"❌ Error Suno AI: {str(e)}")

async def main():
    print("Menghidupkan Pyrogram & PyTgCalls userbot...")
    await call_py.start()
    await app.start()
    print("purumi_ubot Pyrogram aktif 24/7 dengan fitur lengkap!")
    await idle()

if __name__ == "__main__":
    app.run(main())
    
