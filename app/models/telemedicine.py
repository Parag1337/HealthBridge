from datetime import datetime
from app import db
import secrets

class VideoConsultation(db.Model):
    __tablename__ = 'video_consultations'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Video consultation details
    room_id = db.Column(db.String(100), unique=True, nullable=False)
    meeting_url = db.Column(db.String(500))
    status = db.Column(db.String(20), default='scheduled')  # scheduled, active, completed, cancelled
    
    # Technical details
    platform = db.Column(db.String(50), default='webrtc')  # webrtc, zoom, meet, etc.
    duration_minutes = db.Column(db.Integer)
    actual_start_time = db.Column(db.DateTime)
    actual_end_time = db.Column(db.DateTime)
    
    # Connection details
    patient_joined_at = db.Column(db.DateTime)
    doctor_joined_at = db.Column(db.DateTime)
    connection_quality = db.Column(db.String(20))  # excellent, good, fair, poor
    
    # Session recording (optional)
    recording_enabled = db.Column(db.Boolean, default=False)
    recording_url = db.Column(db.String(500))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    appointment = db.relationship('Appointment', backref='video_consultation', uselist=False)
    patient = db.relationship('User', foreign_keys=[patient_id])
    doctor = db.relationship('User', foreign_keys=[doctor_id])
    
    def __init__(self, **kwargs):
        super(VideoConsultation, self).__init__(**kwargs)
        if not self.room_id:
            self.room_id = self.generate_room_id()
    
    @staticmethod
    def generate_room_id():
        return f"room_{secrets.token_urlsafe(16)}"
    
    def start_consultation(self):
        self.status = 'active'
        self.actual_start_time = datetime.utcnow()
        db.session.commit()
    
    def end_consultation(self):
        self.status = 'completed'
        self.actual_end_time = datetime.utcnow()
        if self.actual_start_time:
            duration = self.actual_end_time - self.actual_start_time
            self.duration_minutes = int(duration.total_seconds() / 60)
        db.session.commit()
    
    def patient_join(self):
        self.patient_joined_at = datetime.utcnow()
        db.session.commit()
    
    def doctor_join(self):
        self.doctor_joined_at = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<VideoConsultation {self.id}: {self.room_id} - {self.status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'room_id': self.room_id,
            'meeting_url': self.meeting_url,
            'status': self.status,
            'platform': self.platform,
            'duration_minutes': self.duration_minutes,
            'actual_start_time': self.actual_start_time.isoformat() if self.actual_start_time else None,
            'actual_end_time': self.actual_end_time.isoformat() if self.actual_end_time else None,
            'patient_joined_at': self.patient_joined_at.isoformat() if self.patient_joined_at else None,
            'doctor_joined_at': self.doctor_joined_at.isoformat() if self.doctor_joined_at else None,
            'connection_quality': self.connection_quality,
            'recording_enabled': self.recording_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }