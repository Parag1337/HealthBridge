#!/usr/bin/env python3
"""
Simple script to create a test patient account for testing purposes
"""
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from datetime import date

def create_test_accounts():
    """Create test patient and doctor accounts"""
    app = create_app()
    
    with app.app_context():
        # Check if test patient already exists
        test_patient = User.query.filter_by(email='testpatient@demo.com').first()
        if not test_patient:
            # Create test patient
            patient = User(
                email='testpatient@demo.com',
                first_name='Demo',
                last_name='Patient',
                phone='5551234567',
                role='patient',
                date_of_birth=date(1990, 1, 1),
                gender='male',
                address='123 Demo Street, Demo City'
            )
            patient.set_password('demo123')
            db.session.add(patient)
            print("✅ Created test patient: testpatient@demo.com / demo123")
        else:
            print("ℹ️ Test patient already exists: testpatient@demo.com / demo123")
        
        # Check if test doctor already exists (besides the existing one)
        test_doctor = User.query.filter_by(email='testdoctor@demo.com').first()
        if not test_doctor:
            # Create test doctor
            doctor = User(
                email='testdoctor@demo.com',
                first_name='Demo',
                last_name='Doctor',
                phone='5559876543',
                role='doctor',
                specialization='general',
                license_number='DEMO123',
                qualification='MBBS',
                experience=5
            )
            doctor.set_password('demo123')
            db.session.add(doctor)
            print("✅ Created test doctor: testdoctor@demo.com / demo123")
        else:
            print("ℹ️ Test doctor already exists: testdoctor@demo.com / demo123")
        
        try:
            db.session.commit()
            print("\n🎉 Test accounts ready!")
            print("\n📋 Login Credentials:")
            print("Patient: testpatient@demo.com / demo123")
            print("Doctor: testdoctor@demo.com / demo123")
            print("Sample Doctor: doctor@healthbridge.com / doctor123")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating test accounts: {e}")

if __name__ == "__main__":
    create_test_accounts()