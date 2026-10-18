import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv('API_ID', '0') or 0)
API_HASH = os.getenv('API_HASH', '')
SESSION_STRING = os.getenv('SESSION_STRING', '')
PREFIXES = list(os.getenv('PREFIX', '.')) or ['.']
MIN_PROMO_INTERVAL = max(60, int(os.getenv('MIN_PROMO_INTERVAL', '60')))
BC_DELAY = max(3.0, float(os.getenv('BC_DELAY', '5')))
MAX_DURATION = int(os.getenv('MAX_DURATION', '3600'))
