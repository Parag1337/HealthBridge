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
                "ALTER TABLE users ADD COLUMN emergency_contact VARCHAR(100) DEFAULT NULL",
                "ALTER TABLE users ADD COLUMN emergency_contact_phone VARCHAR(15) DEFAULT NULL"
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