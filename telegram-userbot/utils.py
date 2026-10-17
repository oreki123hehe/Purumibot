import time
from pyrogram import filters
import config

START_TIME = time.time()


def cmd(*names):
    """Filter perintah yang dikirim oleh akun sendiri, misalnya .ping."""
    return filters.me & filters.command(list(names), prefixes=config.PREFIXES)


def get_args(message):
    text = message.text or message.caption or ""
    parts = text.split(None, 1)
    return parts[1].strip() if len(parts) > 1 else ""


def fmt_uptime():
    seconds = int(time.time() - START_TIME)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    parts = []
    if days:
        parts.append(f"{days}h")
    if hours:
        parts.append(f"{hours}j")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}d")
    return " ".join(parts)
