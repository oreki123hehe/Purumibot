import asyncio
import importlib
import logging
import pkgutil

import config
from pyrogram import idle
from core import app, call
import plugins

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("userbot")


def load_plugins():
    for _, name, _ in pkgutil.iter_modules(plugins.__path__):
        try:
            importlib.import_module(f"plugins.{name}")
            log.info("Plugin dimuat: %s", name)
        except Exception as exc:
            log.warning("Plugin '%s' dilewati: %s", name, exc)


async def main():
    if not config.API_ID or not config.API_HASH:
        raise SystemExit("API_ID / API_HASH belum diisi. Salin .env.example menjadi .env lalu isi.")
    load_plugins()
    await app.start()
    if call:
        await call.start()
    me = await app.get_me()
    log.info("Userbot aktif sebagai %s (id %s). Ketik .help", me.first_name, me.id)
    try:
        await idle()
    finally:
        if call:
            await call.stop()
        await app.stop()


if __name__ == "__main__":
    asyncio.run(main())
