from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db
import secrets

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').lower()  # Convert to lowercase
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            if user.is_temporary_password:
                return redirect(url_for('auth.change_password'))
            return redirect(url_for('journal.create_entry'))
        else:
            flash('Invalid username or password')
            
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():    
    if request.method == 'POST':
        username = request.form.get('username').lower()  # Convert to lowercase
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')        
        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('auth.register'))
            
        user_exists = User.query.filter_by(username=username).first()        
        if user_exists:
            flash('Username already exists!')
            return redirect(url_for('auth.register'))        
        
        email_exists = User.query.filter_by(email=email).first()        
        if email_exists:
            flash('Email already registered!')
            return redirect(url_for('auth.register'))
        
        new_user = User()
        new_user.username = username
        new_user.email = email
        new_user.set_password(password)
        new_user.first_name = first_name
        new_user.last_name = request.form.get('last_name')
        new_user.phone = request.form.get('phone')
        new_user.address = request.form.get('address')
        new_user.city = request.form.get('city')
        new_user.is_confirmed = True
        
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('journal.create_entry'))
        
    return render_template('auth/register.html')

@bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Email is required!')
            return render_template('auth/reset_password.html')

        user = User.query.filter_by(email=email).first()
        if user:
            new_password = secrets.token_urlsafe(12)
            user.set_password(new_password)
            user.is_temporary_password = True
            db.session.commit()
            flash('Please contact administrator for your new password')
            return redirect(url_for('auth.login'))
        else:
            flash('Email not found!')

    return render_template('auth/reset_password.html')

@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('Passwords do not match!')
            return render_template('auth/change_password.html')
        
        current_user.set_password(new_password)
        current_user.is_temporary_password = False
        db.session.commit()
        
        flash('Password successfully updated!')
        return redirect(url_for('journal.create_entry'))
    
    return render_template('auth/change_password.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('auth/logout.html')

@bp.route('/index')
def index():
    return redirect(url_for('auth.login'))

@bp.route('/check_username/<username>')
def check_username(username):
    user = User.query.filter_by(username=username).first()
    return jsonify({'available': user is None})

@bp.route('/check_email/<email>')
def check_email(email):
    user = User.query.filter_by(email=email).first()
    return jsonify({'available': user is None})
