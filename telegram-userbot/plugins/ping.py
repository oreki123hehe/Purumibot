import platform
import time
from core import app
from utils import cmd, fmt_uptime

@app.on_message(cmd('ping'))
async def ping(_, message):
    started = time.perf_counter()
    await message.edit('╭━━〔 **NETWORK CHECK** 〕━━╮\n⏳ Mengukur respons...')
    latency = (time.perf_counter() - started) * 1000
    quality = 'EXCELLENT' if latency < 100 else 'STABLE' if latency < 300 else 'SLOW'
    await message.edit(
        '╭━━〔 🟢 **SYSTEM ONLINE** 〕━━╮\n'
        f'⚡ **Latency**  `{latency:.1f} ms` · {quality}\n'
        f'⏱ **Uptime**   `{fmt_uptime()}`\n'
        '╰━━━━━━━━━━━━━━━━━━╯\n'
        '_PURUMI • NETWORK MONITOR_'
    )

@app.on_message(cmd('alive'))
async def alive(client, message):
    me = await client.get_me()
    await message.edit(
        '╭━━〔 ✦ **PURUMI ONLINE** 〕━━╮\n'
        f'👤 **Account**  {me.first_name}\n'
        f'🐍 **Python**   `{platform.python_version()}`\n'
        f'⏱ **Uptime**   `{fmt_uptime()}`\n'
        '🟢 **Status**   All systems ready\n'
        '╰━━━━━━━━━━━━━━━━━━╯\n'
        '_YOUR PERSONAL TELEGRAM TOOLKIT_'
    )
