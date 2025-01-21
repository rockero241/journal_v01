from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('main/index.html')
#    return redirect(url_for('auth/login'))

@bp.route('/home')
def home():
    return render_template('auth/home.html')
    #return redirect(url_for('auth/home.html'))

@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('main/dashboard.html')
