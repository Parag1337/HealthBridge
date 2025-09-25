#!/usr/bin/env python3
"""
Sample Data Population Script for HealthBridge AI
This script creates realistic sample data for all database tables.
"""

import os
import sys
from datetime import datetime, date, time, timedelta
from decimal import Decimal
import random
from faker import Faker

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.appointment import Appointment
from app.models.prescription import Prescription
from app.models.prescription_components import PrescriptionMedication, LabTest, PrescriptionEdit
from app.models.telemedicine import VideoConsultation
from app.models.scheduling import DoctorSchedule, SlotConfiguration
from app.models.feedback import AppointmentFeedback

# Initialize Faker for generating realistic data
fake = Faker()

def create_sample_users():
    """Create sample patients, doctors, and admin users"""
    print("Creating sample users...")
    
    users_created = []
    
    # Create Admin User
    admin = User(
        email="admin@healthbridge.com",
        first_name="Admin",
        last_name="User",
        phone="+1-555-0001",
        role="admin",
        is_active=True
    )
    admin.set_password("admin123")
    db.session.add(admin)
    users_created.append(admin)
    
    # Sample Doctor Data
    doctors_data = [
        {
            "email": "dr.smith@healthbridge.com",
            "first_name": "John",
            "last_name": "Smith",
            "specialization": "Cardiology",
            "qualification": "MD, Cardiology",
            "experience": 15,
            "consultation_fee": 250.00,
            "bio": "Experienced cardiologist with expertise in interventional cardiology and heart disease prevention.",
            "hospital_affiliation": "Central Medical Hospital",
            "practice_city": "New York",
            "practice_state": "NY"
        },
        {
            "email": "dr.johnson@healthbridge.com",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "specialization": "Pediatrics",
            "qualification": "MD, Pediatrics",
            "experience": 12,
            "consultation_fee": 200.00,
            "bio": "Pediatrician specializing in child development and preventive care.",
            "hospital_affiliation": "Children's Medical Center",
            "practice_city": "Los Angeles",
            "practice_state": "CA"
        },
        {
            "email": "dr.williams@healthbridge.com",
            "first_name": "Michael",
            "last_name": "Williams",
            "specialization": "Orthopedics",
            "qualification": "MD, Orthopedic Surgery",
            "experience": 18,
            "consultation_fee": 300.00,
            "bio": "Orthopedic surgeon with expertise in sports medicine and joint replacement.",
            "hospital_affiliation": "Sports Medicine Institute",
            "practice_city": "Chicago",
            "practice_state": "IL"
        },
        {
            "email": "dr.brown@healthbridge.com",
            "first_name": "Emily",
            "last_name": "Brown",
            "specialization": "Dermatology",
            "qualification": "MD, Dermatology",
            "experience": 10,
            "consultation_fee": 180.00,
            "bio": "Dermatologist specializing in skin cancer prevention and cosmetic procedures.",
            "hospital_affiliation": "Skin Care Medical Group",
            "practice_city": "Miami",
            "practice_state": "FL"
        },
        {
            "email": "dr.davis@healthbridge.com",
            "first_name": "Robert",
            "last_name": "Davis",
            "specialization": "Neurology",
            "qualification": "MD, PhD, Neurology",
            "experience": 20,
            "consultation_fee": 350.00,
            "bio": "Neurologist and researcher specializing in brain disorders and neurological conditions.",
            "hospital_affiliation": "Neurological Institute",
            "practice_city": "Boston",
            "practice_state": "MA"
        }
    ]
    
    # Create doctors
    for doc_data in doctors_data:
        doctor = User(
            email=doc_data["email"],
            first_name=doc_data["first_name"],
            last_name=doc_data["last_name"],
            phone=fake.phone_number()[:15],
            role="doctor",
            specialization=doc_data["specialization"],
            license_number=f"MD{random.randint(100000, 999999)}",
            qualification=doc_data["qualification"],
            experience=doc_data["experience"],
            consultation_fee=doc_data["consultation_fee"],
            bio=doc_data["bio"],
            hospital_affiliation=doc_data["hospital_affiliation"],
            practice_address=fake.street_address(),
            practice_city=doc_data["practice_city"],
            practice_state=doc_data["practice_state"],
            practice_zip_code=fake.zipcode(),
            practice_phone=fake.phone_number()[:15],
            rating=round(random.uniform(4.0, 5.0), 1),
            total_patients=random.randint(50, 200)
        )
        doctor.set_password("doctor123")
        db.session.add(doctor)
        users_created.append(doctor)
    
    # Sample Patient Data
    patients_data = [
        {
            "email": "patient1@example.com",
            "first_name": "Alice",
            "last_name": "Wilson",
            "date_of_birth": date(1985, 3, 15),
            "gender": "Female",
            "blood_type": "A+",
            "allergies": "Penicillin"
        },
        {
            "email": "patient2@example.com",
            "first_name": "Bob",
            "last_name": "Martinez",
            "date_of_birth": date(1978, 7, 22),
            "gender": "Male",
            "blood_type": "O-",
            "allergies": "None"
        },
        {
            "email": "patient3@example.com",
            "first_name": "Carol",
            "last_name": "Taylor",
            "date_of_birth": date(1992, 11, 8),
            "gender": "Female",
            "blood_type": "B+",
            "allergies": "Shellfish, Latex"
        },
        {
            "email": "patient4@example.com",
            "first_name": "David",
            "last_name": "Anderson",
            "date_of_birth": date(1965, 5, 30),
            "gender": "Male",
            "blood_type": "AB+",
            "allergies": "Aspirin"
        },
        {
            "email": "patient5@example.com",
            "first_name": "Emma",
            "last_name": "Thompson",
            "date_of_birth": date(1990, 9, 12),
            "gender": "Female",
            "blood_type": "A-",
            "allergies": "None"
        },
        {
            "email": "patient6@example.com",
            "first_name": "Frank",
            "last_name": "Garcia",
            "date_of_birth": date(1982, 1, 25),
            "gender": "Male",
            "blood_type": "O+",
            "allergies": "Peanuts"
        },
        {
            "email": "patient7@example.com",
            "first_name": "Grace",
            "last_name": "Lee",
            "date_of_birth": date(1988, 4, 18),
            "gender": "Female",
            "blood_type": "B-",
            "allergies": "Sulfa drugs"
        },
        {
            "email": "patient8@example.com",
            "first_name": "Henry",
            "last_name": "Clark",
            "date_of_birth": date(1975, 12, 3),
            "gender": "Male",
            "blood_type": "A+",
            "allergies": "None"
        }
    ]
    
    # Create patients
    for pat_data in patients_data:
        patient = User(
            email=pat_data["email"],
            first_name=pat_data["first_name"],
            last_name=pat_data["last_name"],
            phone=fake.phone_number()[:15],
            role="patient",
            date_of_birth=pat_data["date_of_birth"],
            gender=pat_data["gender"],
            address=fake.address(),
            emergency_contact=fake.name(),
            emergency_contact_phone=fake.phone_number()[:15],
            blood_type=pat_data["blood_type"],
            allergies=pat_data["allergies"]
        )
        patient.set_password("patient123")
        db.session.add(patient)
        users_created.append(patient)
    
    db.session.commit()
    print(f"Created {len(users_created)} users (1 admin, {len(doctors_data)} doctors, {len(patients_data)} patients)")
    return users_created

def create_doctor_schedules():
    """Create sample doctor schedules"""
    print("Creating doctor schedules...")
    
    doctors = User.query.filter_by(role='doctor').all()
    schedules_created = 0
    
    for doctor in doctors:
        # Create slot configuration
        slot_config = SlotConfiguration(
            doctor_id=doctor.id,
            slot_duration_minutes=random.choice([30, 45, 60]),
            buffer_time_minutes=random.choice([5, 10, 15]),
            max_patients_per_day=random.randint(15, 25),
            advance_booking_days=30,
            last_minute_booking_hours=2
        )
        db.session.add(slot_config)
        
        # Create weekly schedule (Monday to Friday)
        for day in range(5):  # 0=Monday to 4=Friday
            # Morning session
            morning_start = time(9, 0)
            morning_end = time(12, 0)
            morning_schedule = DoctorSchedule(
                doctor_id=doctor.id,
                day_of_week=day,
                start_time=morning_start,
                end_time=morning_end
            )
            db.session.add(morning_schedule)
            schedules_created += 1
            
            # Afternoon session
            afternoon_start = time(14, 0)
            afternoon_end = time(17, 0)
            afternoon_schedule = DoctorSchedule(
                doctor_id=doctor.id,
                day_of_week=day,
                start_time=afternoon_start,
                end_time=afternoon_end
            )
            db.session.add(afternoon_schedule)
            schedules_created += 1
        
        # Some doctors also work on Saturday
        if random.choice([True, False]):
            saturday_schedule = DoctorSchedule(
                doctor_id=doctor.id,
                day_of_week=5,  # Saturday
                start_time=time(9, 0),
                end_time=time(13, 0)
            )
            db.session.add(saturday_schedule)
            schedules_created += 1
    
    db.session.commit()
    print(f"Created {schedules_created} doctor schedule entries")

def create_appointments():
    """Create sample appointments"""
    print("Creating sample appointments...")
    
    doctors = User.query.filter_by(role='doctor').all()
    patients = User.query.filter_by(role='patient').all()
    
    appointments_created = []
    appointment_statuses = ['scheduled', 'confirmed', 'completed', 'cancelled']
    appointment_types = ['in-person', 'online', 'telemedicine']
    
    # Create appointments for the past 30 days and future 30 days
    for _ in range(50):  # Create 50 appointments
        doctor = random.choice(doctors)
        patient = random.choice(patients)
        
        # Random date within 60 days (30 past, 30 future)
        days_offset = random.randint(-30, 30)
        appointment_date = date.today() + timedelta(days=days_offset)
        
        # Random time during business hours
        hour = random.randint(9, 16)
        minute = random.choice([0, 15, 30, 45])
        appointment_time = time(hour, minute)
        
        status = random.choice(appointment_statuses)
        if days_offset < 0:  # Past appointments
            status = random.choice(['completed', 'cancelled'])
        
        appointment = Appointment(
            date=appointment_date,
            time=appointment_time,
            reason=fake.sentence(nb_words=6),
            status=status,
            appointment_type=random.choice(appointment_types),
            patient_id=patient.id,
            doctor_id=doctor.id,
            consultation_fee=doctor.consultation_fee,
            notes=fake.text(max_nb_chars=200) if random.choice([True, False]) else None
        )
        
        # Set completion times for completed appointments
        if status == 'completed':
            appointment.started_at = datetime.combine(appointment_date, appointment_time)
            appointment.completed_at = appointment.started_at + timedelta(minutes=random.randint(30, 60))
        
        db.session.add(appointment)
        appointments_created.append(appointment)
    
    db.session.commit()
    print(f"Created {len(appointments_created)} appointments")
    return appointments_created

def create_prescriptions():
    """Create sample prescriptions"""
    print("Creating sample prescriptions...")
    
    completed_appointments = Appointment.query.filter_by(status='completed').all()
    prescriptions_created = []
    
    # Create prescriptions for about 70% of completed appointments
    for appointment in completed_appointments:
        if random.random() < 0.7:  # 70% chance
            prescription = Prescription(
                patient_id=appointment.patient_id,
                doctor_id=appointment.doctor_id,
                prescribed_date=appointment.date,
                status=random.choice(['Active', 'Completed', 'Cancelled']),
                notes=fake.text(max_nb_chars=150),
                refills_remaining=random.randint(0, 5)
            )
            db.session.add(prescription)
            prescriptions_created.append(prescription)
    
    db.session.commit()
    
    # Create prescription medications
    medications_data = [
        {"name": "Amoxicillin", "dosage": "500mg", "frequency": "3 times daily", "duration": "7 days"},
        {"name": "Lisinopril", "dosage": "10mg", "frequency": "Once daily", "duration": "30 days"},
        {"name": "Metformin", "dosage": "850mg", "frequency": "Twice daily", "duration": "90 days"},
        {"name": "Atorvastatin", "dosage": "20mg", "frequency": "Once daily", "duration": "30 days"},
        {"name": "Omeprazole", "dosage": "20mg", "frequency": "Once daily", "duration": "14 days"},
        {"name": "Ibuprofen", "dosage": "400mg", "frequency": "As needed", "duration": "10 days"},
        {"name": "Hydrochlorothiazide", "dosage": "25mg", "frequency": "Once daily", "duration": "30 days"},
        {"name": "Prednisone", "dosage": "5mg", "frequency": "Twice daily", "duration": "5 days"}
    ]
    
    medications_created = 0
    for prescription in prescriptions_created:
        # Each prescription can have 1-3 medications
        num_medications = random.randint(1, 3)
        for _ in range(num_medications):
            med_data = random.choice(medications_data)
            medication = PrescriptionMedication(
                prescription_id=prescription.id,
                medication_name=med_data["name"],
                dosage=med_data["dosage"],
                frequency=med_data["frequency"],
                duration=med_data["duration"],
                instructions=fake.sentence(nb_words=8),
                status=random.choice(['Active', 'Completed'])
            )
            db.session.add(medication)
            medications_created += 1
    
    db.session.commit()
    print(f"Created {len(prescriptions_created)} prescriptions with {medications_created} medications")

def create_telemedicine_sessions():
    """Create sample telemedicine video consultations"""
    print("Creating telemedicine sessions...")
    
    online_appointments = Appointment.query.filter(
        Appointment.appointment_type.in_(['online', 'telemedicine'])
    ).all()
    
    sessions_created = []
    for appointment in online_appointments:
        video_consultation = VideoConsultation(
            appointment_id=appointment.id,
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id,
            platform=random.choice(['webrtc', 'zoom', 'google-meet']),
            status='completed' if appointment.status == 'completed' else 'scheduled',
            recording_enabled=random.choice([True, False])
        )
        
        if appointment.status == 'completed':
            # Set realistic join and duration times
            video_consultation.patient_joined_at = appointment.started_at + timedelta(minutes=random.randint(0, 5))
            video_consultation.doctor_joined_at = appointment.started_at + timedelta(minutes=random.randint(0, 3))
            video_consultation.actual_start_time = max(video_consultation.patient_joined_at, video_consultation.doctor_joined_at)
            video_consultation.actual_end_time = appointment.completed_at
            video_consultation.duration_minutes = random.randint(20, 45)
            video_consultation.connection_quality = random.choice(['excellent', 'good', 'fair'])
        
        db.session.add(video_consultation)
        sessions_created.append(video_consultation)
    
    db.session.commit()
    print(f"Created {len(sessions_created)} telemedicine sessions")

def create_feedback():
    """Create sample appointment feedback"""
    print("Creating appointment feedback...")
    
    completed_appointments = Appointment.query.filter_by(status='completed').all()
    feedback_created = []
    
    # Create feedback for about 60% of completed appointments
    for appointment in completed_appointments:
        if random.random() < 0.6:  # 60% chance
            feedback = AppointmentFeedback(
                appointment_id=appointment.id,
                patient_id=appointment.patient_id,
                doctor_id=appointment.doctor_id,
                overall_rating=random.randint(3, 5),
                doctor_rating=random.randint(3, 5),
                communication_rating=random.randint(3, 5),
                punctuality_rating=random.randint(3, 5),
                cleanliness_rating=random.randint(3, 5),
                positive_feedback=fake.paragraph(nb_sentences=2),
                negative_feedback=fake.sentence() if random.choice([True, False]) else None,
                suggestions=fake.sentence() if random.choice([True, False]) else None,
                would_recommend=random.choice([True, True, True, False])  # 75% would recommend
            )
            db.session.add(feedback)
            feedback_created.append(feedback)
    
    db.session.commit()
    print(f"Created {len(feedback_created)} feedback entries")

def create_lab_tests():
    """Create sample lab tests"""
    print("Creating lab tests...")
    
    prescriptions = Prescription.query.all()
    tests_created = 0
    
    test_types = [
        {"name": "Complete Blood Count", "type": "Blood"},
        {"name": "Lipid Panel", "type": "Blood"},
        {"name": "Comprehensive Metabolic Panel", "type": "Blood"},
        {"name": "Urinalysis", "type": "Urine"},
        {"name": "Chest X-Ray", "type": "X-Ray"},
        {"name": "MRI Brain", "type": "MRI"},
        {"name": "ECG", "type": "Cardiac"},
        {"name": "Thyroid Function Test", "type": "Blood"}
    ]
    
    # Add lab tests to some prescriptions
    for prescription in prescriptions:
        if random.random() < 0.3:  # 30% of prescriptions have lab tests
            num_tests = random.randint(1, 2)
            for _ in range(num_tests):
                test_data = random.choice(test_types)
                lab_test = LabTest(
                    prescription_id=prescription.id,
                    test_name=test_data["name"],
                    test_type=test_data["type"],
                    instructions=fake.sentence(nb_words=8),
                    status=random.choice(['Pending', 'Completed', 'In Progress']),
                    priority=random.choice(['Normal', 'Urgent']),
                    suggested_date=date.today() + timedelta(days=random.randint(1, 14)),
                    ordered_by=prescription.doctor_id
                )
                
                if lab_test.status == 'Completed':
                    lab_test.completed_date = lab_test.suggested_date + timedelta(days=random.randint(0, 3))
                    lab_test.results = fake.paragraph(nb_sentences=3)
                
                db.session.add(lab_test)
                tests_created += 1
    
    db.session.commit()
    print(f"Created {tests_created} lab tests")

def main():
    """Main function to populate all sample data"""
    print("🏥 HealthBridge AI - Sample Data Population")
    print("=" * 50)
    
    # Create Flask app context
    app = create_app()
    with app.app_context():
        try:
            # Create all users
            users = create_sample_users()
            
            # Create doctor schedules
            create_doctor_schedules()
            
            # Create appointments
            appointments = create_appointments()
            
            # Create prescriptions
            create_prescriptions()
            
            # Create telemedicine sessions
            create_telemedicine_sessions()
            
            # Create feedback
            create_feedback()
            
            # Create lab tests
            create_lab_tests()
            
            print("=" * 50)
            print("✅ Sample data creation completed successfully!")
            print("\n📊 Database Summary:")
            print(f"   👥 Users: {User.query.count()}")
            print(f"   📅 Appointments: {Appointment.query.count()}")
            print(f"   💊 Prescriptions: {Prescription.query.count()}")
            print(f"   🧪 Lab Tests: {LabTest.query.count()}")
            print(f"   📹 Video Consultations: {VideoConsultation.query.count()}")
            print(f"   ⭐ Feedback Entries: {AppointmentFeedback.query.count()}")
            print(f"   📋 Doctor Schedules: {DoctorSchedule.query.count()}")
            print("\n🔐 Login Credentials:")
            print("   Admin: admin@healthbridge.com / admin123")
            print("   Doctors: dr.smith@healthbridge.com / doctor123")
            print("   Patients: patient1@example.com / patient123")
            
        except Exception as e:
            print(f"❌ Error creating sample data: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    main()