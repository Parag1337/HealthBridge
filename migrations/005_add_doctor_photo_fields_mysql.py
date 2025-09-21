import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

def add_doctor_photo_fields_mysql():
    """Add photo and additional fields for doctors to MySQL database"""
    app = create_app()
    
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                # Add new columns to users table
                new_columns = [
                    'ADD COLUMN consultation_fee DECIMAL(10,2) DEFAULT 0.00',
                    'ADD COLUMN profile_photo VARCHAR(255) DEFAULT NULL',
                    'ADD COLUMN rating DECIMAL(3,2) DEFAULT 0.00',
                    'ADD COLUMN total_patients INT DEFAULT 0',
                    'ADD COLUMN about TEXT DEFAULT NULL',
                    'ADD COLUMN blood_type VARCHAR(5) DEFAULT NULL',
                    'ADD COLUMN allergies TEXT DEFAULT NULL'
                ]
                
                for column_def in new_columns:
                    try:
                        query = f'ALTER TABLE users {column_def}'
                        conn.execute(text(query))
                        conn.commit()
                        print(f"Added: {column_def}")
                    except Exception as e:
                        if "Duplicate column name" in str(e):
                            print(f"Column already exists: {column_def}")
                        else:
                            print(f"Error adding {column_def}: {e}")
                
                print("Successfully updated users table with new fields")
                
                # Verify the new structure
                result = conn.execute(text("DESCRIBE users;"))
                columns = result.fetchall()
                print("\nUpdated users table structure:")
                for col in columns:
                    print(f"  - {col[0]} ({col[1]})")
                    
        except Exception as e:
            print(f"Error updating database: {e}")

if __name__ == "__main__":
    add_doctor_photo_fields_mysql()