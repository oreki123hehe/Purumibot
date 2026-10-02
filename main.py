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

@app.on_message(filters.command(["menu", "help"], prefixes=".") & filters.me)
async def menu_command(client, message: Message):
    menu_text = (
        "<b>⚡ PURUMI UBOT BETA (SOUNDCLOUD EDITION) ⚡</b>\n\n"
        "Daftar Perintah Aktif (Mode Beta):\n"
        "🏓 <code>.ping</code> — Cek status & latensi bot\n"
        "🆔 <code>.id</code> — Cek ID Telegram target (reply/username)\n"
        "📥 <code>.save</code> — Bypass & amankan media privat / terkunci\n"
        "📢 <code>.bc [pesan]</code> — Broadcast pesan ke semua grup\n"
        "🎵 <code>.play [judul lagu]</code> — Putar musik via SoundCloud\n"
        "⏹️ <code>.stop</code> — Berhentikan pemutar musik VC\n"
        "👀 <code>.sangmata</code> — Cek riwayat nama (reply target)\n"
        "📋 <code>.menu</code> — Menampilkan menu ini\n\n"
        "🧪 <i>Status: Beta Online 24/7</i>"
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
        f"🧪 Status: <b>Beta Testing Online (24/7)</b>"
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
    
    await message.edit("📥 Mem-bypass dan amankan media privat...")
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

def search_soundcloud(query):
    # Jika pengguna memasukkan link SoundCloud langsung
    if "soundcloud.com" in query:
        return query, "Direct SoundCloud URL"
        
    search_query = f"scsearch1:{query}"
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'skip_download': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(search_query, download=False)
            if 'entries' in info and len(info['entries']) > 0:
                item = info['entries'][0]
                return item['url'], item.get('title', 'Unknown Title')
        except Exception as e:
            print(f"Error SoundCloud search: {e}")
    return None, None

@app.on_message(filters.command("play", prefixes=".") & filters.me)
async def play_voice_chat(client, message: Message):
    if len(message.command) < 2:
        await message.edit("❌ Masukkan judul lagu! Contoh: `.play dj remix`")
        return
        
    query = message.text.split(None, 1)[1]
    await message.edit(f"🔍 Mencari musik di SoundCloud: `{query}`...")
    
    stream_url, title = search_soundcloud(query)
    if not stream_url:
        await message.edit("❌ Lagu tidak ditemukan di SoundCloud.")
        return
        
    chat_id = message.chat.id
    try:
        from pytgcalls import PyTgCalls
        call_py = PyTgCalls(client)
        await call_py.start()
        await call_py.play(chat_id, stream_url)
        await message.edit(f"🎶 **[BETA] Memutar di Voice Chat:**\n`{title}`")
    except Exception as e:
        await message.edit(f"❌ Gagal memutar di Voice Chat: {str(e)}")

@app.on_message(filters.command("stop", prefixes=".") & filters.me)
async def stop_voice_chat(client, message: Message):
    chat_id = message.chat.id
    try:
        from pytgcalls import PyTgCalls
        call_py = PyTgCalls(client)
        await call_py.leave_group_call(chat_id)
        await message.edit("⏹ Pemutaran Voice Chat dihentikan.")
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

async def main():
    print("Menghidupkan Purumi UBot BETA (SoundCloud)...")
    await app.start()
    print("Purumi UBot BETA aktif 24/7!")
    await idle()

if __name__ == "__main__":
    app.run(main())
    
