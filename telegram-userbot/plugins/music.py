import asyncio
import os
import re
from pyrogram import filters
from core import app, call

if call is None:
    raise RuntimeError("py-tgcalls tidak terpasang, fitur musik nonaktif")

from yt_dlp import YoutubeDL
from pytgcalls import filters as fl
from pytgcalls.types import MediaStream
import config
from utils import cmd, get_args

os.makedirs("downloads", exist_ok=True)
URL_RE = re.compile(r"https?://")
queues = {}


def _fetch(query):
    target = query if URL_RE.match(query) else f"ytsearch1:{query}"
    options = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "noplaylist": True, "quiet": True, "no_warnings": True, "geo_bypass": True,
    }
    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(target, download=False)
        if "entries" in info:
            entries = [entry for entry in info["entries"] if entry]
            if not entries:
                raise ValueError("Lagu tidak ditemukan")
            info = entries[0]
        if (info.get("duration") or 0) > config.MAX_DURATION:
            raise ValueError(f"Durasi melebihi batas {config.MAX_DURATION // 60} menit")
        info = ydl.extract_info(info.get("webpage_url") or info["url"], download=True)
        path = ydl.prepare_filename(info)
    return {
        "title": info.get("title", "Tanpa judul"),
        "path": path,
        "duration": info.get("duration") or 0,
        "url": info.get("webpage_url", ""),
    }


def _duration(seconds):
    return f"{seconds // 60}:{seconds % 60:02d}" if seconds else "?"


def _cleanup(track):
    if track.get("local"):
        return
    path = track["path"]
    if any(item["path"] == path for queue in queues.values() for item in queue):
        return
    try:
        os.remove(path)
    except OSError:
        pass


async def _play_current(chat_id):
    track = queues[chat_id][0]
    await call.play(chat_id, MediaStream(track["path"], video_flags=MediaStream.Flags.IGNORE))


async def _next(chat_id):
    queue = queues.get(chat_id)
    if not queue:
        return None
    _cleanup(queue.pop(0))
    if not queue:
        queues.pop(chat_id, None)
        try:
            await call.leave_call(chat_id)
        except Exception:
            pass
        return None
    await _play_current(chat_id)
    return queue[0]


async def _clear(chat_id):
    for track in queues.pop(chat_id, []):
        _cleanup(track)
    try:
        await call.leave_call(chat_id)
    except Exception:
        pass


@app.on_message(cmd("play") & filters.group)
async def play(_, message):
    query = get_args(message)
    reply = message.reply_to_message
    status = await message.edit("🔎 Memproses...")
    try:
        if not query and reply and (reply.audio or reply.voice or reply.video or reply.document):
            path = await reply.download(file_name="downloads/")
            media = reply.audio or reply.voice or reply.video or reply.document
            track = {
                "title": getattr(media, "title", None) or getattr(media, "file_name", None) or "Audio",
                "path": path,
                "duration": getattr(media, "duration", 0) or 0,
                "url": "",
                "local": True,
            }
        elif query:
            track = await asyncio.get_running_loop().run_in_executor(None, _fetch, query)
        else:
            return await status.edit("Gunakan: `.play <judul lagu / link>` atau balas file audio.")
    except Exception as exc:
        return await status.edit(f"❌ Gagal mengambil lagu: `{type(exc).__name__}: {exc}`")

    chat_id = message.chat.id
    queue = queues.setdefault(chat_id, [])
    queue.append(track)
    if len(queue) == 1:
        try:
            await _play_current(chat_id)
        except Exception as exc:
            queue.pop()
            if not queue:
                queues.pop(chat_id, None)
            if "NoActiveGroupCall" in type(exc).__name__:
                return await status.edit("❌ Voice chat belum dimulai. Mulai voice chat di grup dulu, lalu ulangi `.play`.")
            return await status.edit(f"❌ Gagal memutar: `{type(exc).__name__}: {exc}`")
        await status.edit(f"▶️ **Memutar**\n🎵 {track['title']}\n⏱ {_duration(track['duration'])}")
    else:
        await status.edit(f"➕ **Masuk antrean #{len(queue) - 1}**\n🎵 {track['title']}")


@app.on_message(cmd("pause") & filters.group)
async def pause(_, message):
    try:
        await call.pause(message.chat.id)
        await message.edit("⏸ Dijeda.")
    except Exception as exc:
        await message.edit(f"❌ `{type(exc).__name__}`")


@app.on_message(cmd("resume") & filters.group)
async def resume(_, message):
    try:
        await call.resume(message.chat.id)
        await message.edit("▶️ Dilanjutkan.")
    except Exception as exc:
        await message.edit(f"❌ `{type(exc).__name__}`")


@app.on_message(cmd("skip") & filters.group)
async def skip(_, message):
    if not queues.get(message.chat.id):
        return await message.edit("Tidak ada lagu yang diputar.")
    try:
        next_track = await _next(message.chat.id)
    except Exception as exc:
        return await message.edit(f"❌ `{type(exc).__name__}`")
    await message.edit(
        f"⏭ Lanjut: **{next_track['title']}**" if next_track
        else "⏹ Antrean habis, keluar dari voice chat."
    )


@app.on_message(cmd("stop", "end") & filters.group)
async def stop(_, message):
    await _clear(message.chat.id)
    await message.edit("⏹ Dihentikan & keluar dari voice chat.")


@app.on_message(cmd("queue") & filters.group)
async def queue_cmd(_, message):
    queue = queues.get(message.chat.id)
    if not queue:
        return await message.edit("Antrean kosong.")
    lines = [f"▶️ **{queue[0]['title']}** ({_duration(queue[0]['duration'])})"]
    lines += [f"`{index}.` {track['title']}" for index, track in enumerate(queue[1:], 1)]
    await message.edit("🎶 **Antrean**\n" + "\n".join(lines))


@app.on_message(cmd("vol", "volume") & filters.group)
async def volume(_, message):
    arg = get_args(message)
    if not arg.isdigit() or not 1 <= int(arg) <= 200:
        return await message.edit("Gunakan: `.vol <1-200>`")
    try:
        await call.change_volume_call(message.chat.id, int(arg))
        await message.edit(f"🔊 Volume: `{arg}`")
    except Exception as exc:
        await message.edit(f"❌ `{type(exc).__name__}`")


@call.on_update(fl.stream_end())
async def on_stream_end(_, update):
    try:
        await _next(update.chat_id)
    except Exception:
        queues.pop(update.chat_id, None)


try:
    from pytgcalls.types import ChatUpdate

    @call.on_update(fl.chat_update(
        ChatUpdate.Status.CLOSED_VOICE_CHAT | ChatUpdate.Status.KICKED | ChatUpdate.Status.LEFT_GROUP
    ))
    async def on_chat_closed(_, update):
        for track in queues.pop(update.chat_id, []):
            _cleanup(track)
except Exception:
    pass
