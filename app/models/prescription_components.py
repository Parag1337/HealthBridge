from app import db
from datetime import datetime

class PrescriptionMedication(db.Model):
    __tablename__ = 'prescription_medications'
    
    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id'), nullable=False)
    medication_name = db.Column(db.String(200), nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.Text)
    status = db.Column(db.String(50), default='Active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship back to prescription
    prescription = db.relationship('Prescription', back_populates='medications')

class LabTest(db.Model):
    __tablename__ = 'lab_tests'
    
    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id'), nullable=False)
    test_name = db.Column(db.String(200), nullable=False)
    test_type = db.Column(db.String(100), nullable=False)  # Blood, Urine, X-Ray, MRI, etc.
    instructions = db.Column(db.Text)
    status = db.Column(db.String(50), default='Pending')  # Pending, Completed, In Progress
    priority = db.Column(db.String(50), default='Normal')  # Normal, Urgent, Immediate
    suggested_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)
    results = db.Column(db.Text)
    result_file_path = db.Column(db.String(500))
    ordered_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # Doctor who ordered the test
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship back to prescription
    prescription = db.relationship('Prescription', back_populates='lab_tests')
    # Relationship to the doctor who ordered the test
    ordering_doctor = db.relationship('User', foreign_keys=[ordered_by])

class PrescriptionEdit(db.Model):
    __tablename__ = 'prescription_edits'
    
    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    edit_reason = db.Column(db.String(200), nullable=False)  # Test results, Follow-up, etc.
    changes_made = db.Column(db.Text, nullable=False)
    lab_test_id = db.Column(db.Integer, db.ForeignKey('lab_tests.id'))  # If edit based on test results
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    prescription = db.relationship('Prescription', back_populates='edits')
    doctor = db.relationship('User')
    lab_test = db.relationship('LabTest')