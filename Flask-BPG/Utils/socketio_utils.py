from flask_socketio import emit, join_room, leave_room, disconnect
from flask_login import current_user
from Logic.Snake import SnakeGame
from Utils.file_storage import read_data, write_data, update_user_progress
import time

active_snake_games = {}
active_snake_threads = {}
sid_to_userr = {}

def register_socketio_events(socketio):

    @socketio.on("join", namespace="/minesweeper")
    def join_game(data):
        if not current_user.is_authenticated:
            emit("error", {"message": "Authentication required"})
            return

        room = str(current_user.id)
        join_room(room)

        data_file = read_data()
        user_id = str(current_user.id)
        progress = data_file["users"].get(user_id, {}).get("minesweeper", {"score": 0, "level": 1})

        emit("player_joined", {
            "user": user_id,
            "progress": progress
        }, room=room)

    @socketio.on("update_progress")
    def update_progress(data):
        if not current_user.is_authenticated:
            emit("error", {"message": "Authentication required"})
            return

        game_name = data.get("game_name")
        score = data.get("score")
        level = data.get("level")

        updated = update_user_progress(current_user.id, game_name, score=score, level=level)
        emit("progress_saved", {"game": game_name, "progress": updated})

    @socketio.on("connect")
    def handle_connect(auth=None):
        from flask import request

        if not current_user.is_authenticated:
            emit("error", {"message": "Authentication required"})
            disconnect()
            return

        user_id = current_user.id
        sid = request.sid

        join_room(sid)
        sid_to_user[sid] = user_id

        print(f"[CONNECT] User {user_id} connected with sid {sid}")

        game = SnakeGame()
        active_snake_games[sid] = game

        emit("state", game.serialize(), room=sid)

        def snake_loop(current_sid):
            g = active_snake_games[current_sid]
            while current_sid in active_snake_games:
                time.sleep(g.tick_delay)
                g.tick()
                socketio.emit("state", g.serialize(), room=current_sid)


        active_snake_threads[sid] = socketio.start_background_task(snake_loop, sid)

    @socketio.on("change_dir")
    def change_dir(data):
        from flask import request
        sid = request.sid

        game = active_snake_games.get(sid)
        if not game:
            print(f"[WARN] No snake game for sid {sid}")
            return

        dx = int(data.get("dx", 0))
        dy = int(data.get("dy", 0))
        game.change_dir(dx, dy) 

    @socketio.on("disconnect")
    def handle_disconnect():
        if not current_user.is_authenticated:
            print("[INFO] Anonymous user disconnected")
            return

        user_id = current_user.id
        print(f"[DISCONNECT] Cleaning up user {user_id}")
        active_snake_games.pop(user_id, None)
        active_snake_threads.pop(user_id, None)
        disconnect()

 
