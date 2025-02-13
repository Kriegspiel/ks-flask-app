import os
from forms import PrepareGameForm
from flask import render_template, redirect, request, url_for, session, flash
from flask import Blueprint
import random

from database import mongo
games = mongo.db.games
users = mongo.db.users

prepare_game_bp = Blueprint('prepare_game_bp', __name__, template_folder='templates')

@prepare_game_bp.route('/prepare_game', methods=['GET', 'POST'])
def prepare_game():
    form = PrepareGameForm()
    
    if request.method == 'GET':
        form['game_id'].data = __generate_new_game_id()
        return render_template('prepare_game.html', form=form)
    
    game_id = form["game_id"].data
    game = games.find_one({'game_id':game_id})
    if form['create'].data:
        if not game:
            # log.info(f'Create game selected {game_id}')
            return redirect(url_for('prepare_game_bp.create', game_id=game_id))
        else:
            form.game_id.errors = ["Game already exists."]
    elif form['connect'].data and form.validate_on_submit():
        if game:
            if not game["b_username"] or (session['username'] in [game['w_username'], game['b_username']]):
                # log.info(f'Connect to game {form["game_id"].data}')
                return redirect(url_for('prepare_game_bp.connect', game_id=game_id))
            else:
                form.game_id.errors = [f"Game '{game_id}' is already full. Select another game id."]
        else:
            form.game_id.errors = [f"Game '{game_id}' doesn't exists. Use Create button."]
    return render_template('prepare_game.html', form=form, game_id=game_id)

@prepare_game_bp.route('/create', methods=['GET', 'POST'])
def create():
    game_id = request.args.get('game_id')
    # log.info(f'Generated id: {game_id}')
    games.insert_one({
        'game_id': game_id,
        'w_username': session['username'],
        'b_username': None,
        'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
        'w_fen': '8/8/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
        'b_fen': 'rnbqkbnr/pppppppp/8/8/8/8/8/8 w KQkq - 0 1',
        'current_turn': 'w',
        'last_move_if_capture': None,
        'is_check': False,
        'winner_user': None,
        'is_finished': False
    })
    # log.info('Game was created')
    return redirect(url_for('prepare_game_bp.wait', game_id=game_id))

@prepare_game_bp.route('/connect', methods=['GET', 'POST'])
def connect():
    game_id = request.args.get('game_id')
    
    game = games.find_one({'game_id': game_id})
    if game:
        if session['username'] in [game['w_username'], game['b_username']] :
            flash('Game already started', 'danger')
            session['game_id'] = game_id
            return redirect(url_for('prepare_game_bp.wait', game_id=game_id))
        games.update_one({'game_id': game_id}, {'$set': {'b_username': session['username']}})
        session['game_id'] = game_id
        return redirect(url_for('game_bp.game_', game_id=game_id))

    flash('Game not found', 'danger')
    return redirect(url_for('prepare_game_bp.prepare_game', game_id=game_id, errors='Game not found'))

@prepare_game_bp.route('/wait')
def wait():
    # log.error(f'Wait opponent')

    game_id = request.args.get('game_id')
    # log.error(f'Wait opponent for game id: {game_id}')
    if not game_id:
        redirect(url_for('prepare_game_bp.prepare_game'))
    
    game = games.find_one({'game_id': game_id})
    # log.error(f'Game: {game}')
    if not game:
        # log.error(f'Game for game id: {game_id} was not found')
        flash('Game not found', 'danger')
        return redirect(url_for('prepare_game_bp.prepare_game'))
    if game['b_username']:
        session['game_id'] = game_id
        return redirect(url_for('game_bp.game_', game_id=game_id))
    return render_template('wait_opponent.html', game_id=game_id)

def __generate_new_game_id():
    new_game_id = random.randint(100000, 999999)
    while games.find_one({'game_id':new_game_id}):
        new_game_id = random.randint(100000, 999999)
    return new_game_id