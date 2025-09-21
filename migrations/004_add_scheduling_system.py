"""
Database migration for hybrid appointment scheduling system
Adds tables for doctor schedules, slot configurations, availability overrides, 
time slots, and recurring schedule tracking.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.scheduling import (
    DoctorSchedule, SlotConfiguration, AvailabilityOverride, 
    TimeSlot, RecurringSchedule
)

def run_migration():
    """Run the scheduling system migration"""
    
    print("Starting hybrid scheduling system database migration...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Create all new tables
            print("Creating scheduling tables...")
            
            # DoctorSchedule table
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS doctor_schedules (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    doctor_id INT NOT NULL,
                    day_of_week INT NOT NULL,
                    start_time TIME NOT NULL,
                    end_time TIME NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (doctor_id) REFERENCES users (id)
                )
            """))
            
            # SlotConfiguration table
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS slot_configurations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    doctor_id INT NOT NULL UNIQUE,
                    slot_duration_minutes INT DEFAULT 30,
                    buffer_time_minutes INT DEFAULT 5,
                    max_patients_per_day INT DEFAULT 20,
                    advance_booking_days INT DEFAULT 30,
                    last_minute_booking_hours INT DEFAULT 2,
                    auto_generate_slots BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (doctor_id) REFERENCES users (id)
                )
            """))
            
            # AvailabilityOverride table
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS availability_overrides (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    doctor_id INT NOT NULL,
                    date DATE NOT NULL,
                    override_type VARCHAR(20) NOT NULL,
                    start_time TIME,
                    end_time TIME,
                    reason VARCHAR(200),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (doctor_id) REFERENCES users (id)
                )
            """))
            
            # TimeSlot table
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS time_slots (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    doctor_id INT NOT NULL,
                    date DATE NOT NULL,
                    start_time TIME NOT NULL,
                    end_time TIME NOT NULL,
                    status VARCHAR(20) DEFAULT 'available',
                    appointment_id INT,
                    generated_from VARCHAR(20) DEFAULT 'schedule',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (doctor_id) REFERENCES users (id),
                    FOREIGN KEY (appointment_id) REFERENCES appointments (id)
                )
            """))
            
            # Create index for efficient time slot queries (with error handling)
            try:
                db.session.execute(db.text("""
                    CREATE INDEX idx_doctor_date_time 
                    ON time_slots (doctor_id, date, start_time)
                """))
            except Exception as idx_error:
                # Index might already exist, that's okay
                print(f"Index creation skipped (may already exist): {idx_error}")
                pass
            
            # RecurringSchedule table
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS recurring_schedules (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    doctor_id INT NOT NULL,
                    week_start_date DATE NOT NULL,
                    slots_generated BOOLEAN DEFAULT FALSE,
                    generation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (doctor_id) REFERENCES users (id),
                    UNIQUE KEY unique_doctor_week (doctor_id, week_start_date)
                )
            """))
            
            # Create default slot configurations for existing doctors
            print("Creating default slot configurations for existing doctors...")
            
            # Get all doctors
            doctors = db.session.execute(db.text("""
                SELECT id FROM users WHERE role = 'doctor'
            """)).fetchall()
            
            for doctor in doctors:
                doctor_id = doctor[0]
                
                # Check if configuration already exists
                existing = db.session.execute(db.text("""
                    SELECT id FROM slot_configurations WHERE doctor_id = :doctor_id
                """), {"doctor_id": doctor_id}).fetchone()
                
                if not existing:
                    # Create default configuration
                    db.session.execute(db.text("""
                        INSERT INTO slot_configurations 
                        (doctor_id, slot_duration_minutes, buffer_time_minutes, 
                         max_patients_per_day, advance_booking_days, last_minute_booking_hours, 
                         auto_generate_slots)
                        VALUES (:doctor_id, 30, 5, 20, 30, 2, 1)
                    """), {"doctor_id": doctor_id})
                    print(f"Created default slot configuration for doctor ID: {doctor_id}")
            
            # Commit the transaction
            db.session.commit()
            
            print("✅ Hybrid scheduling system migration completed successfully!")
            print("📋 Created tables:")
            print("   - doctor_schedules (weekly working hours)")
            print("   - slot_configurations (doctor preferences)")
            print("   - availability_overrides (manual adjustments)")
            print("   - time_slots (bookable slots)")
            print("   - recurring_schedules (generation tracking)")
            print("🔧 Added default configurations for existing doctors")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            db.session.rollback()
            raise e

if __name__ == "__main__":
    run_migration()