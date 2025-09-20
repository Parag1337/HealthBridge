"""
Database Migration: Add missing prescription columns
Purpose: Add columns that are in the model but missing from the database
"""

import sys
import os

# Add the parent directory to sys.path to find the app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from datetime import datetime

def add_missing_columns():
    """Add missing columns to the prescriptions table"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Adding missing columns to prescriptions table...")
            
            # List of columns to add if they don't exist
            columns_to_add = [
                ("duration", "VARCHAR(50)"),
                ("prescribed_date", "DATE"),
                ("status", "VARCHAR(20) DEFAULT 'Active'"),
                ("notes", "TEXT"),
                ("updated_at", "DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
            ]
            
            # Check existing columns
            result = db.session.execute(db.text("DESCRIBE prescriptions"))
            existing_columns = [row[0] for row in result.fetchall()]
            print(f"Existing columns: {existing_columns}")
            
            # Add missing columns
            added_columns = []
            for column_name, column_type in columns_to_add:
                if column_name not in existing_columns:
                    try:
                        sql = f"ALTER TABLE prescriptions ADD COLUMN {column_name} {column_type}"
                        db.session.execute(db.text(sql))
                        added_columns.append(column_name)
                        print(f"✓ Added column: {column_name}")
                    except Exception as e:
                        print(f"⚠️  Could not add {column_name}: {e}")
                else:
                    print(f"✓ Column {column_name} already exists")
            
            if added_columns:
                db.session.commit()
                print(f"\n✓ Successfully added {len(added_columns)} columns: {added_columns}")
            else:
                print("\n✓ All required columns already exist")
            
            # Update existing records with default values
            print("\nUpdating existing records with default values...")
            try:
                # Set default status for records without it
                db.session.execute(db.text("UPDATE prescriptions SET status = 'Active' WHERE status IS NULL"))
                
                # Set prescribed_date to created_at for records without it
                db.session.execute(db.text("UPDATE prescriptions SET prescribed_date = DATE(created_at) WHERE prescribed_date IS NULL"))
                
                # Set updated_at to created_at for records without it
                db.session.execute(db.text("UPDATE prescriptions SET updated_at = created_at WHERE updated_at IS NULL"))
                
                db.session.commit()
                print("✓ Updated existing records with default values")
                
            except Exception as e:
                print(f"⚠️  Could not update existing records: {e}")
                db.session.rollback()
            
            return True
            
        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("=== Adding Missing Prescription Columns ===")
    
    if add_missing_columns():
        print("\n🎉 Migration completed successfully!")
        print("\nPrescription table is now compatible with the enhanced model.")
    else:
        print("\n❌ Migration failed. Please check the errors above.")