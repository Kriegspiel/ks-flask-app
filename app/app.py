import os
import logging
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from forms import RegistrationForm, LoginForm
import bcrypt
import chess

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers

# Конфигурация базы данных
mongo_username = os.environ.get('MONGO_USERNAME')
mongo_password = os.environ.get('MONGO_PASSWORD')
mongo_host = "mongo"
mongo_port = "27017"
mongo_db = "usersdb"

app.config['MONGO_URI'] = f"mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_db}"
mongo = PyMongo(app)
users = mongo.db.users

game = {
    'username': 'username',
    'opponent_username': 'opponent',
    'current_turn': 'username',
    'turn_color': 'white',
    'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
    'finished': False,
    'pgn': '',
    'message': ''
}

board = chess.Board(game['fen'])

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('chess'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        existing_user = users.find_one({'username': username})
        if existing_user:
            flash('Пользователь уже существует!')
            return redirect(url_for('register'))
        
        password = form.password.data
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        users.insert_one({'username': username, 'password': hashed_password})
        flash('Регистрация прошла успешно!')

        return redirect(url_for('login'))  # Перенаправляем на страницу входа
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Поиск пользователя в базе данных
        user = users.find_one({'username': username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['username'] = username
            return redirect(url_for('chess'))
        else:
            flash('Invalid username or password!')

    return render_template('game.html', title='Login', form=form)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/game')
def game():
    if 'username' not in session:
        flash('Please log in to play chess.', 'warning')
        return redirect(url_for('login'))
    
    game['username'] = session['username']
    game['current_turn'] = session['username']
    return render_template('game.html', title='Chess',
                           username=session['username'],
                           fen='8/8/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')

@app.route('/game/update_data', methods=['GET'])
def update_data():
    if 'username' not in session:
        flash('Please log in to play chess.', 'warning')
        return redirect(url_for('login'))
    
    return jsonify({
        'fen': game['fen'],
        'opponent_username': game['opponent_username'],
        'messages': ""
    })

@app.route('/game/move', methods=['GET'])
def game_move():
    if 'username' not in session:
        flash('Please log in to play chess.', 'warning')
        return redirect(url_for('login'))
    if game['finished']:
        return jsonify({'fen': game['fen'], 'message': 'Game finished.'})
    
    # if session['username'] != game['current_turn']:
    #     app.logger.info(f"Player {session['username']} tried to move out of turn.")
    #     return jsonify({'fen': game['fen'], 'message': 'Not your turn!'})
    
    move = chess.Move.from_uci(f"{request.args.get('source')}{request.args.get('target')}")
    if not move in board.legal_moves:
        return jsonify({'fen': game['fen'], 'message': f'Invalid move. Check: {board.is_check()} Checkmate: {board.is_checkmate()}'})
    board.push(move)
    board2 = chess.Board(board.fen())
    
    remove_color = chess.WHITE if game['turn_color'] == 'white' else chess.BLACK
    for square in chess.scan_reversed(board2.occupied_co[remove_color]):
        board2.remove_piece_at(square)

    game['turn_color'] = 'black' if game['turn_color'] == 'white' else 'white'
    game['current_turn'] = game['opponent_username'] if game['current_turn'] == game['username'] else game['username']
    game['fen'] = board2.fen()
    game['message'] = 'Player moved.'
    game['pgn'] = f"{request.args.get('source')} {request.args.get('target')}"
    return jsonify(game)

if __name__ == '__main__':
    app.run(debug=True)