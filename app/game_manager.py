from flask import session
from flask_login import current_user
from datetime import datetime
from app import db
from app.models import User

class GameSessionManager:
    @staticmethod
    def initialize_session():
        """Initialize the game session with default values."""
        if 'stage' not in session:
            session['stage'] = 1
        if 'points' not in session:
            session['points'] = 0
        session['start_time'] = datetime.now().isoformat()
        session.modified = True

    @staticmethod
    def reset_session():
        """Reset the game session."""
        session.pop('stage', None)
        session.pop('points', None)
        session.pop('current_fruit', None)
        session.pop('random_key_map', None)
        session.pop('start_time', None)
        session.modified = True

    @staticmethod
    def update_session(fruit, shuffled_keyboard):
        """Update the session with the current fruit and shuffled keyboard."""
        session['current_fruit'] = fruit
        session['random_key_map'] = shuffled_keyboard
        session.modified = True

    @staticmethod
    def update_stage_and_points(is_correct):
        """Update stage and points in the session based on correctness of the answer."""
        if is_correct:
            session['stage'] += 1
            session['points'] += 10
        else:
            session['stage'] = 1
            session['points'] = 0
        session.modified = True

class UserManager:
    @staticmethod
    def update_user_score():
        """Update the user's score if the current session score is higher."""
        current_user.points = max(current_user.points, session.get('points', 0))
        db.session.commit()

class GameLogic:
    @staticmethod
    def get_time_for_stage(stage):
        """Return the time left based on the current stage."""
        if stage == 1:
            return 60
        elif stage == 2:
            return 45
        elif stage == 3:
            return 30
        else:
            return max(1, 30 - (stage - 3))

    @staticmethod
    def check_user_input(user_input, original_fruit):
        """Check if the user input matches the original fruit."""
        return user_input == original_fruit

    @staticmethod
    def validate_time():
        """Validate that the time has not run out."""
        start_time = datetime.fromisoformat(session.get('start_time', datetime.now().isoformat()))
        stage = session.get('stage', 1)
        elapsed_time = (datetime.now() - start_time).total_seconds()
        allowed_time = GameLogic.get_time_for_stage(stage)
        return elapsed_time <= allowed_time
