from app import create_app, db
from app.models.user import User
from app.models.appointment import Appointment
from app.models.prescription import Prescription

def init_database():
    """Initialize the database with all tables"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Check what tables were created
        tables = db.engine.table_names()
        print("Created tables:", tables)

if __name__ == "__main__":
    init_database()