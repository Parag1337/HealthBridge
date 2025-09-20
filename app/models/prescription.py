from datetime import datetime
from app import db

class Prescription(db.Model):
    __tablename__ = 'prescriptions'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Legacy fields for backward compatibility
    medication_name = db.Column(db.String(100), nullable=True)
    dosage = db.Column(db.String(50), nullable=True)
    frequency = db.Column(db.String(50), nullable=True)
    duration = db.Column(db.String(100), nullable=True)
    instructions = db.Column(db.Text, nullable=True)
    
    # New fields
    prescribed_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default='Active')
    notes = db.Column(db.Text, nullable=True)
    refills_remaining = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships to User model with different foreign keys
    patient = db.relationship('User', foreign_keys=[patient_id], backref='patient_prescriptions')
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='doctor_prescriptions')
    
    # New relationships to support multiple medications and tests
    medications = db.relationship('PrescriptionMedication', back_populates='prescription', cascade='all, delete-orphan')
    lab_tests = db.relationship('LabTest', back_populates='prescription', cascade='all, delete-orphan')
    edits = db.relationship('PrescriptionEdit', back_populates='prescription', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Prescription {self.id} for Patient {self.patient_id}>'
    
    @property
    def primary_medication(self):
        """Return the first medication or legacy medication_name for display"""
        if self.medications:
            return self.medications[0].medication_name
        return self.medication_name or "No medication specified"
    
    @property
    def medication_count(self):
        """Return count of medications in this prescription"""
        return len(self.medications) if self.medications else (1 if self.medication_name else 0)
    
    @property
    def has_pending_tests(self):
        """Check if prescription has pending lab tests"""
        return any(test.status == 'Pending' for test in self.lab_tests) if self.lab_tests else False