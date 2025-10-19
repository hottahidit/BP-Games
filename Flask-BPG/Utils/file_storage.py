import json
import os
from threading import Lock

DATA_FILE = os.path.join(os.path.dirname(__file__), "../instance/multiplayer_data.json")
lock = Lock()

def read_data():
    """Safely read the multiplayer data file."""
    with lock:
        if not os.path.exists(DATA_FILE):
            return {"rooms": {}, "users": {}}
        with open(DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"rooms": {}, "users": {}}

def write_data(data):
    """Safely write the multiplayer data file."""
    with lock:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

def update_user_progress(user_id, game_name, score=None, level=None):
    """Update or create a user's progress in the file."""
    data = read_data()
    user_key = str(user_id)
    user_data = data["users"].setdefault(user_key, {})
    game_data = user_data.setdefault(game_name, {})

    if score is not None:
        if game_name in ("minesweeper", "lightsout"):
            if "score" not in game_data or score < game_data["score"]:
                game_data["score"] = score
        else:
            if "score" not in game_data or score > game_data["score"]:
                game_data["score"] = score

    if level is not None:
        game_data["level"] = level

    write_data(data)
    return game_data

