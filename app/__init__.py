from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import os
from datetime import date, datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    
    # Load configuration from config.py
    app.config.from_object('app.config.Config')

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    # Import and register blueprints
    from .routes import main, auth, patient, doctor, telemedicine
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(patient.bp)
    app.register_blueprint(doctor.bp)
    app.register_blueprint(telemedicine.bp)

    # Create database tables (only if not in production or if explicitly requested)
    with app.app_context():
        try:
            # Import all models to ensure SQLAlchemy knows about them
            from app.models.user import User
            from app.models.appointment import Appointment
            from app.models.prescription import Prescription, PrescriptionMedication, LabTest
            from app.models.telemedicine import VideoConsultation
            from app.models.scheduling import DoctorSchedule, SlotConfiguration
            
            # Only create tables if they don't exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if not existing_tables:
                print("🔄 Creating database tables...")
                db.create_all()
                print("✅ Database tables created successfully!")
            else:
                print(f"📋 Database already has {len(existing_tables)} tables")
                
        except Exception as e:
            print(f"⚠️  Database initialization warning: {str(e)}")
            # Don't fail the app startup, just log the warning

    # Make date, datetime, and timedelta available to all templates
    @app.template_global()
    def get_date():
        return date
    
    @app.template_global()
    def get_datetime():
        return datetime
    
    @app.template_global()
    def get_timedelta():
        from datetime import timedelta
        return timedelta
    
    @app.template_global()
    def get_duration(start_time, end_time):
        """Calculate duration between two times and return formatted string"""
        if not start_time or not end_time:
            return "N/A"
        
        # If they're datetime objects, extract time
        if hasattr(start_time, 'time'):
            start_time = start_time.time()
        if hasattr(end_time, 'time'):
            end_time = end_time.time()
        
        # Convert to datetime for calculation
        start_dt = datetime.combine(date.today(), start_time)
        end_dt = datetime.combine(date.today(), end_time)
        
        # Handle case where end time is before start time (next day)
        if end_dt < start_dt:
            end_dt += timedelta(days=1)
        
        duration = end_dt - start_dt
        minutes = int(duration.total_seconds() / 60)
        
        if minutes < 60:
            return f"{minutes} min"
        else:
            hours = minutes // 60
            remaining_minutes = minutes % 60
            if remaining_minutes == 0:
                return f"{hours}h"
            else:
                return f"{hours}h {remaining_minutes}m"

    return app