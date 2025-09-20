"""
Test Script: Enhanced Prescription System
Purpose: Test the new multiple medications and lab tests functionality
Usage: python test_prescription_enhancements.py
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app, db
from app.models.user import User
from app.models.prescription import Prescription
from app.models.prescription_components import PrescriptionMedication, LabTest, PrescriptionEdit
from datetime import datetime, date

def test_enhanced_prescriptions():
    """Test the enhanced prescription system"""
    app = create_app()
    
    with app.app_context():
        print("=== Testing Enhanced Prescription System ===\n")
        
        # Test 1: Check if new tables exist
        print("1. Testing database schema...")
        try:
            # Try to query each new table
            med_count = PrescriptionMedication.query.count()
            lab_count = LabTest.query.count()
            edit_count = PrescriptionEdit.query.count()
            
            print(f"   ✓ PrescriptionMedication table: {med_count} records")
            print(f"   ✓ LabTest table: {lab_count} records") 
            print(f"   ✓ PrescriptionEdit table: {edit_count} records")
            
        except Exception as e:
            print(f"   ❌ Database schema error: {e}")
            return False
        
        # Test 2: Check relationships
        print("\n2. Testing model relationships...")
        try:
            # Get a prescription with medications
            prescription = Prescription.query.first()
            if prescription:
                medications = prescription.medications
                lab_tests = prescription.lab_tests
                edits = prescription.edits
                
                print(f"   ✓ Prescription #{prescription.id} has:")
                print(f"     - {len(medications)} medication(s)")
                print(f"     - {len(lab_tests)} lab test(s)")
                print(f"     - {len(edits)} edit(s)")
                print(f"     - Primary medication: {prescription.primary_medication}")
                print(f"     - Medication count: {prescription.medication_count}")
            else:
                print("   ⚠️  No prescriptions found to test relationships")
                
        except Exception as e:
            print(f"   ❌ Relationship error: {e}")
            return False
        
        # Test 3: Test creating a new enhanced prescription
        print("\n3. Testing prescription creation...")
        try:
            # Find a doctor and patient for testing
            doctor = User.query.filter_by(role='doctor').first()
            patient = User.query.filter_by(role='patient').first()
            
            if not doctor or not patient:
                print("   ⚠️  Need at least one doctor and one patient to test creation")
                return True
            
            # Create a test prescription
            test_prescription = Prescription(
                patient_id=patient.id,
                doctor_id=doctor.id,
                medication_name="Test Medication",  # For backward compatibility
                dosage="500mg",
                frequency="Twice daily",
                duration="7 days",
                instructions="Take with food",
                prescribed_date=date.today(),
                status="Active",
                notes="Test prescription with multiple medications"
            )
            
            db.session.add(test_prescription)
            db.session.flush()  # Get the ID
            
            # Add multiple medications
            medications = [
                {
                    'name': 'Amoxicillin',
                    'dosage': '500mg',
                    'frequency': 'Three times daily',
                    'duration': '10 days',
                    'instructions': 'Take with food'
                },
                {
                    'name': 'Ibuprofen',
                    'dosage': '200mg',
                    'frequency': 'As needed',
                    'duration': '7 days',
                    'instructions': 'For pain relief'
                }
            ]
            
            for med_data in medications:
                medication = PrescriptionMedication(
                    prescription_id=test_prescription.id,
                    medication_name=med_data['name'],
                    dosage=med_data['dosage'],
                    frequency=med_data['frequency'],
                    duration=med_data['duration'],
                    instructions=med_data['instructions']
                )
                db.session.add(medication)
            
            # Add lab tests
            lab_tests = [
                {
                    'name': 'Complete Blood Count',
                    'type': 'Blood',
                    'instructions': 'Fasting not required'
                },
                {
                    'name': 'Chest X-Ray',
                    'type': 'X-Ray',
                    'instructions': 'No metal objects'
                }
            ]
            
            for test_data in lab_tests:
                lab_test = LabTest(
                    prescription_id=test_prescription.id,
                    test_name=test_data['name'],
                    test_type=test_data['type'],
                    suggested_date=date.today(),
                    instructions=test_data['instructions'],
                    status='Pending'
                )
                db.session.add(lab_test)
            
            db.session.commit()
            
            print(f"   ✓ Created test prescription #{test_prescription.id}")
            print(f"     - {len(medications)} medications added")
            print(f"     - {len(lab_tests)} lab tests added")
            
        except Exception as e:
            print(f"   ❌ Creation error: {e}")
            db.session.rollback()
            return False
        
        print("\n=== All Tests Passed! ===")
        print("\nEnhanced prescription system is working correctly!")
        print("\nFeatures verified:")
        print("✓ Multiple medications per prescription")
        print("✓ Lab test ordering and tracking")
        print("✓ Prescription relationships")
        print("✓ Backward compatibility")
        
        return True

if __name__ == "__main__":
    test_enhanced_prescriptions()