from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.entry import Entry
import os
from openai import OpenAI

bp = Blueprint('journal', __name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@bp.route('/form', methods=['GET', 'POST'])
@login_required
def journal_form():
    if request.method == 'POST':
        entry = Entry(
            user_id=current_user.id,
            mood=request.form['mood'],
            gratitude=request.form['gratitude'],
            room_for_growth=request.form['room_for_growth'],
            thoughts=request.form['thoughts']
        )
        
        if request.form.get('feedback') == 'yes':
            entry.ai_feedback = get_ai_feedback(entry)
        
        db.session.add(entry)
        db.session.commit()
        
        flash('Journal entry saved successfully!')
        return redirect(url_for('journal.view_entries'))

def get_ai_feedback(entry):
    messages = [
        {"role": "system", "content": "You are a wise life coach who provides feedback based on a user's journaling entry, and gives simple, straightforward and practical advice."},
        {"role": "user", "content": (
            f"Mood: {entry.mood}\n"
            f"Gratitude: {entry.gratitude}\n"
            f"Room for growth: {entry.room_for_growth}\n"
            f"Thoughts: {entry.thoughts}\n"
            "Please provide positive, constructive feedback."
        )}
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )

    return response.choices[0].message.content

@bp.route('/journal', methods=['GET', 'POST'])
@login_required
def create_entry():
    if request.method == 'POST':
        entry = Entry(
            user_id=current_user.id,
            mood=request.form['mood'],
            gratitude=request.form['gratitude'],
            room_for_growth=request.form['room_for_growth'],
            thoughts=request.form['thoughts']
        )

        if request.form.get('feedback') == 'yes':
            entry.ai_feedback = get_ai_feedback(entry)

        db.session.add(entry)
        db.session.commit()

        flash('Journal entry saved successfully!')
        return redirect(url_for('journal.view_entries'))

    return render_template('journal/form.html')

@bp.route('/entries')
@login_required
def view_entries():
    sort_by = request.args.get('sort', 'date_desc')
    mood_filter = request.args.get('mood', None)
    
    query = Entry.query.filter_by(user_id=current_user.id)

    if mood_filter:
        query = query.filter_by(mood=mood_filter)
        
    if sort_by == 'date_asc':
        query = query.order_by(Entry.entry_date.asc())  # ✅ FIXED
    else:
        query = query.order_by(Entry.entry_date.desc())  # ✅ FIXED
        
    entries = query.all()
    return render_template('journal/entries.html', entries=entries)  # ✅ FIXED SYNTAX ERROR

@bp.route('/entry/<int:entry_id>')
@login_required
def view_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        abort(403)
    return render_template('journal/entry_detail.html', entry=entry)
