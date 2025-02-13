from forms import RegistrationForm, LoginForm
from flask import render_template, redirect, url_for, session, flash
import bcrypt
from flask import Blueprint

from database import mongo
users = mongo.db.users

auth_bp = Blueprint('auth_bp', __name__, template_folder='templates')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = users.find_one({'username': username})
        if not user:
            form.username.errors = ["User doesn't exists!"]
        elif not bcrypt.checkpw(password.encode('utf-8'), user['password']):
            form.password.errors = ["Incorrect password!"]
        else:
            session['username'] = username
            return redirect(url_for('home'))

    return render_template('login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        existing_user = users.find_one({'username': username})
        if existing_user:
            form.username.errors = ["The user already exists!"]
            return render_template('register.html', form=form)
        
        password = form.password.data
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        users.insert_one({'username': username, 'password': hashed_password})
        flash('Registration was successful!')

        return redirect(url_for('auth_bp.login'))
    return render_template('register.html', form=form)

@auth_bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('auth_bp.login'))

# def auth_required(func):
#     def wrapper(func):
#         if not 'username' in session:
#             return redirect(url_for('auth_bp.login'))
#         func()
#     return wrapper