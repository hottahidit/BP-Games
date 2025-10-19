from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from Utils.extra_utils import db, login_manager
from Utils.socketio_utils import register_socketio_events 
from Auth.models import User
from Auth.login import auth_bp
from Auth.admin import admin_bp
from Logic.minesweeper import Minesweeper
from Logic.brick_breaker import BrickBreakerGame
from Logic.LightsOut import LightsOutGame
from Logic.Snake import SnakeGame
from termcolor import colored as c
import random, sys, os, time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
app.config['SECRET_KEY'] = 'make-sure-you-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bpg-users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access the games. This is to track your scores.'

register_socketio_events(socketio)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')

mgrid = []
mrevealed = set()
mfirst_click_done = False

config_rows, config_cols, config_mines = 10, 10, 10  # default to Easy

bgame = BrickBreakerGame()
mgame = Minesweeper(config_rows, config_cols, config_mines)
lgame = LightsOutGame(config_rows, config_cols)
sgame = SnakeGame()
minesweeper_games = {}
lightsout_games = {}
snake_games = {}
snake_threads = {}

app.config["games"] = {
    "minesweeper": mgame,
    "brickbreaker": bgame,
    "lightsout": lgame,
    "snake": sgame
}

def snake_loop():
    global sgame
    while True:
        sgame.tick()
        socketio.emit('state', sgame.serialize())
        time.sleep(sgame.tick_delay)

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect('/dashboard')
    return render_template('home.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

#=========================== * Minesweeper * ===========================#
@app.route('/games/minesweeper')
@login_required
def minesweeper():
    return render_template('games/minesweeper.html')

@app.route('/games/minesweeper-info')
@login_required
def min_info():
    uid = current_user.id 
    if uid not in minesweeper_games:
        minesweeper_games[uid] = Minesweeper(config_rows, config_cols, config_mines)

        game = minesweeper_games[uid]
        return jsonify({'rows': mgame.rows, 'cols': mgame.cols, 'mines':mgame.mines})

@app.route('/games/minesweeper-reset')
@login_required
def min_reset():
    mode = request.args.get('mode', 'easy')
    if mode == 'easy':
        rows, cols, mines = 10, 10, 10
    elif mode == 'medium':
        rows, cols, mines = 18, 18, 40
    elif mode == 'hard':
        rows, cols, mines = 24, 24, 99
    else:
        rows, cols, mines = config_rows, config_cols, config_mines  

    uid = current_user.id
    minesweeper_games[uid] = Minesweeper(rows, cols, mines)
    return redirect('/games/minesweeper')

@app.route('/games/minesweeper-reveal')
@login_required
def min_reveal():
    r = int(request.args.get('row'))
    c = int(request.args.get('col'))
    print(r, c)
    uid = current_user.id
    
    if uid not in minesweeper_games:
        user_minesweeper_games[uid] = Minesweeper(config_rows, config_cols, config_mines)

    game = minesweeper_games[uid]
    data, game_over = game.reveal_cell(r, c)

    if game_over:
        data.append({'game_over': True})

    return jsonify(data)

#=========================== * Lights Out * ===========================#
@app.route('/games/lights-off')
@login_required
def lights_off():
    uid = current_user.id
    if uid not in lightsout_games:
        lightsout_games[uid] = LightsOutGame(5, 5)
    return render_template('games/LightsOut.html')


@app.route('/games/lights-off-config')
@login_required
def lights_off_config():
    uid = current_user.id
    game = lightsout_games.get(uid)
    if not game:
        game = LightsOutGame(5, 5)
        lightsout_games[uid] = game
    return jsonify({'rows': game.rows, 'cols': game.cols})


@app.route('/games/lights-off-reset')
@login_required
def lights_off_reset():
    uid = current_user.id
    mode = request.args.get('mode', 'easy')

    if mode == 'easy':
        rows, cols = 5, 5
    elif mode == 'medium':
        rows, cols = 8, 8
    elif mode == 'hard':
        rows, cols = 10, 10
    else:
        rows, cols = 5, 5

    lightsout_games[uid] = LightsOutGame(rows, cols)
    return jsonify(lightsout_games[uid].get_state())


@app.route('/games/lights-off-toggle', methods=['POST'])
@login_required
def lights_off_toggle():
    uid = current_user.id
    game = lightsout_games.get(uid)
    if not game:
        game = LightsOutGame(5, 5)
        lightsout_games[uid] = game

    r = int(request.json.get('row'))
    c = int(request.json.get('col'))
    game.toggle(r, c)
    return jsonify(game.get_state())

#=========================== * Brick Breaker * ===========================#
@app.route("/games/brickbreaker")
@login_required
def brickbreaker_page():
    return render_template("games/brick_breaker.html")

@app.route("/games/brickbreaker-state")
@login_required
def get_state():
    return jsonify(bgame.get_state())

@app.route("/games/brickbreaker-step")
@login_required
def step():
    bgame.step()
    return jsonify(bgame.get_state())

@app.route("/games/brickbreaker-move", methods=["POST"])
@login_required
def move_paddle():
    direction = request.json.get("direction")
    if direction == "left":
        bgame.paddle.move_left()
    elif direction == "right":
        bgame.paddle.move_right()
    return jsonify(bgame.get_state())

@app.route("/games/brickbreaker-reset")
@login_required
def reset():
    bgame.reset()
    return jsonify(bgame.get_state())

#=========================== * Snake * ===========================#
@app.route('/games/snake')
@login_required
def snake():
    return render_template('games/snake.html')

@socketio.on('connect')
def handle_connect(auth=None):
    if not current_user.is_authenticated:
        emit('error', {'message': 'Authentication required'})
        return

    uid = current_user.id
    join_room(str(uid))

    if uid not in snake_games:
        snake_games[uid] = SnakeGame()

    game = snake_games[uid]
    emit('state', game.serialize(), room=str(uid))

    if uid not in snake_threads:
        def snake_loop(user_id):
            while user_id in snake_games:
                game = snake_games[user_id]
                game.tick()
                socketio.emit('state', game.serialize(), room=str(user_id))
                time.sleep(game.tick_delay)

        snake_threads[uid] = socketio.start_background_task(snake_loop, uid)

@socketio.on('change_dir')
def change_dir(data):
    if not current_user.is_authenticated:
        return

    uid = current_user.id
    game = snake_games.get(uid)
    if not game:
        return

    dx = int(data.get('dx', 0))
    dy = int(data.get('dy', 0))
    game.change_dir(dx, dy)

@socketio.on('restart')
def restart():
    if not current_user.is_authenticated:
        return

    uid = current_user.id
    snake_games[uid] = SnakeGame()
    emit('state', snake_games[uid].serialize(), room=str(uid))

@socketio.on('disconnect')
def handle_disconnect():
    if not current_user.is_authenticated:
        return

    uid = current_user.id
    print(f"[DISCONNECT] Cleaning up user {uid}")
    snake_games.pop(uid, None)
    snake_threads.pop(uid, None)

def create_tables():
    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(username='z3n').first()
        if not admin:
            admin_user = User(
                username='z3n',
                email='z3n@bpgames.com',
                password_hash=generate_password_hash('z3n4z3n'),
                is_admin=True,
                is_approved=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin created - username: z3n, password: z3n4z3n")

if __name__ == '__main__':
    with app.app_context():
        create_tables()
    socketio.run(app, debug=True)
