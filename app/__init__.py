from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Load configuration from config.py
    app.config.from_object('app.config.Config')

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    # Import and register blueprints
    from .routes import main, auth, patient, doctor
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(patient.bp)
    app.register_blueprint(doctor.bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app