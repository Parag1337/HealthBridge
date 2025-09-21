"""
Database migration to add appointment_type field for hybrid appointments
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

def add_appointment_type_field():
    """Add appointment_type field to appointments table"""
    app = create_app()
    
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                # Add appointment_type column to appointments table
                try:
                    query = "ALTER TABLE appointments ADD COLUMN appointment_type VARCHAR(20) DEFAULT 'in-person' AFTER status"
                    conn.execute(text(query))
                    conn.commit()
                    print("✅ Added appointment_type column to appointments table")
                except Exception as e:
                    if "Duplicate column name" in str(e):
                        print("⚠️  appointment_type column already exists, skipping...")
                    else:
                        raise e
                
                # Update existing appointments to have in-person type
                update_query = "UPDATE appointments SET appointment_type = 'in-person' WHERE appointment_type IS NULL"
                conn.execute(text(update_query))
                conn.commit()
                print("✅ Updated existing appointments to 'in-person' type")
                
                print("✅ Appointment type migration completed successfully!")
                return True
                
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            return False

if __name__ == "__main__":
    success = add_appointment_type_field()
    if not success:
        exit(1)