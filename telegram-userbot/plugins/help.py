from core import app
from utils import cmd

HELP = '''╭━━〔 **PURUMI USERBOT** 〕━━╮
│  Premium command center
╰━━━━━━━━━━━━━━━━━━━━╯

✦ **SYSTEM**
`.status` / `.dashboard` — dashboard live
`.ping` / `.alive` — koneksi & runtime
`.help` — pusat bantuan
`.id` — identitas chat / user
`.restart` — mulai ulang bot

✦ **ACCOUNT TOOLS**
`.afk [alasan]` — aktifkan mode AFK
`.afk off` — nonaktifkan AFK
`.join <link/@username>` — bergabung ke chat
`.leave` — keluar dari grup saat ini

✦ **PROMOTION STUDIO**
`.gcast <teks>` — kirim ke grup yang sudah ada di dialog akun
Balas pesan + `.gcast` — salin pesan ke grup
`.bcstop` — hentikan broadcast
`.addbl [chat_id]` — blacklist grup
`.delbl [chat_id]` — hapus dari blacklist
`.listbl` — tampilkan blacklist
`.promo add <interval> <teks>` — jadwalkan promo di grup saat ini
Balas pesan + `.promo add <interval>` — jadwalkan salinan
`.promo list` — daftar jadwal
`.promo on|off|del <id|all>` — kelola jadwal
`.promo set <id> <interval>` — ubah interval

✦ **VOICE PLAYER** _(opsional)_
`.play <judul/link>` — putar audio
`.pause` · `.resume` · `.skip` · `.stop`
`.queue` — antrean · `.vol <1-200>` — volume

╭━━〔 **QUICK NOTES** 〕━━╮
• Interval promo minimal 60 detik.
• Promosikan hanya ke grup yang mengizinkan.
• Jangan bagikan `SESSION_STRING`.
╰━━━━━━━━━━━━━━━━━━━━╯
_PURUMI • Crafted for your workflow_'''

@app.on_message(cmd('help', 'menu'))
async def help_cmd(_, message):
    await message.edit(HELP)
