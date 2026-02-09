import json
import os

MEMORY_FILE = "/home/memory.json"


def _load():
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def _save(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f)


def add_message(role, content):
    data = _load()
    data.append({"role": role, "content": content})

    # keep only last 10 messages (token control + speed)
    data = data[-10:]

    _save(data)


def get_memory():
    return _load()


def clear_memory():
    _save([])
