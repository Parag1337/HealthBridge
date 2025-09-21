from datetime import datetime
from app import db

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    reason = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, confirmed, in-progress, completed, cancelled
    appointment_type = db.Column(db.String(20), default='in-person')  # in-person, online, hybrid
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional fields for appointment management
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    # Telemedicine fields
    telemedicine_platform = db.Column(db.String(50), nullable=True)  # zoom, google-meet, etc.
    telemedicine_link = db.Column(db.Text, nullable=True)  # Meeting link
    consultation_fee = db.Column(db.Numeric(10, 2), nullable=True)  # Fee for consultation

    # Relationships to User model with different foreign keys
    patient = db.relationship('User', foreign_keys=[patient_id], backref='patient_appointments')
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='doctor_appointments')

    def __repr__(self):
        return f'<Appointment {self.id} - Patient {self.patient_id} with Doctor {self.doctor_id} on {self.date} at {self.time}>'
    
    def can_provide_feedback(self):
        """Check if appointment is eligible for feedback"""
        return self.status == 'completed' and self.completed_at is not None
    
    def has_feedback(self):
        """Check if feedback has been provided for this appointment"""
        return hasattr(self, 'feedback') and self.feedback is not None
    
    def is_telemedicine(self):
        """Check if this is a telemedicine appointment"""
        return self.appointment_type in ['online', 'telemedicine']
    
    def has_video_consultation(self):
        """Check if this appointment has an associated video consultation"""
        return hasattr(self, 'video_consultation') and self.video_consultation is not None
    
    def start_appointment(self):
        """Mark appointment as started"""
        self.status = 'in-progress'
        self.started_at = datetime.utcnow()
        db.session.commit()
    
    def complete_appointment(self):
        """Mark appointment as completed"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        db.session.commit()
    
    def cancel_appointment(self, reason=None):
        """Cancel the appointment"""
        self.status = 'cancelled'
        if reason:
            self.notes = f"Cancelled: {reason}"
        db.session.commit()
    
    def to_dict(self):
        """Convert appointment to dictionary"""
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'time': self.time.strftime('%H:%M') if self.time else None,
            'reason': self.reason,
            'status': self.status,
            'appointment_type': self.appointment_type,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'notes': self.notes,
            'telemedicine_platform': self.telemedicine_platform,
            'telemedicine_link': self.telemedicine_link,
            'consultation_fee': float(self.consultation_fee) if self.consultation_fee else None,
            'has_feedback': self.has_feedback(),
            'can_provide_feedback': self.can_provide_feedback(),
            'is_telemedicine': self.is_telemedicine(),
            'has_video_consultation': self.has_video_consultation()
        }