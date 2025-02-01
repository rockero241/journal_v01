from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    # ✅ Fix the relationship name & ensure bidirectional linking
    entries = db.relationship('Entry', back_populates='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'
