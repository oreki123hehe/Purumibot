# Purumi Userbot — Premium Command Center

Userbot Telegram berbasis Pyrogram dengan panel teks yang konsisten, dashboard runtime, alat akun, player voice chat opsional, dan Promotion Studio untuk grup yang mengizinkan promosi.

## ✦ Fitur

- **System dashboard:** `.status` / `.dashboard`, `.ping`, `.alive`
- **Account tools:** `.id`, `.afk`, `.join`, `.leave`, `.restart`
- **Promotion Studio:** `.gcast`, `.bcstop`, blacklist target, promo terjadwal per grup
- **Voice player opsional:** `.play`, `.pause`, `.resume`, `.skip`, `.stop`, `.queue`, `.vol`
- **Keamanan dasar:** file rahasia dan data runtime dikecualikan dari Git

## Setup

1. Salin `.env.example` menjadi `.env`.
2. Isi `API_ID` dan `API_HASH` dari https://my.telegram.org.
3. Jalankan `python gen_session.py`, lalu simpan hasilnya sebagai `SESSION_STRING` di `.env`.
4. Instal dependensi dan jalankan bot:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python main.py
```

Di Termux, gunakan `requirements-lite.txt` jika instalasi dependensi musik gagal.

## Promotion Studio

- `.gcast <teks>` — broadcast ke grup yang sudah ada di dialog akun
- Balas pesan dengan `.gcast` — salin pesan ke grup target
- `.bcstop` — hentikan broadcast
- `.addbl [chat_id]`, `.delbl [chat_id]`, `.listbl` — kelola blacklist
- `.promo add 5m <teks>` — promo berkala di grup tempat perintah dijalankan
- Balas pesan lalu `.promo add 5m` — jadwalkan salinan pesan
- `.promo list`, `.promo on 1`, `.promo off 1`, `.promo del 1`, `.promo set 1 10m`

Interval promo minimum 60 detik. Broadcast memiliki jeda minimal 3 detik. Gunakan hanya di grup yang mengizinkan promosi; jangan mengirim pesan yang tidak diminta. Telegram dapat membatasi akun atas aktivitas berulang atau spam.

## Rahasia & sesi

Jangan commit atau membagikan `.env`, `SESSION_STRING`, atau file `.session`. Atur environment variables secara aman di server/hosting. Gunakan akun cadangan dan tinjau izin bot sebelum menjalankan.

> UI premium di sini berupa panel teks Telegram yang konsisten; belum ada dashboard web terpisah. Kode belum diuji dengan kredensial Telegram nyata.
