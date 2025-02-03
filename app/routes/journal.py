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
         {"role": "system", "content": 
         "You are a supportive, slightly teasing friend who gives personalized journal feedback in 75 words or less. Your tone is casual, fun, and engaging—like a real person who cares. 😜"},
        {"role": "user", "content": f"""
        Journal Entry:
        - **Mood:** {entry.mood}
        - **Gratitude:** {entry.gratitude}
        - **Room for Growth:** {entry.room_for_growth}
        - **Thoughts:** {entry.thoughts}

        Provide personalized feedback that:
        - Feels like a friend responding, not a self-help book.
        - Matches the user's emotional tone! If they're excited, mirror that energy 🎉. If they're tired or overwhelmed, be reassuring.
        - Offers **1-2 concrete, actionable suggestions** that are fun & doable.
        - Rotates techniques to keep responses fresh.
        - Does **not** force advice—if no 'Room for Growth' is provided, just validate and encourage them. ❤️
        - Uses emojis sparingly but effectively to enhance personality.
        - Sounds **natural and human**—avoid robotic phrasing or generic motivational quotes.
        """}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Use the fastest model
        messages=messages,
        max_tokens=100,  # Reduce output length
        temperature=0.7  # Keeps responses focused
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
