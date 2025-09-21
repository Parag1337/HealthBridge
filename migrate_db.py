"""
Database migration script to add missing columns to users table
Run this script to update your existing MySQL database schema
"""

from app import create_app, db
from sqlalchemy import text

def migrate_database():
    app = create_app()
    
    with app.app_context():
        try:
            # Check if columns exist and add them if they don't
            migrations = [
                # Existing emergency contact fields
                "ALTER TABLE users ADD COLUMN emergency_contact VARCHAR(100) DEFAULT NULL",
                "ALTER TABLE users ADD COLUMN emergency_contact_phone VARCHAR(15) DEFAULT NULL",
                
                # Doctor practice location fields
                "ALTER TABLE users ADD COLUMN practice_address TEXT DEFAULT NULL",
                "ALTER TABLE users ADD COLUMN practice_city VARCHAR(100) DEFAULT NULL",
                "ALTER TABLE users ADD COLUMN practice_state VARCHAR(50) DEFAULT NULL",
                "ALTER TABLE users ADD COLUMN practice_zip_code VARCHAR(20) DEFAULT NULL",
                "ALTER TABLE users ADD COLUMN practice_latitude FLOAT DEFAULT NULL",
                "ALTER TABLE users ADD COLUMN practice_longitude FLOAT DEFAULT NULL",
                "ALTER TABLE users ADD COLUMN practice_phone VARCHAR(15) DEFAULT NULL",
                
                # Appointment enhancement fields
                "ALTER TABLE appointments ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
                "ALTER TABLE appointments ADD COLUMN started_at DATETIME DEFAULT NULL",
                "ALTER TABLE appointments ADD COLUMN completed_at DATETIME DEFAULT NULL",
                "ALTER TABLE appointments ADD COLUMN notes TEXT DEFAULT NULL"
            ]
            
            for migration in migrations:
                try:
                    db.session.execute(text(migration))
                    db.session.commit()
                    print(f"✅ Successfully executed: {migration}")
                except Exception as e:
                    if "Duplicate column name" in str(e):
                        print(f"ℹ️  Column already exists: {migration}")
                    else:
                        print(f"❌ Error executing {migration}: {e}")
                        db.session.rollback()
            
            print("\n🎉 Database migration completed!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()

if __name__ == "__main__":
    migrate_database()