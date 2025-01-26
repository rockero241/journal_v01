import secrets
import smtplib
import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db
from app.routes import journal
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_confirmed:
                flash('Please confirm your email before logging in.')
                return render_template('auth/unconfirmed.html')
            
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
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')  # Get first_name from form
        
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
        # Basic auth fields
        new_user.username = username
        new_user.email = email
        new_user.set_password(password)
        
        # Personal information
        new_user.first_name = request.form.get('first_name')
        new_user.last_name = request.form.get('last_name')
        new_user.phone = request.form.get('phone')
        
        # Address information
        new_user.address = request.form.get('address')
        new_user.city = request.form.get('city')
        new_user.state = request.form.get('state')
        new_user.country = request.form.get('country')
        new_user.postal_code = request.form.get('postal_code')
        
        # Generate confirmation token
        token = new_user.generate_confirmation_token()
        
        # Save to database
        db.session.add(new_user)
        db.session.commit()        
        # Send confirmation email
        confirmation_link = url_for('auth.confirm_email', token=token, _external=True)
        msg = MIMEMultipart()
        msg['From'] = os.environ.get("MY_GOOGLE_USER")
        msg['To'] = email
        msg['Subject'] = "Journal App - Please confirm Your Email"
        
        body = (f"Dear {first_name.capitalize()},\n\n"
        f"Thank you for registering with our Journal App.\n\n"
        f"Please click the following link to confirm your email: {confirmation_link}\n\n"
        f"Best regards,\n"
        f"Journal App Team")        
        msg.attach(MIMEText(body, 'plain'))

        # Send email using existing SMTP configuration
        smtp_server = "smtp.gmail.com"
        port = 587
        sender_email = os.environ.get("MY_GOOGLE_USER")
        app_password = os.environ.get("MY_GOOGLE_PASS")

        print(f"Debug10: Before sending mail: {smtp_server}, {port}, {sender_email}")
        try:
            server = smtplib.SMTP(smtp_server, port)
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)
            server.quit()
            # Replace the redirect with rendering the confirmation page
            return render_template('auth/registration_confirmation.html')
        except Exception as e:
            flash('Error sending confirmation email.')
            print(f"Debug: Error sending confirmation email: {e}")
        
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
            
            
            # Gmail SMTP configuration
              #  Get variables from environment
            google_user=os.environ.get("MY_GOOGLE_USER")
            google_pass=os.environ.get("MY_GOOGLE_PASS")
         
            smtp_server = "smtp.gmail.com"
            port = 587
            sender_email = google_user
            app_password = google_pass

            #  Please set up a 16 digits password in this link
            #  https://support.google.com/mail/?p=InvalidSecondFactor
            #  Then click on Create and manage your app passwords


            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = "Password Reset"

            body = f"Your new password is: {new_password}\nPlease change it after logging in."
            msg.attach(MIMEText(body, 'plain'))
            print(f"Debug: Before try ")

            try:
                server = smtplib.SMTP(smtp_server, port)
                server.starttls()
                server.login(sender_email, app_password)
                server.send_message(msg)
                server.quit()

                db.session.commit()
                flash('New password has been sent to your email!')
                return redirect(url_for('auth.login'))
            except Exception as e:
                print(f"Debug:  Exception: {e}")
                flash('Error sending email. Please try again.')
                return redirect(url_for('auth.reset_password'))
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
    #return redirect(url_for('main.index'))
    return render_template('auth/logout.html')

@bp.route('/index')
def index():
    #return render_template('auth/form.html')
    return redirect(url_for('auth.home'))

@bp.route('/confirm/<token>')
def confirm_email(token):
    try:
        user = User.query.filter_by(confirmation_token=token).first()
        if user:
            if user.is_confirmed:
                flash('Account already confirmed.')
            else:
                user.is_confirmed = True
                user.confirmation_token = None
                db.session.commit()
                return render_template('auth/confirmation_success.html')
        else:
            flash('Invalid or expired confirmation link.')
            return redirect(url_for('auth.login'))
    except:
        flash('The confirmation link is invalid or has expired.')
        return redirect(url_for('auth.login'))
          
@bp.route('/resend_confirmation', methods=['GET', 'POST'])
def resend_confirmation():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user and not user.is_confirmed:
            token = user.generate_confirmation_token()
            confirmation_link = url_for('auth.confirm_email', token=token, _external=True)
            
            msg = MIMEMultipart()
            msg['From'] = os.environ.get("MY_GOOGLE_USER")
            msg['To'] = email
            msg['Subject'] = "Journal App - New Confirmation Email"
            
            body = (f"Dear {user.first_name.capitalize()},\n\n"                   f"Here is your new confirmation link: {confirmation_link}\n\n"
                   f"Best regards,\n"
                   f"Journal App Team")            
            msg.attach(MIMEText(body, 'plain'))

            smtp_server = "smtp.gmail.com"
            port = 587
            sender_email = os.environ.get("MY_GOOGLE_USER")
            app_password = os.environ.get("MY_GOOGLE_PASS")

            try:
                server = smtplib.SMTP(smtp_server, port)
                server.starttls()
                server.login(sender_email, app_password)
                server.send_message(msg)
                server.quit()
                return render_template('auth/resend_confirmation_success.html')
            except Exception as e:
                flash('Error sending confirmation email.')
                print(f"Debug: Error sending confirmation email: {e}")
        else:
            flash('Email not found or already confirmed.')
            
    return render_template('auth/resend_confirmation.html')

@bp.route('/check_username/<username>')
def check_username(username):
    user = User.query.filter_by(username=username).first()
    return jsonify({'available': user is None})

@bp.route('/check_email/<email>')
def check_email(email):
    user = User.query.filter_by(email=email).first()
    return jsonify({'available': user is None})
