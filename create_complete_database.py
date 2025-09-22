#!/usr/bin/env python3
"""
Complete Database Setup Script for HealthBridge AI
This script creates the entire database schema with all tables and fields.
Run this once to set up a fresh database with all required tables.

Usage: python create_complete_database.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text
import traceback

def create_complete_database():
    """Create complete database schema with all tables and fields"""
    
    print("=" * 60)
    print("🏥 HealthBridge AI - Complete Database Setup")
    print("=" * 60)
    print("🚀 Creating complete database schema...")
    print()
    
    app = create_app()
    
    with app.app_context():
        try:
            # Drop all existing tables first (be careful!)
            print("⚠️  Dropping existing tables...")
            db.drop_all()
            
            # Create all tables from models
            print("📋 Creating base tables from models...")
            db.create_all()
            
            print("✅ Base tables created successfully!")
            print()
            
            # Now add all the additional fields and modifications
            print("🔧 Adding additional fields and enhancements...")
            
            # 1. Add doctor photo and additional fields
            print("📸 Adding doctor photo fields...")
            add_doctor_photo_fields()
            
            # 2. Add scheduling system tables
            print("📅 Adding scheduling system...")
            add_scheduling_system()
            
            # 3. Add appointment type field
            print("🏥 Adding appointment type field...")
            add_appointment_type_field()
            
            # 4. Add feedback system
            print("📝 Adding feedback system...")
            add_feedback_system()
            
            # 5. Add telemedicine fields
            print("💻 Adding telemedicine fields...")
            add_telemedicine_fields()
            
            # 6. Add missing user fields
            print("👤 Adding missing user fields...")
            add_missing_user_fields()
            
            # 7. Add appointment preferences
            print("⚙️ Adding appointment preferences...")
            add_appointment_preferences()
            
            # 8. Add prescription enhancements
            print("💊 Adding prescription enhancements...")
            add_prescription_enhancements()
            
            # 9. Update lab tests
            print("🧪 Adding lab tests support...")
            add_lab_tests_support()
            
            print()
            print("🎉 Complete database setup finished successfully!")
            print("💡 Your HealthBridge database is ready to use!")
            
        except Exception as e:
            print(f"❌ Error during database setup: {str(e)}")
            print("📋 Full error details:")
            traceback.print_exc()
            return False
            
    return True

def add_doctor_photo_fields():
    """Add photo and additional fields for doctors"""
    try:
        # Add photo fields to users table for doctors
        db.session.execute(text("""
            ALTER TABLE users 
            ADD COLUMN photo_filename VARCHAR(255) DEFAULT NULL
        """))
        
        db.session.execute(text("""
            ALTER TABLE users 
            ADD COLUMN photo_url VARCHAR(500) DEFAULT NULL
        """))
        
        # Add additional doctor fields
        db.session.execute(text("""
            ALTER TABLE users 
            ADD COLUMN specialization VARCHAR(200) DEFAULT NULL
        """))
        
        db.session.execute(text("""
            ALTER TABLE users 
            ADD COLUMN license_number VARCHAR(100) DEFAULT NULL
        """))
        
        db.session.execute(text("""
            ALTER TABLE users 
            ADD COLUMN years_of_experience INT DEFAULT NULL
        """))
        
        db.session.execute(text("""
            ALTER TABLE users 
            ADD COLUMN consultation_fee DECIMAL(10,2) DEFAULT NULL
        """))
        
        db.session.execute(text("""
            ALTER TABLE users 
            ADD COLUMN bio TEXT DEFAULT NULL
        """))
        
        db.session.commit()
        print("   ✅ Doctor photo and profile fields added")
        
    except Exception as e:
        if "Duplicate column name" in str(e):
            print("   ⚠️  Doctor fields already exist, skipping...")
        else:
            print(f"   ❌ Error adding doctor fields: {e}")
        db.session.rollback()

def add_scheduling_system():
    """Add comprehensive scheduling system tables"""
    try:
        # DoctorSchedule table
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS doctor_schedules (
                id INT AUTO_INCREMENT PRIMARY KEY,
                doctor_id INT NOT NULL,
                day_of_week INT NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                is_available BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_doctor_day (doctor_id, day_of_week)
            )
        """))
        
        # SlotConfiguration table
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS slot_configurations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                doctor_id INT NOT NULL,
                slot_duration INT NOT NULL DEFAULT 30,
                buffer_time INT NOT NULL DEFAULT 5,
                max_patients_per_slot INT NOT NULL DEFAULT 1,
                advance_booking_days INT NOT NULL DEFAULT 30,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_doctor_config (doctor_id)
            )
        """))
        
        # AvailabilityOverride table
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS availability_overrides (
                id INT AUTO_INCREMENT PRIMARY KEY,
                doctor_id INT NOT NULL,
                override_date DATE NOT NULL,
                start_time TIME,
                end_time TIME,
                is_available BOOLEAN DEFAULT FALSE,
                reason VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_doctor_date (doctor_id, override_date)
            )
        """))
        
        # TimeSlot table
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS time_slots (
                id INT AUTO_INCREMENT PRIMARY KEY,
                doctor_id INT NOT NULL,
                slot_date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                is_booked BOOLEAN DEFAULT FALSE,
                appointment_id INT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE SET NULL,
                UNIQUE KEY unique_doctor_slot (doctor_id, slot_date, start_time)
            )
        """))
        
        # RecurringSchedule table
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS recurring_schedules (
                id INT AUTO_INCREMENT PRIMARY KEY,
                doctor_id INT NOT NULL,
                pattern_type ENUM('weekly', 'monthly') NOT NULL DEFAULT 'weekly',
                pattern_data JSON,
                start_date DATE NOT NULL,
                end_date DATE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """))
        
        db.session.commit()
        print("   ✅ Scheduling system tables created")
        
    except Exception as e:
        if "already exists" in str(e):
            print("   ⚠️  Scheduling tables already exist, skipping...")
        else:
            print(f"   ❌ Error creating scheduling tables: {e}")
        db.session.rollback()

def add_appointment_type_field():
    """Add appointment_type field to appointments table"""
    try:
        db.session.execute(text("""
            ALTER TABLE appointments 
            ADD COLUMN appointment_type ENUM('in-person', 'online', 'telemedicine') DEFAULT 'in-person'
        """))
        
        db.session.commit()
        print("   ✅ Appointment type field added")
        
    except Exception as e:
        if "Duplicate column name" in str(e):
            print("   ⚠️  Appointment type field already exists, skipping...")
        else:
            print(f"   ❌ Error adding appointment type field: {e}")
        db.session.rollback()

def add_feedback_system():
    """Add comprehensive feedback system"""
    try:
        # Create feedback table
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT NOT NULL,
                doctor_id INT NOT NULL,
                appointment_id INT,
                rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
                comment TEXT,
                feedback_type ENUM('appointment', 'general', 'telemedicine') DEFAULT 'appointment',
                is_anonymous BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE SET NULL
            )
        """))
        
        # Add feedback-related fields to appointments
        db.session.execute(text("""
            ALTER TABLE appointments 
            ADD COLUMN feedback_submitted BOOLEAN DEFAULT FALSE
        """))
        
        db.session.execute(text("""
            ALTER TABLE appointments 
            ADD COLUMN feedback_rating INT DEFAULT NULL
        """))
        
        db.session.commit()
        print("   ✅ Feedback system created")
        
    except Exception as e:
        if "already exists" in str(e) or "Duplicate column name" in str(e):
            print("   ⚠️  Feedback system already exists, skipping...")
        else:
            print(f"   ❌ Error creating feedback system: {e}")
        db.session.rollback()

def add_telemedicine_fields():
    """Add telemedicine support fields"""
    try:
        # Create telemedicine_sessions table
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS telemedicine_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                appointment_id INT NOT NULL,
                session_url VARCHAR(500),
                session_id VARCHAR(255),
                platform ENUM('jitsi', 'zoom', 'custom') DEFAULT 'jitsi',
                status ENUM('scheduled', 'active', 'completed', 'cancelled') DEFAULT 'scheduled',
                started_at TIMESTAMP NULL,
                ended_at TIMESTAMP NULL,
                duration_minutes INT DEFAULT NULL,
                recording_url VARCHAR(500) DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE CASCADE,
                UNIQUE KEY unique_appointment (appointment_id)
            )
        """))
        
        # Add telemedicine fields to appointments
        db.session.execute(text("""
            ALTER TABLE appointments 
            ADD COLUMN meeting_url VARCHAR(500) DEFAULT NULL
        """))
        
        db.session.execute(text("""
            ALTER TABLE appointments 
            ADD COLUMN meeting_id VARCHAR(255) DEFAULT NULL
        """))
        
        db.session.execute(text("""
            ALTER TABLE appointments 
            ADD COLUMN platform ENUM('jitsi', 'zoom', 'custom') DEFAULT 'jitsi'
        """))
        
        db.session.commit()
        print("   ✅ Telemedicine fields added")
        
    except Exception as e:
        if "already exists" in str(e) or "Duplicate column name" in str(e):
            print("   ⚠️  Telemedicine fields already exist, skipping...")
        else:
            print(f"   ❌ Error adding telemedicine fields: {e}")
        db.session.rollback()

def add_missing_user_fields():
    """Add missing fields to users table"""
    try:
        # Add comprehensive user fields
        fields_to_add = [
            ("phone_number", "VARCHAR(20) DEFAULT NULL"),
            ("date_of_birth", "DATE DEFAULT NULL"),
            ("gender", "ENUM('male', 'female', 'other') DEFAULT NULL"),
            ("address", "TEXT DEFAULT NULL"),
            ("emergency_contact_name", "VARCHAR(255) DEFAULT NULL"),
            ("emergency_contact_phone", "VARCHAR(20) DEFAULT NULL"),
            ("blood_type", "VARCHAR(5) DEFAULT NULL"),
            ("allergies", "TEXT DEFAULT NULL"),
            ("medical_history", "TEXT DEFAULT NULL"),
            ("current_medications", "TEXT DEFAULT NULL"),
            ("is_active", "BOOLEAN DEFAULT TRUE"),
            ("last_login", "TIMESTAMP NULL DEFAULT NULL"),
            ("profile_picture", "VARCHAR(255) DEFAULT NULL"),
            ("timezone", "VARCHAR(50) DEFAULT 'UTC'"),
            ("preferred_language", "VARCHAR(10) DEFAULT 'en'"),
            ("notification_preferences", "JSON DEFAULT NULL")
        ]
        
        for field_name, field_definition in fields_to_add:
            try:
                db.session.execute(text(f"""
                    ALTER TABLE users 
                    ADD COLUMN {field_name} {field_definition}
                """))
            except Exception as field_error:
                if "Duplicate column name" in str(field_error):
                    continue
                else:
                    print(f"     ⚠️  Error adding field {field_name}: {field_error}")
        
        db.session.commit()
        print("   ✅ Missing user fields added")
        
    except Exception as e:
        print(f"   ❌ Error adding missing user fields: {e}")
        db.session.rollback()

def add_appointment_preferences():
    """Add appointment preferences system"""
    try:
        # Create appointment_preferences table
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS appointment_preferences (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                preferred_time_slots JSON DEFAULT NULL,
                preferred_days JSON DEFAULT NULL,
                appointment_type_preference ENUM('in-person', 'online', 'both') DEFAULT 'both',
                reminder_preferences JSON DEFAULT NULL,
                special_requirements TEXT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_preferences (user_id)
            )
        """))
        
        # Add preference fields to appointments
        db.session.execute(text("""
            ALTER TABLE appointments 
            ADD COLUMN preferred_language VARCHAR(10) DEFAULT 'en'
        """))
        
        db.session.execute(text("""
            ALTER TABLE appointments 
            ADD COLUMN special_instructions TEXT DEFAULT NULL
        """))
        
        db.session.execute(text("""
            ALTER TABLE appointments 
            ADD COLUMN reminder_sent BOOLEAN DEFAULT FALSE
        """))
        
        db.session.commit()
        print("   ✅ Appointment preferences added")
        
    except Exception as e:
        if "already exists" in str(e) or "Duplicate column name" in str(e):
            print("   ⚠️  Appointment preferences already exist, skipping...")
        else:
            print(f"   ❌ Error adding appointment preferences: {e}")
        db.session.rollback()

def add_prescription_enhancements():
    """Add enhanced prescription system"""
    try:
        # Add missing prescription fields
        prescription_fields = [
            ("dosage_unit", "VARCHAR(50) DEFAULT 'mg'"),
            ("route_of_administration", "VARCHAR(100) DEFAULT 'oral'"),
            ("prescription_type", "ENUM('acute', 'chronic', 'preventive') DEFAULT 'acute'"),
            ("refills_remaining", "INT DEFAULT 0"),
            ("max_refills", "INT DEFAULT 0"),
            ("is_generic_allowed", "BOOLEAN DEFAULT TRUE"),
            ("pharmacy_instructions", "TEXT DEFAULT NULL"),
            ("side_effects", "TEXT DEFAULT NULL"),
            ("contraindications", "TEXT DEFAULT NULL"),
            ("drug_interactions", "TEXT DEFAULT NULL"),
            ("prescription_status", "ENUM('active', 'completed', 'cancelled', 'expired') DEFAULT 'active'"),
            ("prescribed_by", "INT DEFAULT NULL"),
            ("verified_by", "INT DEFAULT NULL"),
            ("dispensed_at", "TIMESTAMP NULL DEFAULT NULL"),
            ("last_refill_date", "TIMESTAMP NULL DEFAULT NULL")
        ]
        
        for field_name, field_definition in prescription_fields:
            try:
                db.session.execute(text(f"""
                    ALTER TABLE prescriptions 
                    ADD COLUMN {field_name} {field_definition}
                """))
            except Exception as field_error:
                if "Duplicate column name" in str(field_error):
                    continue
        
        # Add foreign key for prescribed_by
        try:
            db.session.execute(text("""
                ALTER TABLE prescriptions 
                ADD FOREIGN KEY (prescribed_by) REFERENCES users(id) ON DELETE SET NULL
            """))
        except:
            pass  # Foreign key might already exist
        
        db.session.commit()
        print("   ✅ Prescription enhancements added")
        
    except Exception as e:
        print(f"   ❌ Error adding prescription enhancements: {e}")
        db.session.rollback()

def add_lab_tests_support():
    """Add lab tests and medical records support"""
    try:
        # Create lab_tests table
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS lab_tests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT NOT NULL,
                doctor_id INT NOT NULL,
                test_name VARCHAR(255) NOT NULL,
                test_type VARCHAR(100) NOT NULL,
                test_description TEXT,
                test_date DATE NOT NULL,
                results TEXT,
                normal_range VARCHAR(255),
                status ENUM('ordered', 'completed', 'cancelled') DEFAULT 'ordered',
                lab_facility VARCHAR(255),
                technician_notes TEXT,
                doctor_notes TEXT,
                is_critical BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """))
        
        # Create medical_documents table
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS medical_documents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT NOT NULL,
                doctor_id INT,
                document_name VARCHAR(255) NOT NULL,
                document_type ENUM('lab_report', 'xray', 'prescription', 'discharge_summary', 'other') NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                file_size INT,
                mime_type VARCHAR(100),
                description TEXT,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_sensitive BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """))
        
        db.session.commit()
        print("   ✅ Lab tests and medical documents support added")
        
    except Exception as e:
        if "already exists" in str(e):
            print("   ⚠️  Lab tests tables already exist, skipping...")
        else:
            print(f"   ❌ Error adding lab tests support: {e}")
        db.session.rollback()

if __name__ == "__main__":
    print("\n🏥 HealthBridge AI - Complete Database Setup")
    print("=" * 50)
    
    response = input("⚠️  This will DROP all existing tables and recreate them. Continue? (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        success = create_complete_database()
        if success:
            print("\n🎉 Database setup completed successfully!")
            print("💡 You can now run your application with: python run.py")
        else:
            print("\n❌ Database setup failed. Please check the errors above.")
    else:
        print("\n✋ Database setup cancelled.")