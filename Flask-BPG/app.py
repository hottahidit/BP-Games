from flask import Flask, request, jsonify, render_template, redirect, url_for
from minesweeper import Minesweeper
from brick_breaker import BrickBreakerGame
from termcolor import colored as c
import random
import sys

app = Flask(__name__)

grid = []
revealed = set()
first_click_done = False

def ask_custom_config():
    use_custom = input("Use custom config? (y/n): ").strip().lower()
    if use_custom == 'y':
        rows = int(input("Rows: "))
        cols = int(input("Cols: "))
        mines = int(input("Mines: "))
        return rows, cols, mines
    return None

custom_config = ask_custom_config()
if custom_config:
    config_rows, config_cols, config_mines = custom_config
else:
    config_rows, config_cols, config_mines = 10, 10, 10  # default to Easy

mgame = Minesweeper(config_rows, config_cols, config_mines)
bgame = BrickBreakerGame()

@app.route('/')
def home():
    return render_template('index.html')

#===================== * MINESWEEPER * =========================#
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

if __name__ == '__main__':
    app.run(debug=True)

