"""Generate a Pyrogram SESSION_STRING. Keep it private."""
from pyrogram import Client

api_id = int(input("API_ID   : ").strip())
api_hash = input("API_HASH : ").strip()

with Client("gen", api_id=api_id, api_hash=api_hash, in_memory=True) as client:
    session_string = client.export_session_string()
    print("\nSESSION_STRING (jangan dibagikan):\n")
    print(session_string)
    print("\nSimpan di .env pada variabel SESSION_STRING.")
