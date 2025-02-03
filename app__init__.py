from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    # Your existing configuration code here
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Register blueprints
    from app.routes import auth
    app.register_blueprint(auth.bp)

    from app.routes import main    
    app.register_blueprint(main.bp)
    
    from app.routes import journal
    app.register_blueprint(journal.bp)
    
    return app

