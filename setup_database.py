#!/usr/bin/env python3
"""
Database setup script for HealthBridge
This script initializes the database with all required tables
"""
import os
from app import create_app, db
from app.models.user import User
from app.models.appointment import Appointment
from app.models.prescription import Prescription, PrescriptionMedication, LabTest
from app.models.telemedicine import VideoConsultation
from app.models.scheduling import DoctorSchedule, SlotConfiguration

def setup_database():
    """Initialize database with all tables"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Creating database tables...")
            
            # Create all tables
            db.create_all()
            
            print("✅ Database tables created successfully!")
            
            # Check if tables exist
            tables = db.engine.table_names()
            print(f"📋 Created tables: {', '.join(tables)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting up database: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    if setup_database():
        print("🎉 Database setup completed successfully!")
    else:
        print("💥 Database setup failed!")
        exit(1)