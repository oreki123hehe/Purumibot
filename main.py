import os
import asyncio
import requests
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = 33599996
API_HASH = "d029d0d0e3738e12168a2903be7bfe4b"
OWNER_ID = 5174581173
GEMINI_API_KEY = "AQ.Ab8RN6JZb4O4VcJBVipG_4iKTfYmhVSfLXFfPbDBRhx80wbI5A"

app = Client(
    "purumi_userbot",
    api_id=API_ID,
    api_hash=API_HASH
)

owner_filter = filters.user(OWNER_ID) | filters.me

@app.on_message(owner_filter & filters.command("ping"))
async def ping_pong(client: Client, message: Message):
    await message.edit(
        "🔥 **Userbot Purumi Ultimate Supreme 2026 Aktif!**\n"
        "• Sang Mata (Anti-Delete) ✅\n"
        "• Pencuri Media Privat (`/save`) ✅\n"
        "• Gemini AI (`/ai`) ✅\n"
        "• Suno AI Generator (`/suno`) ✅\n"
        "• Downloader Media Sosmed (`/dl`) ✅"
    )

@app.on_message(owner_filter & (filters.command("ai") | filters.command("gemini")))
async def ask_gemini(client: Client, message: Message):
    query = message.text.replace("/ai", "").replace("/gemini", "").strip()
    if not query:
        await message.reply("Mau tanya apa ke Gemini? Contoh: `/ai Jelaskan teori relativitas`")
        return

    msg = await message.reply("🤖 Sedang berpikir...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": query}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15).json()
        if "error" in response:
            await msg.edit(f"Gagal dari Gemini: {response['error'].get('message')}")
            return
        
        reply_text = response["candidates"][0]["content"]["parts"][0]["text"]
        if len(reply_text) > 4000:
            reply_text = reply_text[:4000] + "\n\n*(Pesan dipotong)*"
        await msg.edit(f"🤖 **Gemini AI:**\n\n{reply_text}")
    except Exception as e:
        await msg.edit(f"Error: {str(e)}")

@app.on_message(owner_filter & filters.command("suno"))
async def suno_ai_music(client: Client, message: Message):
    prompt = message.text.replace("/suno", "").strip()
    if not prompt:
        await message.reply("🎵 Masukkan tema lagu! Contoh: `/suno Rock tahun 90-an tentang perjuangan hidup`")
        return

    msg = await message.reply(f"🎶 **Suno AI** sedang meracik lirik untuk tema: *{prompt}*...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    song_prompt = f"Buatkan lirik lagu lengkap dengan struktur [Verse], [Chorus], [Bridge] bertema: {prompt}"
    data = {"contents": [{"parts": [{"text": song_prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15).json()
        lyrics = response["candidates"][0]["content"]["parts"][0]["text"]
        result_text = f"🎶 **Suno AI - Hasil Lirik** 🎶\n\n**Tema:** {prompt}\n\n{lyrics}"
        if len(result_text) > 4000:
            result_text = result_text[:4000]
        await msg.edit(result_text)
    except Exception as e:
        await msg.edit(f"Gagal: {str(e)}")

@app.on_message(owner_filter & filters.command("dl"))
async def downloader_media(client: Client, message: Message):
    link = message.text.replace("/dl", "").strip()
    if not link:
        await message.reply("Kirim link video yang mau diunduh! Contoh: `/dl https://vt.tiktok.com/...`")
        return

    msg = await message.reply("📥 Sedang memproses dan mengunduh media...")
    try:
        import yt_dlp
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'noplaylist': True,
        }
        os.makedirs("downloads", exist_ok=True)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(info)

        if os.path.exists(filename):
            await client.send_video("me", filename, caption=f"📥 Berhasil mengunduh dari: {link}")
            await msg.edit("Sukses! Video telah dikirim ke Saved Messages Anda.")
            os.remove(filename)
        else:
            await msg.edit("Gagal menemukan file video.")
    except Exception as e:
        await msg.edit(f"Gagal mengunduh media: {str(e)}")

@app.on_deleted_messages()
async def anti_delete_watcher(client: Client, messages: list[Message]):
    for msg in messages:
        if msg.chat and msg.chat.type in ["group", "supergroup"]:
            deleted_text = msg.text or msg.caption or "[Media Tanpa Teks]"
            sender = msg.from_user.first_name if msg.from_user else "Seseorang"
            try:
                await client.send_message(
                    "me",
                    f"👁️ **[SANG MATA - PESAN DIHAPUS]**\n"
                    f"• Dari Grup: {msg.chat.title}\n"
                    f"• Pengirim: {sender}\n"
                    f"• Pesan: {deleted_text}"
                )
            except Exception:
                pass

@app.on_message(owner_filter & filters.command("save"))
async def save_restricted_media(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply("Balas (reply) media dari channel/grup privat dengan perintah `/save`!")
        return

    target_msg = message.reply_to_message
    status_msg = await message.reply("🔓 Menyedot media privat...")

    try:
        file_path = await client.download_media(target_msg)
        if file_path:
            if target_msg.video:
                await client.send_video("me", file_path, caption="📥 Video privat diamankan.")
            elif target_msg.photo:
                await client.send_photo("me", file_path, caption="📥 Foto privat diamankan.")
            elif target_msg.document:
                await client.send_document("me", file_path, caption="📥 Dokumen privat diamankan.")
            else:
                await client.send_message("me", f"Media disimpan di: {file_path}")
            
            await status_msg.edit("Sukses! Media privat masuk ke Saved Messages.")
            if os.path.exists(file_path):
                os.remove(file_path)
        else:
            await status_msg.edit("Gagal mengunduh.")
    except Exception as e:
        await msg.edit(f"Error: {str(e)}")

if __name__ == "__main__":
    print("Memulai Userbot Purumi Ultimate Supreme...")
    app.run()
  
