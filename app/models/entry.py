from app import db
from datetime import datetime

class Entry(db.Model):
    __tablename__ = 'entry'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    entry_date = db.Column(db.DateTime, default=datetime.utcnow)
    mood = db.Column(db.String(64), nullable=False)
    gratitude = db.Column(db.Text, nullable=False)
    room_for_growth = db.Column(db.Text, nullable=False)
    thoughts = db.Column(db.Text, nullable=False)
    ai_feedback = db.Column(db.Text)

    # ✅ Make sure this matches `User.entries`
    user = db.relationship('User', back_populates='entries')

    def __repr__(self):
        return f'<Entry {self.entry_date}>'
