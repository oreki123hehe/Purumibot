# Telegram Userbot (Pyrogram)

Folder terpisah untuk userbot Telegram berbasis Pyrogram.

## Fitur
- `.ping` dan `.alive`
- `.help`, `.id`, `.afk`, `.join`, `.leave`, `.restart`
- Pemutar musik voice chat (opsional; memerlukan `py-tgcalls`)

Fitur broadcast massal dan promo berulang tidak disertakan dalam versi ini agar tidak mengotomatisasi pesan massal yang tidak diminta.

## Konfigurasi
1. Salin `.env.example` menjadi `.env`.
2. Isi `API_ID` dan `API_HASH` dari https://my.telegram.org.
3. Jalankan `python gen_session.py`, lalu simpan hasil `SESSION_STRING` ke `.env`.
4. Jangan commit `.env` atau file sesi. Jangan bagikan `SESSION_STRING`.

## Jalankan

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python main.py
```

Gunakan akun cadangan dan hormati aturan Telegram. Fitur musik mungkin memerlukan lingkungan Linux/VPS dengan FFmpeg.
