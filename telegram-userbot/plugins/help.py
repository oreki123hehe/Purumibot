from core import app
from utils import cmd

HELP = """**📖 BANTUAN USERBOT**

**🏓 Umum**
`.ping` `.alive` `.help` `.id` `.afk [alasan]` `.afk off`
`.join <link/@username>` `.leave` `.restart`

**📢 Promosi grup**
`.gcast <teks>` — kirim ke grup yang terdaftar di dialog akun
Balas pesan lalu `.gcast` — salin pesan ke grup
`.bcstop` — hentikan broadcast
`.addbl [chat_id]`, `.delbl [chat_id]`, `.listbl` — blacklist target
`.promo add <interval> <teks>` — promo berkala di grup saat ini
Balas pesan lalu `.promo add <interval>` untuk menjadwalkan salinan
`.promo list`, `.promo on|off|del <id|all>`, `.promo set <id> <interval>`

**🎵 Musik (voice chat; opsional)**
`.play <judul/link>` atau balas audio dengan `.play`
`.pause` `.resume` `.skip` `.stop` `.queue` `.vol <1-200>`

Hormati aturan grup dan jangan mengirim promosi tanpa izin. Interval terlalu cepat dapat menyebabkan pembatasan akun.
"""


@app.on_message(cmd("help", "menu"))
async def help_cmd(_, message):
    await message.edit(HELP)
