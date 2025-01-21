from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from app.models.user import User
from app import db
from app.routes import journal

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!')
            #next_page = request.args.get('next')
            #return redirect(next_page) if next_page else redirect(url_for('main.index'))
            #return redirect(next_page) if next_page else redirect(url_for('journal.form'))
            return redirect(url_for('journal.create_entry'))
        else:
            flash('Invalid username or password')
            #return redirect(url_for('auth.login'))
            
    return render_template('auth/login.html')
    #return redirect(url_to('main.form'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('auth.register'))

        user_exists = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()

        if user_exists:
            flash('Username already exists!')
            return redirect(url_for('auth.register'))
        
        if email_exists:
            flash('Email already registered!')
            return redirect(url_for('auth.register'))

        new_user = User()
        new_user.username = username
        new_user.email = email
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful!')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    #return redirect(url_for('main.index'))
    return render_template('auth/logout.html')

@bp.route('/index')
def index():
    #return render_template('auth/form.html')
    return redirect(url_for('auth.home'))
