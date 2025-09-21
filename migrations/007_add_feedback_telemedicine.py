"""
Database migration to add feedback and telemedicine tables
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'password'),
            database=os.getenv('DB_NAME', 'smart_healthcare_db')
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_feedback_table(cursor):
    """Create appointment_feedback table"""
    create_feedback_sql = """
    CREATE TABLE IF NOT EXISTS appointment_feedback (
        id INT AUTO_INCREMENT PRIMARY KEY,
        appointment_id INT NOT NULL,
        patient_id INT NOT NULL,
        doctor_id INT NOT NULL,
        overall_rating INT NOT NULL CHECK (overall_rating >= 1 AND overall_rating <= 5),
        doctor_rating INT NOT NULL CHECK (doctor_rating >= 1 AND doctor_rating <= 5),
        communication_rating INT NOT NULL CHECK (communication_rating >= 1 AND communication_rating <= 5),
        punctuality_rating INT NOT NULL CHECK (punctuality_rating >= 1 AND punctuality_rating <= 5),
        cleanliness_rating INT NOT NULL CHECK (cleanliness_rating >= 1 AND cleanliness_rating <= 5),
        positive_feedback TEXT,
        negative_feedback TEXT,
        suggestions TEXT,
        would_recommend BOOLEAN DEFAULT TRUE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE CASCADE,
        FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE KEY unique_appointment_feedback (appointment_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    cursor.execute(create_feedback_sql)
    print("✓ Created appointment_feedback table")

def create_video_consultations_table(cursor):
    """Create video_consultations table"""
    create_video_sql = """
    CREATE TABLE IF NOT EXISTS video_consultations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        appointment_id INT NOT NULL,
        patient_id INT NOT NULL,
        doctor_id INT NOT NULL,
        room_id VARCHAR(100) UNIQUE NOT NULL,
        meeting_url VARCHAR(500),
        status VARCHAR(20) DEFAULT 'scheduled',
        platform VARCHAR(50) DEFAULT 'webrtc',
        duration_minutes INT,
        actual_start_time DATETIME,
        actual_end_time DATETIME,
        patient_joined_at DATETIME,
        doctor_joined_at DATETIME,
        connection_quality VARCHAR(20),
        recording_enabled BOOLEAN DEFAULT FALSE,
        recording_url VARCHAR(500),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE CASCADE,
        FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE KEY unique_appointment_video (appointment_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    cursor.execute(create_video_sql)
    print("✓ Created video_consultations table")

def add_indexes(cursor):
    """Add indexes for better performance"""
    indexes = [
        "CREATE INDEX idx_feedback_patient ON appointment_feedback(patient_id);",
        "CREATE INDEX idx_feedback_doctor ON appointment_feedback(doctor_id);", 
        "CREATE INDEX idx_feedback_rating ON appointment_feedback(overall_rating);",
        "CREATE INDEX idx_video_patient ON video_consultations(patient_id);",
        "CREATE INDEX idx_video_doctor ON video_consultations(doctor_id);",
        "CREATE INDEX idx_video_status ON video_consultations(status);",
        "CREATE INDEX idx_video_room ON video_consultations(room_id);"
    ]
    
    for index_sql in indexes:
        try:
            cursor.execute(index_sql)
        except Error as e:
            if "Duplicate key name" not in str(e):
                print(f"Warning: Could not create index: {e}")
    
    print("✓ Added performance indexes")

def run_migration():
    """Run the database migration"""
    print("Starting feedback and telemedicine migration...")
    
    connection = get_db_connection()
    if not connection:
        print("❌ Failed to connect to database")
        return False
    
    try:
        cursor = connection.cursor()
        
        # Create tables
        create_feedback_table(cursor)
        create_video_consultations_table(cursor)
        
        # Add indexes
        add_indexes(cursor)
        
        # Commit changes
        connection.commit()
        print("✅ Migration completed successfully!")
        
        # Show table info
        cursor.execute("SHOW TABLES LIKE '%feedback%' OR SHOW TABLES LIKE '%video%';")
        tables = cursor.fetchall()
        print(f"\nCreated tables: {', '.join([table[0] for table in tables])}")
        
        return True
        
    except Error as e:
        print(f"❌ Migration failed: {e}")
        connection.rollback()
        return False
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("\n🎉 Ready to use feedback and telemedicine features!")
    else:
        print("\n💥 Migration failed. Please check the errors above.")