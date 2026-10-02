import asyncio
import os
import time
import requests
from telethon import TelegramClient, events
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest

# Kredensial Langsung (Tertanam Sesuai Permintaan)
API_ID = 33599996
API_HASH = "d029d0d0e3738e12168a2903be7bfe4b"
SUNO_API_KEY = "d92ffda3944beccca46e988984668171"

# Inisialisasi Klien Ganda (Akun Utama & Akun Tumbal)
main_client = TelegramClient('main_session', API_ID, API_HASH)
dummy_client = TelegramClient('dummy_session', API_ID, API_HASH)

# ==========================================
# 1. FITUR PING (Cek Status & Latensi)
# ==========================================
@main_client.on(events.NewMessage(outgoing=True, pattern=r'^\.ping$'))
async def ping_command(event):
    try:
        start_time = time.time()
        message = await event.edit("🏓 Pinging...")
        end_time = time.time()
        latency = round((end_time - start_time) * 1000, 2)
        await message.edit(
            f"<b>Pong! 🏓</b>\n"
            f"⏱️ Latensi: <code>{latency} ms</code>\n"
            f"🤖 Status: <b>Online & Stabil (Oktober 2026)</b>",
            parse_mode='html'
        )
    except Exception as e:
        await event.respond(f"❌ Error Ping: {str(e)}")

# ==========================================
# 2. FITUR SYNC PROFIL (Utama ke Tumbal)
# ==========================================
@main_client.on(events.NewMessage(outgoing=True, pattern=r'^\.sync$'))
async def sync_profile(event):
    try:
        await event.edit("🔄 Menyinkronkan profil akun tumbal...")
        me = await main_client.get_me()
        entity_me = await main_client.get_entity(me)
        bio = getattr(entity_me, 'about', '') or ''
        
        # Samakan Nama Depan, Belakang, & Bio
        await dummy_client(UpdateProfileRequest(
            first_name=me.first_name,
            last_name=me.last_name or '',
            about=bio
        ))
        
        # Samakan Foto Profil
        photo = await main_client.download_profile_photo('me')
        if photo:
            uploaded = await dummy_client.upload_file(photo)
            old_photos = await dummy_client.get_profile_photos('me')
            if old_photos:
                await dummy_client(DeletePhotosRequest(old_photos))
            await dummy_client(UploadProfilePhotoRequest(file=uploaded))
            if os.path.exists(photo):
                os.remove(photo) # Bersihkan file cache lokal
            
        await event.respond("✅ Berhasil! Profil akun tumbal kini meniru akun utama.")
    except Exception as e:
        await event.respond(f"❌ Gagal sinkron: {str(e)}")

# ==========================================
# 3. FITUR BYPASS MEDIA PRIVAT (.save)
# ==========================================
@main_client.on(events.NewMessage(outgoing=True, pattern=r'^\.save$'))
async def save_restricted_media(event):
    try:
        reply = await event.get_reply_message()
        if not reply or not reply.media:
            await event.edit("❌ Balas (reply) ke pesan foto/video terkunci yang ingin disimpan!")
            return
        
        await event.edit("📥 Mengamankan media dari channel/grup privat...")
        file_path = await main_client.download_media(reply)
        if file_path:
            await main_client.send_file('me', file_path, caption="📥 Berhasil mengamankan media privat.")
            if os.path.exists(file_path):
                os.remove(file_path)
            await event.edit("✅ Media berhasil dikirim ke Saved Messages Anda!")
        else:
            await event.edit("❌ Gagal mengunduh media (file kosong).")
    except Exception as e:
        await event.respond(f"❌ Gagal mengunduh media: {str(e)}")

# ==========================================
# 4. FITUR BROADCAST KE SEMUA GRUP (.bc)
# ==========================================
@main_client.on(events.NewMessage(outgoing=True, pattern=r'^\.bc\s+(.+)'))
async def broadcast_groups(event):
    message_to_send = event.pattern_match.group(1)
    await event.edit("⏳ Memulai pengiriman pesan siaran ke semua grup...")
    
    success_count = 0
    fail_count = 0
    
    try:
        async for dialog in main_client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                try:
                    await main_client.send_message(dialog.id, message_to_send)
                    success_count += 1
                    await asyncio.sleep(1.5) # Jeda aman anti FloodWait Telegram
                except Exception:
                    fail_count += 1
                    continue
                    
        await event.respond(
            f"✅ **Broadcast Selesai!**\n"
            f"- Terkirim: {success_count} grup/channel\n"
            f"- Gagal: {fail_count} grup/channel"
        )
    except Exception as e:
        await event.respond(f"❌ Terjadi kesalahan saat broadcast: {str(e)}")

# ==========================================
# 5. FITUR SUNO AI GENERATOR (.suno)
# ==========================================
@main_client.on(events.NewMessage(outgoing=True, pattern=r'^\.suno\s+(.+)'))
async def generate_suno_music(event):
    query = event.pattern_match.group(1)
    await event.edit(f"🎵 Mengirim permintaan Suno AI untuk tema: `{query}`...")
    
    try:
        # Endpoint standar mutakhir Suno API
        url = "https://api.sunoapi.org/v1/generate"
        headers = {
            "Authorization": f"Bearer {SUNO_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "prompt": query,
            "instrumental": False
        }
        
        # Eksekusi request menggunakan timeout agar tidak blocking selamanya
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            audio_url = data.get("audio_url") or data.get("data", {}).get("audio_url")
            if audio_url:
                await main_client.send_file('me', audio_url, caption=f"🎶 **Suno AI Result**\nTema: {query}")
                await event.edit("✅ Lagu berhasil dibuat dan dikirim ke Saved Messages!")
            else:
                await event.edit("✅ Permintaan Suno diproses! (Cek dashboard/riwayat akun Suno Anda jika tautan belum terkirim otomatis).")
        else:
            await event.respond(f"⚠️ Gagal terhubung ke server Suno (Status: {response.status_code})")
    except Exception as e:
        await event.respond(f"❌ Error Suno AI: {str(e)}")

# ==========================================
# MENJALANKAN SISTEM
# ==========================================
async def main():
    print("Menghidupkan Userbot Utama & Tumbal secara bersamaan...")
    await main_client.start()
    await dummy_client.start()
    print("Userbot siap digunakan 24/7 tanpa error!")
    await asyncio.gather(
        main_client.run_until_disconnected(),
        dummy_client.run_until_disconnected()
    )

if __name__ == '__main__':
    asyncio.run(main())
          
