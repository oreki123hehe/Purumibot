from core import app
from utils import cmd

HELP = """**📖 BANTUAN USERBOT**

**🏓 Umum**
`.ping` `.alive` `.help` `.id` `.afk [alasan]` `.afk off`
`.join <link/@username>` `.leave` `.restart`

**🎵 Musik (voice chat grup; opsional)**
`.play <judul/link>` atau balas audio dengan `.play`
`.pause` `.resume` `.skip` `.stop` `.queue` `.vol <1-200>`
"""


@app.on_message(cmd("help", "menu"))
async def help_cmd(_, message):
    await message.edit(HELP)
