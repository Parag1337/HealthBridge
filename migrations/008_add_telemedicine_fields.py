"""
Migration script to add telemedicine fields to appointments table
Run this file independently: python migrations/008_add_telemedicine_fields.py
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
            database='smart_healthcare',
            user='root',
            password='root'
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def add_telemedicine_fields():
    """Add telemedicine-specific fields to appointments table"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Check if columns already exist
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'smart_healthcare' 
            AND TABLE_NAME = 'appointments' 
            AND COLUMN_NAME IN ('telemedicine_platform', 'telemedicine_link', 'consultation_fee');
        """)
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        # Add missing columns
        if 'telemedicine_platform' not in existing_columns:
            print("Adding telemedicine_platform column...")
            cursor.execute("""
                ALTER TABLE appointments 
                ADD COLUMN telemedicine_platform VARCHAR(50) NULL 
                COMMENT 'Platform for telemedicine (zoom, google-meet, etc.)';
            """)
        
        if 'telemedicine_link' not in existing_columns:
            print("Adding telemedicine_link column...")
            cursor.execute("""
                ALTER TABLE appointments 
                ADD COLUMN telemedicine_link TEXT NULL 
                COMMENT 'Meeting link for telemedicine session';
            """)
        
        if 'consultation_fee' not in existing_columns:
            print("Adding consultation_fee column...")
            cursor.execute("""
                ALTER TABLE appointments 
                ADD COLUMN consultation_fee DECIMAL(10,2) NULL 
                COMMENT 'Fee for this consultation';
            """)
        
        # Update appointment_type enum to include telemedicine
        print("Updating appointment_type enum...")
        cursor.execute("""
            ALTER TABLE appointments 
            MODIFY COLUMN appointment_type VARCHAR(20) DEFAULT 'in-person' 
            COMMENT 'Type: in-person, online, telemedicine, hybrid';
        """)
        
        connection.commit()
        print("✅ Telemedicine fields added successfully!")
        return True
        
    except Error as e:
        print(f"❌ Error adding telemedicine fields: {e}")
        connection.rollback()
        return False
        
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("🏥 Adding telemedicine fields to appointments table...")
    success = add_telemedicine_fields()
    if success:
        print("🎉 Migration completed successfully!")
    else:
        print("💥 Migration failed!")
        sys.exit(1)