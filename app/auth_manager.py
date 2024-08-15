from flask_login import login_user, current_user, logout_user
from app import db, bcrypt
from app.models import User

class AuthManager:
    @staticmethod
    def register_user(form):
        """Register a new user with the provided form data."""
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def login_user(form):
        """Log in the user if the credentials are correct."""
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return True
        return False

    @staticmethod
    def logout_user():
        """Log out the current user."""
        logout_user()
