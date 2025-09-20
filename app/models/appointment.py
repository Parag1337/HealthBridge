from datetime import datetime
from app import db

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    reason = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships to User model with different foreign keys
    patient = db.relationship('User', foreign_keys=[patient_id], backref='patient_appointments')
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='doctor_appointments')

    def __repr__(self):
        return f'<Appointment {self.id} - Patient {self.patient_id} with Doctor {self.doctor_id} on {self.date} at {self.time}>'