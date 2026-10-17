import platform
import time
from core import app
from utils import cmd, fmt_uptime


@app.on_message(cmd("ping"))
async def ping(_, message):
    started = time.perf_counter()
    await message.edit("🏓 Pinging...")
    latency = (time.perf_counter() - started) * 1000
    await message.edit(f"🏓 **Pong!**\n⚡ Latensi: `{latency:.1f} ms`\n⏱ Uptime: `{fmt_uptime()}`")


@app.on_message(cmd("alive"))
async def alive(client, message):
    me = await client.get_me()
    await message.edit(
        "✅ **Userbot aktif**\n"
        f"👤 Akun: {me.first_name}\n"
        f"🐍 Python: `{platform.python_version()}`\n"
        f"⏱ Uptime: `{fmt_uptime()}`"
    )
