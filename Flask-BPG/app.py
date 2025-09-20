from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from extra_utils import db, login_manager
#from Auth.models import User
#from Auth.login import auth_bp
#from Auth.admin import admin_bp
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

from Auth.models import User
from Auth.login import auth_bp
from Auth.admin import admin_bp

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')

mgrid = []
mrevealed = set()
mfirst_click_done = False

config_rows, config_cols, config_mines = 10, 10, 10  # default to Easy

mgame = Minesweeper(config_rows, config_cols, config_mines)
bgame = BrickBreakerGame()
lgame = LightsOutGame(config_rows, config_cols)
sgame = SnakeGame()

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

#=========================== * MINESWEEPER * ===========================#
@app.route('/minesweeper')
@login_required
def minesweeper():
    return render_template('minesweeper.html')

@app.route('/minesweeper-info')
@login_required
def min_info():
    return jsonify({'rows': mgame.rows, 'cols': mgame.cols, 'mines':mgame.mines})

@app.route('/minesweeper-reset')
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
        rows, cols, mines = config_rows, config_cols, config_mines  # fallback to custom/default
    global mgame
    mgame = Minesweeper(rows, cols, mines)
    return redirect('/minesweeper')

@app.route('/minesweeper-reveal')
@login_required
def min_reveal():
    r = int(request.args.get('row'))
    c = int(request.args.get('col'))
    print(r, c)

    data, game_over = mgame.reveal_cell(r, c)

    if game_over:
        data.append({'game_over': True})

    return jsonify(data)

#=========================== * LIGHTS OUT * ===========================#
@app.route('/lights-off')
@login_required
def lights_off():
    return render_template('LightsOut.html')

@app.route('/lights-off-config')
@login_required
def lights_off_config():
    return jsonify({'rows': lgame.rows, 'cols': lgame.cols})

@app.route('/lights-off-reset')
@login_required
def lights_off_reset():
    mode = request.args.get('mode', 'easy')
    if mode == 'easy':
        rows, cols = 5, 5
    elif mode == 'medium':
        rows, cols = 8, 8
    elif mode == 'hard':
        rows, cols = 10, 10
    else:
        rows, cols = config_rows, config_cols
    global lgame
    lgame = LightsOutGame(rows, cols)
    return jsonify(lgame.get_state())

@app.route('/lights-off-toggle', methods=['POST'])
@login_required
def lights_off_toggle():
    r = int(request.json.get('row'))
    c = int(request.json.get('col'))
    lgame.toggle(r, c)
    return jsonify(lgame.get_state())

#=========================== * BRICK BREAKER * ===========================#
@app.route("/brickbreaker")
@login_required
def brickbreaker_page():
    return render_template("brick_breaker.html")

@app.route("/brickbreaker-state")
@login_required
def get_state():
    return jsonify(bgame.get_state())

@app.route("/brickbreaker-step")
@login_required
def step():
    bgame.step()
    return jsonify(bgame.get_state())

@app.route("/brickbreaker-move", methods=["POST"])
@login_required
def move_paddle():
    direction = request.json.get("direction")
    if direction == "left":
        bgame.paddle.move_left()
    elif direction == "right":
        bgame.paddle.move_right()
    return jsonify(bgame.get_state())

@app.route("/brickbreaker-reset")
@login_required
def reset():
    bgame.reset()
    return jsonify(bgame.get_state())

#=========================== * Snake * ===========================#
@app.route('/snake')
@login_required
def snake():
    return render_template('snake.html')

@socketio.on('connect')
def handle_connect(auth=None):
    if current_user.is_authenticated:
        emit('state', sgame.serialize())
        socketio.start_background_task(snake_loop)
    else:
        emit('error', {'message': 'Authentication required'})

@socketio.on('change_dir')
def change_dir(data):
    if current_user.is_authenticated:
        global sgame
        dx = int(data.get('dx', 0))
        dy = int(data.get('dy', 0))
        sgame.change_dir(dx, dy)

@socketio.on('restart')
def restart():
    if current_user.is_authenticated:
        global sgame
        sgame = SnakeGame()
        emit('state', sgame.serialize())

def create_tables():
    with app.app_context():
        db.create_all()

        # Create default admin if doesn't exist
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
    create_tables()
    socketio.run(app, debug=True)
