# Purumibot — Telegram Userbot

Userbot Telegram berbasis Pyrogram dengan panel perintah, alat akun, broadcast terkontrol, promosi terjadwal, dan pemutar voice chat opsional.

## Fitur
- Status: `.status`, `.dashboard`, `.ping`, `.alive`
- Akun: `.id`, `.afk`, `.join`, `.leave`, `.restart`
- Broadcast: `.gcast`, `.bcstop`, blacklist target
- Promosi terjadwal: `.promo add/list/on/off/del/set`
- Musik voice chat: `.play`, `.pause`, `.resume`, `.skip`, `.stop`, `.queue`, `.vol`

## Konfigurasi lokal
1. Salin `.env.example` menjadi `.env`.
2. Isi `API_ID` dan `API_HASH` dari [my.telegram.org](https://my.telegram.org).
3. Buat session secara lokal dengan `python gen_session.py`, lalu simpan hasilnya sebagai `SESSION_STRING` di environment lokal/server.
4. Instal Python 3.11, FFmpeg, lalu dependensi:

```bash
pip install -r requirements.txt
python main.py
```

## Deploy dengan Docker/Koyeb
- Repository root ini sudah menjadi direktori aplikasi; pilih branch `main` dan gunakan **Dockerfile** di root.
- Tambahkan `API_ID`, `API_HASH`, dan `SESSION_STRING` sebagai environment variables/secrets di dashboard hosting. Opsional: `PREFIX`, `MIN_PROMO_INTERVAL`, `BC_DELAY`, `MAX_DURATION`.
- Jangan menaruh kredensial asli di GitHub. Jangan commit file `.env`, session Telegram, atau data runtime.
- Pemutar voice chat memerlukan dukungan `py-tgcalls`, FFmpeg, dan koneksi yang stabil. Pastikan jenis service dan paket hosting mendukung proses worker yang berjalan terus-menerus. Paket gratis dapat memiliki batasan tidur, CPU, memori, dan durasi proses; deploy tidak otomatis menjamin bot musik 24/7.

## Keamanan
Gunakan akun cadangan dan hormati aturan Telegram. Broadcast/promosi hanya ke grup yang mengizinkan pesan tersebut; pengiriman berulang dapat memicu pembatasan akun.

UI saat ini berupa panel teks Telegram, bukan dashboard web terpisah. Kode tetap perlu diuji dengan akun dan konfigurasi runtime milikmu.
