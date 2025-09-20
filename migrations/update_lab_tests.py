import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

app = create_app()
with app.app_context():
    try:
        db.session.execute(db.text('ALTER TABLE lab_tests ADD COLUMN priority VARCHAR(50) DEFAULT "Normal"'))
        print("Added priority column")
    except Exception as e:
        print(f"Priority column may already exist: {e}")
    
    try:
        db.session.execute(db.text('ALTER TABLE lab_tests ADD COLUMN ordered_by INT'))
        print("Added ordered_by column")
    except Exception as e:
        print(f"Ordered_by column may already exist: {e}")
    
    db.session.commit()
    print("Lab tests table updated")