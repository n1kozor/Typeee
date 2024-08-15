from datetime import datetime

from flask import Blueprint, render_template, url_for, flash, redirect, request, jsonify, session
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import User
from app.game import Game
from app.forms import RegistrationForm, LoginForm
from app.game_manager import GameSessionManager, UserManager, GameLogic
from app.auth_manager import AuthManager

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        if AuthManager.login_user(form):
            return redirect(url_for('main.dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@main.route('/start-timer', methods=['POST'])
def start_timer():
    session['start_time'] = datetime.now().timestamp()  # Tárolás UNIX timestamp-ként (float)
    return jsonify({'status': 'Timer started', 'start_time': session['start_time']})


@main.route('/check-time', methods=['POST'])
def check_time():
    client_elapsed_time = float(request.json['client_elapsed_time'])

    if 'start_time' not in session:
        return jsonify({'error': 'Timer not started'}), 400

    server_time = datetime.now().timestamp()
    server_start_time = session['start_time']  # Már floatként van tárolva
    server_elapsed_time = server_time - server_start_time

    time_difference = abs(server_elapsed_time - client_elapsed_time)

    if time_difference > 2:  # Például 2 másodperc eltérésnél figyelmeztetünk
        return jsonify({'status': 'cheating', 'time_difference': time_difference}), 200
    else:
        return jsonify({'status': 'ok', 'time_difference': time_difference}), 200



@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        AuthManager.register_user(form)
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)


@main.route("/dashboard")
@login_required
def dashboard():
    UserManager.update_user_score()
    GameSessionManager.reset_session()

    leaderboard = User.query.order_by(User.points.desc()).limit(10).all()

    return render_template('dashboard.html', title='Dashboard', leaderboard=leaderboard)

@main.route("/reset", methods=['POST'])
def reset_game():
    GameSessionManager.reset_session()
    return '', 204


@main.route('/reset-session', methods=['POST'])
def reset_session():
    session.clear()  # Töröljük a session adatait
    return redirect(url_for('dashboard'))  # Visszairányítás a dashboardra

@main.route("/rules")
@login_required
def rules():
    return render_template('rules.html', title='Rules')

@main.route("/play", methods=['GET', 'POST'])
@login_required
def play():
    if request.method == 'POST':
        GameSessionManager.initialize_session()

        stage = session['stage']
        points = session['points']

        fruit = Game.get_random_fruit()
        shuffled_keyboard = Game.shuffle_keyboard()
        encoded_keyboard = Game.encode_key_map(shuffled_keyboard)

        time_left = GameLogic.get_time_for_stage(stage)

        GameSessionManager.update_session(fruit, encoded_keyboard)
        UserManager.update_user_score()

        return jsonify({
            'fruit': fruit,
            'keyboard': encoded_keyboard,
            'time_left': time_left,
            'stage': stage,
            'points': points
        })

    return render_template('play.html', title='Play')

@main.route("/validate", methods=['POST'])
@login_required
def validate():
    user_input = request.json.get('user_input', '')
    original_fruit = session.get('current_fruit', '')

    if not GameLogic.validate_time():
        GameSessionManager.update_stage_and_points(False)
        return jsonify({
            'success': False,
            'message': 'Time is up!',
            'next_stage': session['stage'],
            'points': session['points']
        })

    is_correct = GameLogic.check_user_input(user_input, original_fruit)

    GameSessionManager.update_stage_and_points(is_correct)
    UserManager.update_user_score()

    return jsonify({
        'success': is_correct,
        'next_stage': session['stage'],
        'points': session['points']
    })

@main.route("/logout")
def logout():
    UserManager.update_user_score()
    GameSessionManager.reset_session()
    AuthManager.logout_user()
    return redirect(url_for('main.login'))
