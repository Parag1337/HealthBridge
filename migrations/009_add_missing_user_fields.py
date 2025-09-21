"""
Migration script to add missing user fields to users table for MySQL
Run this file independently: python migrations/009_add_missing_user_fields.py
"""

import mysql.connector
from mysql.connector import Error
import sys
import os

# Add the parent directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_db_connection():
    """Get database connection using app config values"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='smart_healthcare_db',
            user='root',
            password='password'
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def add_missing_user_fields():
    """Add missing fields to users table"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Check which columns already exist
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'smart_healthcare_db' 
            AND TABLE_NAME = 'users';
        """)
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        # Add missing columns one by one
        columns_to_add = [
            ('years_of_experience', 'INT NULL COMMENT "Years of experience for doctors"'),
            ('bio', 'TEXT NULL COMMENT "Doctor bio/description"'),
            ('hospital_affiliation', 'VARCHAR(200) NULL COMMENT "Hospital name for doctors"')
        ]
        
        for column_name, column_definition in columns_to_add:
            if column_name not in existing_columns:
                print(f"Adding {column_name} column...")
                cursor.execute(f"""
                    ALTER TABLE users 
                    ADD COLUMN {column_name} {column_definition};
                """)
            else:
                print(f"✓ Column {column_name} already exists")
        
        connection.commit()
        print("✅ Missing user fields added successfully!")
        return True
        
    except Error as e:
        print(f"❌ Error adding user fields: {e}")
        connection.rollback()
        return False
        
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def add_missing_appointment_fields():
    """Add missing telemedicine fields to appointments table"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Check which columns already exist in appointments table
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'smart_healthcare_db' 
            AND TABLE_NAME = 'appointments';
        """)
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        print(f"Existing appointment columns: {existing_columns}")
        
        # Add missing telemedicine columns
        appointment_columns_to_add = [
            ('telemedicine_platform', 'VARCHAR(50) NULL COMMENT "Platform for telemedicine (zoom, google-meet, etc.)"'),
            ('telemedicine_link', 'TEXT NULL COMMENT "Meeting link for telemedicine session"'),
            ('consultation_fee', 'DECIMAL(10,2) NULL COMMENT "Fee for this consultation"')
        ]
        
        for column_name, column_definition in appointment_columns_to_add:
            if column_name not in existing_columns:
                print(f"Adding {column_name} column to appointments...")
                cursor.execute(f"""
                    ALTER TABLE appointments 
                    ADD COLUMN {column_name} {column_definition};
                """)
            else:
                print(f"✓ Appointment column {column_name} already exists")
        
        connection.commit()
        print("✅ Missing appointment fields added successfully!")
        return True
        
    except Error as e:
        print(f"❌ Error adding appointment fields: {e}")
        connection.rollback()
        return False
        
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


if __name__ == "__main__":
    print("🏥 Adding missing fields to database tables...")
    
    user_success = add_missing_user_fields()
    appointment_success = add_missing_appointment_fields()
    
    if user_success and appointment_success:
        print("🎉 Migration completed successfully!")
    else:
        print("💥 Migration failed!")
        sys.exit(1)