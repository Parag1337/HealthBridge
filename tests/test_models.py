from app import create_app, db
from app.models.user import User
from app.models.appointment import Appointment
from app.models.prescription import Prescription
import unittest

class ModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create sample data using unified User model
        self.patient_user = User(
            email='patient@test.com',
            first_name='John',
            last_name='Doe',
            role='patient'
        )
        self.patient_user.set_password('password')
        
        self.doctor_user = User(
            email='doctor@test.com',
            first_name='Dr. Jane',
            last_name='Smith',
            role='doctor',
            specialization='Cardiology'
        )
        self.doctor_user.set_password('password')

        db.session.add(self.patient_user)
        db.session.add(self.doctor_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_patient_user_creation(self):
        user = User.query.filter_by(email='patient@test.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.role, 'patient')
        self.assertEqual(user.first_name, 'John')

    def test_doctor_user_creation(self):
        doctor = User.query.filter_by(email='doctor@test.com').first()
        self.assertIsNotNone(doctor)
        self.assertEqual(doctor.role, 'doctor')
        self.assertEqual(doctor.specialization, 'Cardiology')

    def test_password_hashing(self):
        user = User.query.filter_by(email='patient@test.com').first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password('password'))
        self.assertFalse(user.check_password('wrongpassword'))

    def test_prescription_creation(self):
        prescription = Prescription.query.first()
        self.assertIsNotNone(prescription)
        self.assertEqual(prescription.medication, 'Aspirin')
        self.assertEqual(prescription.dosage, '100mg')

if __name__ == '__main__':
    unittest.main()