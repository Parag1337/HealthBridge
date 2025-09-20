from datetime import datetime
from app import db

class Prescription(db.Model):
    __tablename__ = 'prescriptions'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    medication_name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.String(50), nullable=False)
    instructions = db.Column(db.Text, nullable=True)
    refills_remaining = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships to User model with different foreign keys
    patient = db.relationship('User', foreign_keys=[patient_id], backref='patient_prescriptions')
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='doctor_prescriptions')

    def __repr__(self):
        return f'<Prescription {self.medication_name} for Patient {self.patient_id}>'