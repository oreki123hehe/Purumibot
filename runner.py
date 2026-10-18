"""Process supervisor sederhana untuk menjaga Purumi tetap berjalan.

Catatan: loop ini mengulang proses jika berhenti/crash, tetapi tidak dapat
mencegah platform hosting menidurkan atau menghentikan container.
"""
import os
import signal
import subprocess
import sys
import time
import logging

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger("purumi-supervisor")

stopping = False
child = None


def request_stop(signum, _frame):
    global stopping
    stopping = True
    log.info("Sinyal %s diterima; menghentikan Purumi...", signum)
    if child is not None and child.poll() is None:
        child.terminate()


signal.signal(signal.SIGTERM, request_stop)
signal.signal(signal.SIGINT, request_stop)

# Validasi konfigurasi agar tidak mengulang tanpa henti bila variabel wajib kosong.
if not os.getenv("API_ID") or not os.getenv("API_HASH"):
    log.error("API_ID dan API_HASH wajib diisi pada Environment Variables.")
    sys.exit(1)

delay = 5
max_delay = 60

while not stopping:
    log.info("Menjalankan Purumi (main.py)...")
    try:
        child = subprocess.Popen([sys.executable, "-u", "main.py"])
        code = child.wait()
    except Exception:
        log.exception("Gagal menjalankan main.py")
        code = 1

    child = None
    if stopping:
        break

    if code == 0:
        log.warning("Purumi berhenti normal; akan dicoba jalankan lagi dalam 5 detik.")
        delay = 5
    else:
        log.error("Purumi keluar dengan kode %s; restart dalam %s detik.", code, delay)

    # if/else menjaga jeda restart bertahap untuk menghindari crash loop cepat.
    wait_until = time.monotonic() + delay
    while not stopping and time.monotonic() < wait_until:
        time.sleep(min(1, max(0, wait_until - time.monotonic())))

    if code != 0:
        delay = min(delay * 2, max_delay)

log.info("Supervisor Purumi selesai.")
