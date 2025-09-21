import sqlite3
import os

def add_doctor_photo_fields():
    """Add photo and additional fields for doctors and patients"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'healthbridge.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Add new fields for doctors
        new_columns = [
            ('consultation_fee', 'REAL DEFAULT 0.0'),
            ('profile_photo', 'TEXT'),
            ('rating', 'REAL DEFAULT 0.0'),
            ('total_patients', 'INTEGER DEFAULT 0'),
            ('about', 'TEXT'),
            ('blood_type', 'TEXT'),
            ('allergies', 'TEXT')
        ]
        
        for column_name, column_type in new_columns:
            try:
                cursor.execute(f'ALTER TABLE users ADD COLUMN {column_name} {column_type}')
                print(f"Added column {column_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"Column {column_name} already exists, skipping")
                else:
                    print(f"Error adding column {column_name}: {e}")
        
        conn.commit()
        print("Successfully added doctor photo and additional fields")
        
    except Exception as e:
        print(f"Error updating database: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    add_doctor_photo_fields()