import asyncio
from pyrogram.enums import ChatType
from pyrogram.errors import ChatWriteForbidden, UserBannedInChannel, ChannelPrivate, ChatAdminRequired, PeerIdInvalid, SlowmodeWait
from core import app
import config
import db
from utils import cmd, get_args, send_payload, parse_duration

tasks = {}
FATAL = (ChatWriteForbidden, UserBannedInChannel, ChannelPrivate, ChatAdminRequired, PeerIdInvalid)
HELP = ('Promo otomatis\n.promo add <interval> <teks> (di grup target)\nBalas pesan + .promo add <interval> untuk menyalin pesan itu\n.promo list | .promo on|off|del <id|all> | .promo set <id> <interval>\nInterval minimum: ' + str(config.MIN_PROMO_INTERVAL) + ' detik.')

async def _runner(client, job_id):
    failures = 0
    while True:
        job = db.data['promos'].get(str(job_id))
        if not job or not job.get('active'):
            break
        try:
            source = tuple(job['src']) if job.get('src') else None
            await send_payload(client, job['chat_id'], job.get('text'), source)
            job['sent'] = job.get('sent', 0) + 1
            job['last_error'] = None
            failures = 0
        except SlowmodeWait as exc:
            await asyncio.sleep(exc.value + 1)
            continue
        except FATAL as exc:
            job['active'] = False
            job['last_error'] = type(exc).__name__
            db.save()
            break
        except Exception as exc:
            failures += 1
            job['last_error'] = type(exc).__name__
            if failures >= 5:
                job['active'] = False
                db.save()
                break
        db.save()
        await asyncio.sleep(max(config.MIN_PROMO_INTERVAL, int(job['interval'])))
    tasks.pop(job_id, None)

def start_job(client, job_id):
    task = tasks.get(job_id)
    if task and not task.done():
        return
    tasks[job_id] = asyncio.create_task(_runner(client, job_id))

def stop_job(job_id):
    task = tasks.pop(job_id, None)
    if task:
        task.cancel()

async def restore():
    for key, job in db.data['promos'].items():
        if job.get('active'):
            start_job(app, int(key))

def _ids(value):
    if value.lower() == 'all':
        return [int(key) for key in db.data['promos']]
    if value.isdigit() and value in db.data['promos']:
        return [int(value)]
    return []

@app.on_message(cmd('promo'))
async def promo_cmd(client, message):
    raw = get_args(message)
    parts = raw.split(None, 1)
    sub = parts[0].lower() if parts else 'help'
    rest = parts[1].strip() if len(parts) > 1 else ''
    if sub == 'add':
        pieces = rest.split(None, 1)
        if not pieces:
            return await message.edit(HELP)
        interval = parse_duration(pieces[0])
        if interval is None or interval < config.MIN_PROMO_INTERVAL:
            return await message.edit('Interval tidak valid. Minimum ' + str(config.MIN_PROMO_INTERVAL) + ' detik. Contoh: 60, 5m, 1h.')
        remainder = pieces[1].strip() if len(pieces) > 1 else ''
        reply = message.reply_to_message
        source = [reply.chat.id, reply.id] if reply else None
        if not source and not remainder:
            return await message.edit('Isi teks promo atau balas pesan yang ingin dipromosikan.')
        if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
            return await message.edit('Jalankan .promo add dari grup target.')
        chat_id = message.chat.id
        title = (await client.get_chat(chat_id)).title or str(chat_id)
        job_id = int(db.data.get('next_id', 1))
        db.data['next_id'] = job_id + 1
        db.data.setdefault('promos', {})[str(job_id)] = {'id': job_id, 'chat_id': chat_id, 'title': title, 'text': None if source else remainder, 'src': source, 'interval': interval, 'active': True, 'sent': 0, 'last_error': None}
        db.save()
        start_job(client, job_id)
        return await message.edit(f'Promo #{job_id} aktif di {title}. Interval: {interval} detik.')
    if sub == 'list':
        promos = db.data.setdefault('promos', {})
        if not promos:
            return await message.edit('Belum ada promo terjadwal.')
        lines = ['Daftar promo']
        for job in promos.values():
            status = 'AKTIF' if job.get('active') else 'NONAKTIF'
            error = ' Error: ' + str(job['last_error']) if job.get('last_error') else ''
            lines.append(f"{status} #{job['id']} {job['title']} — tiap {job['interval']}s — terkirim {job.get('sent', 0)}{error}")
        return await message.edit('\n'.join(lines))
    if sub in ('on', 'off', 'del'):
        ids = _ids(rest)
        if not ids:
            return await message.edit('ID promo tidak ditemukan. Lihat .promo list.')
        for job_id in ids:
            job = db.data['promos'].get(str(job_id))
            if sub == 'del':
                stop_job(job_id)
                db.data['promos'].pop(str(job_id), None)
            elif sub == 'off':
                job['active'] = False
                stop_job(job_id)
            else:
                job['active'] = True
                job['last_error'] = None
                start_job(client, job_id)
        db.save()
        return await message.edit('Promo ' + ', '.join('#' + str(item) for item in ids) + ': ' + sub)
    if sub == 'set':
        pieces = rest.split()
        if len(pieces) != 2 or not pieces[0].isdigit() or pieces[0] not in db.data['promos']:
            return await message.edit('Gunakan: .promo set <id> <interval>')
        interval = parse_duration(pieces[1])
        if interval is None or interval < config.MIN_PROMO_INTERVAL:
            return await message.edit('Interval minimum ' + str(config.MIN_PROMO_INTERVAL) + ' detik.')
        db.data['promos'][pieces[0]]['interval'] = interval
        db.save()
        return await message.edit(f'Interval promo #{pieces[0]} diatur menjadi {interval} detik.')
    await message.edit(HELP)
