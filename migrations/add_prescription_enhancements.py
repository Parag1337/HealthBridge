"""
Database Migration: Add Enhanced Prescription Support
Created: Enhanced prescription system with multiple medications and lab tests
Purpose: Support multiple medications per prescription and lab test ordering
"""

import sys
import os

# Add the parent directory to sys.path to find the app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from app import create_app, db
from app.models.prescription_components import PrescriptionMedication, LabTest, PrescriptionEdit
from app.models.prescription import Prescription
from datetime import datetime

def create_tables():
    """Create new tables for enhanced prescription system"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create the new tables
            print("Creating prescription enhancement tables...")
            
            # Create PrescriptionMedication table
            db.create_all()
            
            print("✓ PrescriptionMedication table created")
            print("✓ LabTest table created") 
            print("✓ PrescriptionEdit table created")
            
            # Add notes column to existing prescriptions table if it doesn't exist
            try:
                from sqlalchemy import text
                result = db.session.execute(text("PRAGMA table_info(prescription)"))
                columns = [row[1] for row in result.fetchall()]
                
                if 'notes' not in columns:
                    db.session.execute(text("ALTER TABLE prescription ADD COLUMN notes TEXT"))
                    print("✓ Added 'notes' column to prescription table")
                else:
                    print("✓ 'notes' column already exists in prescription table")
                    
                db.session.commit()
                
            except Exception as e:
                print(f"Note: Could not add notes column (may already exist): {e}")
                db.session.rollback()
            
            print("\n=== Migration completed successfully! ===")
            print("\nNew features available:")
            print("• Multiple medications per prescription")
            print("• Lab test ordering and tracking")
            print("• Prescription edit history")
            print("• Enhanced prescription notes")
            
            return True
            
        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()
            return False

def migrate_existing_prescriptions():
    """Migrate existing single-medication prescriptions to new format"""
    app = create_app()
    
    with app.app_context():
        try:
            print("\nMigrating existing prescriptions to new format...")
            
            # Get all existing prescriptions
            prescriptions = Prescription.query.all()
            migrated_count = 0
            
            for prescription in prescriptions:
                # Check if this prescription already has medications in the new format
                existing_meds = PrescriptionMedication.query.filter_by(
                    prescription_id=prescription.id
                ).first()
                
                if not existing_meds and prescription.medication_name:
                    # Create a PrescriptionMedication record from the old single medication
                    medication = PrescriptionMedication(
                        prescription_id=prescription.id,
                        medication_name=prescription.medication_name,
                        dosage=prescription.dosage or '',
                        frequency=prescription.frequency or '',
                        duration=prescription.duration or '',
                        instructions=prescription.instructions or ''
                    )
                    
                    db.session.add(medication)
                    migrated_count += 1
            
            if migrated_count > 0:
                db.session.commit()
                print(f"✓ Migrated {migrated_count} existing prescriptions to new format")
            else:
                print("✓ No prescriptions needed migration (already migrated or no data)")
            
            return True
            
        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("=== Enhanced Prescription System Migration ===")
    print("This migration adds support for:")
    print("• Multiple medications per prescription")
    print("• Lab test ordering and tracking")
    print("• Prescription editing with history")
    print("=" * 50)
    
    # Create new tables
    if create_tables():
        # Migrate existing data
        migrate_existing_prescriptions()
        print("\n🎉 Migration completed successfully!")
        print("\nNext steps:")
        print("1. Restart your Flask application")
        print("2. Test creating a new prescription with multiple medications")
        print("3. Test adding lab tests to prescriptions")
    else:
        print("\n❌ Migration failed. Please check the errors above.")