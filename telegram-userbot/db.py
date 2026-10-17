import copy
import json
import os

os.makedirs("data", exist_ok=True)
_PATH = os.path.join("data", "db.json")
_DEFAULT = {"promos": {}, "blacklist": [], "afk": None, "next_id": 1}


def _load():
    data = {}
    if os.path.exists(_PATH):
        try:
            with open(_PATH, "r", encoding="utf-8") as stream:
                data = json.load(stream)
        except (OSError, ValueError):
            data = {}
    for key, value in _DEFAULT.items():
        data.setdefault(key, copy.deepcopy(value))
    return data


data = _load()


def save():
    temp_path = _PATH + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
    os.replace(temp_path, _PATH)
