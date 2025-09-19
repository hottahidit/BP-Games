from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_socketio import SocketIO,emit
from minesweeper import Minesweeper
from brick_breaker import BrickBreakerGame
from LightsOut import LightsOutGame
from Snake import SnakeGame
from termcolor import colored as c
import random
import sys
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

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
    return render_template('index.html')

#=========================== * MINESWEEPER * ===========================#
@app.route('/minesweeper')
def minesweeper():
    return render_template('minesweeper.html')

@app.route('/minesweeper-info')
def min_info():
    return jsonify({'rows': mgame.rows, 'cols': mgame.cols, 'mines':mgame.mines})

@app.route('/minesweeper-reset')
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
def lights_off():
    return render_template('LightsOut.html')

@app.route('/lights-off-config')
def lights_off_config():
    return jsonify({'rows': lgame.rows, 'cols': lgame.cols})

@app.route('/lights-off-reset')
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
def lights_off_toggle():
    r = int(request.json.get('row'))
    c = int(request.json.get('col'))
    lgame.toggle(r, c)
    return jsonify(lgame.get_state())

#=========================== * BRICK BREAKER * ===========================#
@app.route("/brickbreaker")
def brickbreaker_page():
    return render_template("brick_breaker.html")

@app.route("/brickbreaker-state")
def get_state():
    return jsonify(bgame.get_state())

@app.route("/brickbreaker-step")
def step():
    bgame.step()
    return jsonify(bgame.get_state())

@app.route("/brickbreaker-move", methods=["POST"])
def move_paddle():
    direction = request.json.get("direction")
    if direction == "left":
        bgame.paddle.move_left()
    elif direction == "right":
        bgame.paddle.move_right()
    return jsonify(bgame.get_state())

@app.route("/brickbreaker-reset")
def reset():
    bgame.reset()
    return jsonify(bgame.get_state())

#=========================== * Snake * ===========================#
@app.route('/snake')
def snake():
    return render_template('snake.html')

@socketio.on('connect')
def handle_connect(auth=None):
    emit('state', sgame.serialize())
    socketio.start_background_task(snake_loop)

@socketio.on('change_dir')
def change_dir(data):
    global sgame
    dx = int(data.get('dx', 0))
    dy = int(data.get('dy', 0))
    sgame.change_dir(dx, dy)

@socketio.on('restart')
def restart():
    global sgame
    sgame = SnakeGame()
    emit('state', sgame.serialize())

if __name__ == '__main__':
    socketio.run(app, debug=True)

