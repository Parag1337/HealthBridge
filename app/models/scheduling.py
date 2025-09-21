from datetime import datetime, time
from app import db

class DoctorSchedule(db.Model):
    """
    Doctor's weekly working hours template
    """
    __tablename__ = 'doctor_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    doctor = db.relationship('User', backref='weekly_schedules')
    
    def __repr__(self):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return f'<DoctorSchedule Dr.{self.doctor_id} {days[self.day_of_week]} {self.start_time}-{self.end_time}>'

class SlotConfiguration(db.Model):
    """
    Doctor's slot preferences and settings
    """
    __tablename__ = 'slot_configurations'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    slot_duration_minutes = db.Column(db.Integer, default=30)  # 15, 30, 45, 60 minutes
    buffer_time_minutes = db.Column(db.Integer, default=5)    # Gap between appointments
    max_patients_per_day = db.Column(db.Integer, default=20)  # Daily limit
    advance_booking_days = db.Column(db.Integer, default=30)  # How far in advance patients can book
    last_minute_booking_hours = db.Column(db.Integer, default=2)  # Minimum hours before appointment
    auto_generate_slots = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    doctor = db.relationship('User', backref='slot_configuration')
    
    def __repr__(self):
        return f'<SlotConfig Dr.{self.doctor_id} {self.slot_duration_minutes}min slots>'

class AvailabilityOverride(db.Model):
    """
    Manual adjustments to doctor's availability on specific dates
    """
    __tablename__ = 'availability_overrides'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    override_type = db.Column(db.String(20), nullable=False)  # 'unavailable', 'custom_hours', 'closed'
    start_time = db.Column(db.Time, nullable=True)  # For custom hours
    end_time = db.Column(db.Time, nullable=True)    # For custom hours
    reason = db.Column(db.String(200), nullable=True)  # Holiday, Emergency, etc.
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    doctor = db.relationship('User', backref='availability_overrides')
    
    def __repr__(self):
        return f'<Override Dr.{self.doctor_id} {self.date} {self.override_type}>'

class TimeSlot(db.Model):
    """
    Generated time slots available for booking
    """
    __tablename__ = 'time_slots'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='available')  # available, booked, blocked
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=True)
    generated_from = db.Column(db.String(20), default='schedule')  # schedule, override, manual
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    doctor = db.relationship('User', backref='time_slots')
    appointment = db.relationship('Appointment', backref='time_slot')
    
    # Composite index for efficient queries
    __table_args__ = (
        db.Index('idx_doctor_date_time', 'doctor_id', 'date', 'start_time'),
    )
    
    def __repr__(self):
        return f'<TimeSlot Dr.{self.doctor_id} {self.date} {self.start_time}-{self.end_time} {self.status}>'

class RecurringSchedule(db.Model):
    """
    Tracks recurring schedule generation to avoid duplicates
    """
    __tablename__ = 'recurring_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    week_start_date = db.Column(db.Date, nullable=False)  # Monday of the week
    slots_generated = db.Column(db.Boolean, default=False)
    generation_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    doctor = db.relationship('User', backref='recurring_schedules')
    
    # Composite unique constraint
    __table_args__ = (
        db.UniqueConstraint('doctor_id', 'week_start_date', name='unique_doctor_week'),
    )
    
    def __repr__(self):
        return f'<RecurringSchedule Dr.{self.doctor_id} Week:{self.week_start_date}>'