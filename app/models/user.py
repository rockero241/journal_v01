from app import db, login_manager
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    __table_args__ = (
        db.UniqueConstraint('username', name='uq_user_username'),
        db.UniqueConstraint('email', name='uq_user_email'),
        db.UniqueConstraint('confirmation_token', name='uq_user_confirmation_token'),
    )
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(35), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    is_temporary_password = db.Column(db.Boolean, default=False)
    is_confirmed = db.Column(db.Boolean, default=False)
    confirmation_token = db.Column(db.String(100), unique=True)
    entries = db.relationship('Entry', back_populates='user', lazy='dynamic')

    def generate_confirmation_token(self):
        # Set expiration to 7 days (or any desired duration)
        expires_in = timedelta(hours=48)
        exp_timestamp = datetime.utcnow() + expires_in
        
        payload = {
            'user_id': self.id,
            'exp': exp_timestamp
        }
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        self.confirmation_token = token
        db.session.commit()
        return token   
     
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
