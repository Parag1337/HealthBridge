from datetime import datetime
from app import db

class AppointmentFeedback(db.Model):
    __tablename__ = 'appointment_feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Rating fields (1-5 scale)
    overall_rating = db.Column(db.Integer, nullable=False)
    doctor_rating = db.Column(db.Integer, nullable=False)
    communication_rating = db.Column(db.Integer, nullable=False)
    punctuality_rating = db.Column(db.Integer, nullable=False)
    cleanliness_rating = db.Column(db.Integer, nullable=False)
    
    # Text feedback
    positive_feedback = db.Column(db.Text)
    negative_feedback = db.Column(db.Text)
    suggestions = db.Column(db.Text)
    
    # Would recommend
    would_recommend = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    appointment = db.relationship('Appointment', backref='feedback', uselist=False)
    patient = db.relationship('User', foreign_keys=[patient_id], backref='given_feedback')
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='received_feedback')
    
    def __repr__(self):
        return f'<AppointmentFeedback {self.id}: Rating {self.overall_rating}/5>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'overall_rating': self.overall_rating,
            'doctor_rating': self.doctor_rating,
            'communication_rating': self.communication_rating,
            'punctuality_rating': self.punctuality_rating,
            'cleanliness_rating': self.cleanliness_rating,
            'positive_feedback': self.positive_feedback,
            'negative_feedback': self.negative_feedback,
            'suggestions': self.suggestions,
            'would_recommend': self.would_recommend,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }