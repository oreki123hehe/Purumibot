import re
import time
from pyrogram import filters
import config

START_TIME = time.time()

def cmd(*names):
    return filters.me & filters.command(list(names), prefixes=config.PREFIXES)

def get_args(message):
    text = message.text or message.caption or ''
    parts = text.split(None, 1)
    return parts[1].strip() if len(parts) > 1 else ''

def fmt_uptime():
    seconds = int(time.time() - START_TIME)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    parts = []
    if days: parts.append(f'{days}h')
    if hours: parts.append(f'{hours}j')
    if minutes: parts.append(f'{minutes}m')
    parts.append(f'{seconds}d')
    return ' '.join(parts)

def parse_duration(value):
    match = re.fullmatch(r'(\d+)\s*([smhd]?)', value.strip().lower())
    if not match: return None
    amount = int(match.group(1))
    scale = {'': 1, 's': 1, 'm': 60, 'h': 3600, 'd': 86400}[match.group(2)]
    seconds = amount * scale
    return seconds if seconds > 0 else None

async def send_payload(client, chat_id, text=None, source=None):
    if source:
        source_chat, source_message_id = source
        return await client.copy_message(chat_id=chat_id, from_chat_id=source_chat, message_id=source_message_id)
    if not text: raise ValueError('Pesan kosong')
    return await client.send_message(chat_id, text, disable_web_page_preview=True)
