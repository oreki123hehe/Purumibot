import asyncio
import importlib
import logging
import pkgutil
import config
from pyrogram import idle
from core import app, call
import plugins

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
log = logging.getLogger('userbot')


def load_plugins():
    loaded = 0
    for _, name, _ in pkgutil.iter_modules(plugins.__path__):
        try:
            importlib.import_module(f'plugins.{name}')
            loaded += 1
            log.info('Plugin dimuat: %s', name)
        except Exception:
            log.exception('Plugin %s gagal dimuat', name)
    log.info('Total plugin berhasil dimuat: %s', loaded)


async def main():
    if not config.API_ID or not config.API_HASH:
        raise SystemExit('API_ID / API_HASH belum diisi. Isi Environment Variables di hosting.')

    load_plugins()

    log.info('Memulai koneksi Telegram...')
    await app.start()
    call_started = False

    # PyTgCalls hanya diperlukan untuk fitur voice/music call.
    # Jika library/voice call gagal dimulai, userbot tetap berjalan untuk command lain.
    if call:
        try:
            await call.start()
            call_started = True
            log.info('PyTgCalls aktif.')
        except Exception:
            log.exception('PyTgCalls gagal dimulai; fitur voice/music call dinonaktifkan sementara.')

    try:
        try:
            from plugins.promo import restore
            await restore()
        except Exception:
            log.exception('Jadwal promo tidak dapat dipulihkan.')

        me = await app.get_me()
        log.info('Userbot aktif sebagai %s (id %s). Prefix command: %s',
                 me.first_name, me.id, ''.join(config.PREFIXES))
        await idle()
    finally:
        if call_started:
            try:
                await call.stop()
            except Exception:
                log.exception('Gagal menghentikan PyTgCalls dengan bersih.')
        await app.stop()


if __name__ == '__main__':
    asyncio.run(main())
