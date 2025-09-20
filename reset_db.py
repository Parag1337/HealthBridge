"""
Database reset script - drops all tables and recreates them with the latest schema
WARNING: This will delete all existing data!
"""

from app import create_app, db
from app.models.user import User
from app.models.appointment import Appointment
from app.models.prescription import Prescription

def reset_database():
    app = create_app()
    
    with app.app_context():
        try:
            print("🗑️  Dropping all existing tables...")
            db.drop_all()
            
            print("🏗️  Creating all tables with new schema...")
            db.create_all()
            
            print("✅ Database reset completed successfully!")
            print("\n📋 Tables created:")
            print("   - users (with all new columns)")
            print("   - appointments")
            print("   - prescriptions")
            
            # Create a sample doctor for testing
            print("\n👨‍⚕️ Creating sample doctor for testing...")
            sample_doctor = User(
                email='doctor@healthbridge.com',
                first_name='Dr. John',
                last_name='Smith',
                phone='555-0123',
                role='doctor',
                specialization='General Medicine',
                license_number='MD12345',
                qualification='MD, Internal Medicine',
                experience=5
            )
            sample_doctor.set_password('doctor123')
            
            db.session.add(sample_doctor)
            db.session.commit()
            
            print("✅ Sample doctor created:")
            print(f"   Email: doctor@healthbridge.com")
            print(f"   Password: doctor123")
            print(f"   Role: doctor")
            
        except Exception as e:
            print(f"❌ Database reset failed: {e}")
            db.session.rollback()

if __name__ == "__main__":
    print("⚠️  WARNING: This will delete all existing data!")
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        reset_database()
    else:
        print("❌ Database reset cancelled.")