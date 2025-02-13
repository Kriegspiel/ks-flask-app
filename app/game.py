from flask import render_template, redirect, request, url_for, session, flash, jsonify
from flask import Blueprint
import chess


from database import mongo
games = mongo.db.games

game_bp = Blueprint('game_bp', __name__, template_folder='templates')
# from flask import current_app
# log = current_app.logger

@game_bp.route('/game', methods = ['GET'])
def game_():
    if 'username' not in session: return redirect(url_for('home'))    
    if 'game_id' not in session : return redirect(url_for('prepare_game_bp.create_game'))
    
    game_bp.logger.error(f"Game init {session['game_id']}")
    game = games.find_one({'game_id': session['game_id']})
    if not game:
        game_bp.logger.error(f"Game {session['game_id']} was not found. Deleted?") 
        return redirect(url_for('home'))
    
    return render_template('game.html', 
                            game_id=game['game_id'],
                            w_username=game['w_username'],
                            b_username=game['b_username'],
                            current_turn = game['current_turn'])

@game_bp.route('/game/update_data', methods = ['GET'])
def update_data():
    if 'username' not in session: return redirect(url_for('home'))    
    if 'game_id' not in session : return redirect(url_for('prepare_game_bp.create_game'))
    game = games.find_one({'game_id': session['game_id']})
    if not game:
        game_bp.logger.error(f"Game {session['game_id']} was not found. Deleted?") 
        return redirect(url_for('home'))

    return __json_for_user(session['username'], game)

@game_bp.route('/game/move', methods = ['GET'])
def game_move():
    if 'username' not in session: return redirect(url_for('home'))    
    if 'game_id' not in session: return redirect(url_for('prepare_game_bp.create_game'))
    
    game = games.find_one({'game_id': session['game_id']})
    if not game:
        # log.error(f"Game {session['game_id']} was not found. Deleted?") 
        return redirect(url_for('home'))

    board = chess.Board(game['fen'])

    # Check move
    move = chess.Move.from_uci(f"{request.args.get('source')}{request.args.get('target')}")
    if not move in board.legal_moves:
        game_bp.logger.error(f"Incorrect move: {request.args.get('source')} - {request.args.get('target')}")
        game_bp.logger.error(f"FEN: {game['fen']}")
        return __json_for_user(session['username'], game, move_status="move was rejected")

    game['last_move_if_capture'] = None
    game['captured_figure'] = None
    if board.is_capture(move):
        game['last_move_if_capture'] = request.args.get('target')
        square = chess.parse_square(request.args.get('target'))
        game['captured_figure'] = chess.piece_name(board.piece_type_at(square))

    # Update board
    board.push(move)
    game['fen'] = board.fen()
    
    # Board for white user
    w_board = chess.Board(board.fen())
    for square in chess.scan_reversed(w_board.occupied_co[chess.BLACK]):
        w_board.remove_piece_at(square)
    game['w_fen'] = w_board.fen()

    # Board for black user
    b_board = chess.Board(board.fen())
    for square in chess.scan_reversed(b_board.occupied_co[chess.WHITE]):
        b_board.remove_piece_at(square)
    game['b_fen'] = b_board.fen()

    # Change move
    game['current_turn'] = 'b' if game['current_turn'] == 'w' else 'w'

    # Check game status
    game["is_check"] = board.is_check()
    if board.is_checkmate():
        game["is_finished"] = True
        game["winner_user"] = session["username"]

    games.update_one({'game_id': session['game_id']}, 
        {'$set': {
            'fen': game['fen'],
            'w_fen': game['w_fen'],
            'b_fen': game['b_fen'],
            'current_turn': game['current_turn'],
            'last_move_if_capture': game['last_move_if_capture'],
            'captured_figure': game['captured_figure'],
            'is_check': game["is_check"],
            'winner_user': game["winner_user"],
            'is_finished': game["is_finished"]
        }
    })

    return __json_for_user(session['username'], game, move_status="move was applied")

# -------------------------
# Helper functions
# -------------------------
def __json_for_user(username, game, move_status=""):
    current_fen = game['w_fen'] if username == game['w_username'] else game['b_fen']
    if game["is_finished"]:
        current_fen = game['fen']

    game_bp.logger.error(f"Render {current_fen} for user {username}")
    return jsonify(
        game_id=game['game_id'],
        w_username=game['w_username'],
        b_username=game['b_username'],
        username=username,
        current_turn_status = __get_turn_status(username, game),
        fen=current_fen,
        move_status=move_status)

def __get_turn_status(username, game):
    if not game["is_finished"]:
        current_turn_user = game["w_username"] if game["current_turn"] == "w" else game["b_username"]
        check_msg = "Check." if game["is_check"] else ""
        capture = ""
        if game["last_move_if_capture"]:
            capture = f"{game['captured_figure']} in {game['last_move_if_capture']} was captured."
        if username == current_turn_user:
            return f"It's your turn. {check_msg} {capture}"
        else:
            return f"Waiting for opponents turn. {check_msg} {capture}"
    else:
        return f"It's checkmate! {game['winner_user']} is the winner!"
    