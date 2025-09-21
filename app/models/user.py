from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    role = db.Column(db.String(20), nullable=False)  # 'patient' or 'doctor'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Additional fields for patients
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    address = db.Column(db.Text, nullable=True)
    emergency_contact = db.Column(db.String(100), nullable=True)
    emergency_contact_phone = db.Column(db.String(15), nullable=True)
    blood_type = db.Column(db.String(5), nullable=True)
    allergies = db.Column(db.Text, nullable=True)
    
    # Additional fields for doctors
    specialization = db.Column(db.String(100), nullable=True)
    license_number = db.Column(db.String(50), nullable=True)
    qualification = db.Column(db.String(100), nullable=True)
    experience = db.Column(db.Integer, nullable=True)
    consultation_fee = db.Column(db.Float, nullable=True, default=0.0)
    profile_photo = db.Column(db.String(255), nullable=True)  # Store photo filename
    rating = db.Column(db.Float, nullable=True, default=0.0)
    total_patients = db.Column(db.Integer, nullable=True, default=0)
    about = db.Column(db.Text, nullable=True)  # Doctor's bio/description
    
    # Doctor practice location fields
    practice_address = db.Column(db.Text, nullable=True)
    practice_city = db.Column(db.String(100), nullable=True)
    practice_state = db.Column(db.String(50), nullable=True)
    practice_zip_code = db.Column(db.String(20), nullable=True)
    practice_latitude = db.Column(db.Float, nullable=True)
    practice_longitude = db.Column(db.Float, nullable=True)
    practice_phone = db.Column(db.String(15), nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<User {self.email}>'