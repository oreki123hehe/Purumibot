import os
import time
import asyncio
import requests
from telethon import TelegramClient, events

# ==========================================
# KONFIGURASI KREDENSIAL UTAMA
# ==========================================
API_ID = 33599996
API_HASH = "d029d0d0e3738e12168a2903be7bfe4b"
SUNO_API_KEY = "d92ffda3944beccca46e988984668171"

# Inisialisasi klien murni 1 akun ('main')
client = TelegramClient('main', API_ID, API_HASH)

# ==========================================
# 0. MENU PERINTAH (.menu / .help)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.(menu|help)$'))
async def menu_command(event):
    try:
        menu_text = (
            "<b>✨ PURUMI UBOT - MENU UTAMA ✨</b>\n\n"
            "Daftar Perintah Aktif:\n"
            "🏓 <code>.ping</code> — Cek status & latensi bot\n"
            "📥 <code>.save</code> — Amankan media privat / terkunci\n"
            "📢 <code>.bc [pesan]</code> — Broadcast pesan ke semua grup/channel\n"
            "🎵 <code>.suno [tema]</code> — Buat musik AI via Suno\n"
            "📋 <code>.menu</code> — Menampilkan menu ini\n\n"
            "🤖 <i>Status: Online & Stabil (24/7)</i>"
        )
        await event.edit(menu_text, parse_mode='html')
    except Exception as e:
        await event.respond(f"❌ Error Menu: {str(e)}")

# ==========================================
# 1. CEK STATUS & LATENSI (.ping)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.ping$'))
async def ping_command(event):
    try:
        start_time = time.time()
        message = await event.edit("🏓 Pinging...")
        end_time = time.time()
        latency = round((end_time - start_time) * 1000, 2)
        await message.edit(
            f"<b>Purumi UBot Pong! 🏓</b>\n"
            f"⏱️ Latensi: <code>{latency} ms</code>\n"
            f"🤖 Bot Name: <b>purumi_ubot</b>\n"
            f"🟢 Status: <b>Online & Stabil (24/7)</b>",
            parse_mode='html'
        )
    except Exception as e:
        await event.respond(f"❌ Error Ping: {str(e)}")

# ==========================================
# 2. AMANKAN MEDIA PRIVAT (.save)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.save$'))
async def save_restricted_media(event):
    try:
        reply = await event.get_reply_message()
        if not reply or not reply.media:
            await event.edit("❌ Balas (reply) ke pesan foto/video terkunci yang ingin disimpan!")
            return
        
        await event.edit("📥 Mengamankan media dari channel/grup privat...")
        file_path = await client.download_media(reply)
        if file_path:
            await client.send_file('me', file_path, caption="📥 Berhasil mengamankan media privat via purumi_ubot.")
            if os.path.exists(file_path):
                os.remove(file_path)
            await event.edit("✅ Media berhasil dikirim ke Saved Messages Anda!")
        else:
            await event.edit("❌ Gagal mengunduh media.")
    except Exception as e:
        await event.respond(f"❌ Error: {str(e)}")

# ==========================================
# 3. BROADCAST PESAN (.bc)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.bc\s+(.+)'))
async def broadcast_groups(event):
    message_to_send = event.pattern_match.group(1)
    await event.edit("⏳ Memulai pengiriman pesan siaran...")
    
    success_count = 0
    fail_count = 0
    
    try:
        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                try:
                    await client.send_message(dialog.id, message_to_send)
                    success_count += 1
                    await asyncio.sleep(1.5)
                except Exception:
                    fail_count += 1
                    continue
                    
        await event.respond(
            f"✅ **Broadcast Selesai!**\n"
            f"- Terkirim: {success_count} grup/channel\n"
            f"- Gagal: {fail_count} grup/channel"
        )
    except Exception as e:
        await event.respond(f"❌ Error Broadcast: {str(e)}")

# ==========================================
# 4. SUNO AI GENERATOR (.suno)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.suno\s+(.+)'))
async def generate_suno_music(event):
    query = event.pattern_match.group(1)
    await event.edit(f"🎵 Mengirim permintaan Suno AI untuk tema: `{query}`...")
    
    try:
        url = "https://api.sunoapi.org/v1/generate"
        headers = {
            "Authorization": f"Bearer {SUNO_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "prompt": query,
            "instrumental": False
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            audio_url = data.get("audio_url") or data.get("data", {}).get("audio_url")
            if audio_url:
                await client.send_file('me', audio_url, caption=f"🎶 **Suno AI Result**\nTema: {query}")
                await event.edit("✅ Lagu berhasil dibuat dan dikirim ke Saved Messages!")
            else:
                await event.edit("✅ Permintaan Suno diproses!")
        else:
            await event.respond(f"⚠️ Server Suno sedang gangguan / endpoint berubah (Status: {response.status_code}).")
    except Exception as e:
        await event.respond(f"❌ Error Suno AI: {str(e)}")

# ==========================================
# MENJALANKAN SISTEM
# ==========================================
def main():
    print("Menghidupkan purumi_ubot...")
    client.start()
    print("purumi_ubot siap digunakan 24/7!")
    client.run_until_disconnected()

if __name__ == '__main__':
    main()
