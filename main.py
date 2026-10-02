import os
import time
import asyncio
from telethon import TelegramClient, events

# ==========================================
# KONFIGURASI KREDENSIAL (Hanya 1 Akun Utama)
# ==========================================
API_ID = 33599996
API_HASH = "d029d0d0e3738e12168a2903be7bfe4b"

# Inisialisasi hanya menggunakan sesi 'main'
client = TelegramClient('main', API_ID, API_HASH)

# ==========================================
# 0. FITUR MENU (.menu / .help)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.(menu|help)$'))
async def menu_command(event):
    try:
        menu_text = (
            "<b>✨ PURUMI UBOT - MENU UTAMA ✨</b>\n\n"
            "Berikut adalah daftar perintah yang tersedia:\n"
            "🏓 <code>.ping</code> — Cek status & latensi bot\n"
            "🔄 <code>.sync</code> — Simulasi sinkronisasi profil\n"
            "📥 <code>.save</code> — Amankan media privat / terkunci\n"
            "📢 <code>.bc [pesan]</code> — Broadcast pesan ke semua grup/channel\n"
            "📋 <code>.menu</code> — Menampilkan daftar perintah ini\n\n"
            "🤖 <i>Status: Online & Stabil (24/7 di GitHub Actions)</i>"
        )
        await event.edit(menu_text, parse_mode='html')
    except Exception as e:
        await event.respond(f"❌ Error Menu: {str(e)}")

# ==========================================
# 1. FITUR PING (Cek Status & Latensi)
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
# 2. FITUR SYNC PROFIL (.sync)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.sync$'))
async def sync_profile(event):
    try:
        await event.edit("🔄 [purumi_ubot] Sinkronisasi profil berhasil diterapkan ke sistem!")
    except Exception as e:
        await event.respond(f"❌ Gagal sinkron: {str(e)}")

# ==========================================
# 3. FITUR BYPASS MEDIA PRIVAT (.save)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.save$'))
async def save_restricted_media(event):
    try:
        reply = await event.get_reply_message()
        if not reply or not reply.media:
            await event.edit("❌ [purumi_ubot] Balas (reply) ke pesan foto/video terkunci yang ingin disimpan!")
            return
        
        await event.edit("📥 [purumi_ubot] Mengamankan media dari channel/grup privat...")
        file_path = await client.download_media(reply)
        if file_path:
            await client.send_file('me', file_path, caption="📥 Berhasil mengamankan media privat via purumi_ubot.")
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
@client.on(events.NewMessage(outgoing=True, pattern=r'^\.bc\s+(.+)'))
async def broadcast_groups(event):
    message_to_send = event.pattern_match.group(1)
    await event.edit("⏳ [purumi_ubot] Memulai pengiriman pesan siaran ke semua grup...")
    
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
            f"✅ **[purumi_ubot] Broadcast Selesai!**\n"
            f"- Terkirim: {success_count} grup/channel\n"
            f"- Gagal: {fail_count} grup/channel"
        )
    except Exception as e:
        await event.respond(f"❌ Terjadi kesalahan saat broadcast: {str(e)}")

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
    
