import os
import logging
from flask import Flask, redirect, url_for, session, render_template
from bson.objectid import ObjectId
from forms import RegistrationForm, LoginForm


# Init app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

# Fix logs from gunicorn
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers

# Init database
import database
database.mongo.init_app(app, uri=database.get_db_uri("ks_db"))
users = database.mongo.db.users
errors_logs = database.mongo.db.errors_logs

from auth import auth_bp
app.register_blueprint(auth_bp)

from prepare_game import prepare_game_bp
app.register_blueprint(prepare_game_bp)
prepare_game_bp.logger = app.logger

from game import game_bp
app.register_blueprint(game_bp)
game_bp.logger = app.logger

@app.route('/')
def home():
    if 'username' in session:
        if users.find_one({'username': session['username']}):
            return redirect(url_for('prepare_game_bp.prepare_game'))
        session.pop('username', None)
    if 'game_id' in session:
        session.pop('game_id', None)
    return redirect(url_for('auth_bp.login'))

@app.errorhandler(500)
def internal_error(error):
    import datetime
    errors_logs.insert_one({'time': datetime.datetime.now().strftime("%Y.%m.%d %H:%M"),
                            'user': session['username'],
                            'game': session['game_id'],
                            'error': str(error)})
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)