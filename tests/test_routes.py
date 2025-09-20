from app import app
import unittest

class TestRoutes(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)

    def test_register_page(self):
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)

    def test_patient_dashboard(self):
        response = self.app.get('/patient/dashboard')
        self.assertEqual(response.status_code, 200)

    def test_doctor_dashboard(self):
        response = self.app.get('/doctor/dashboard')
        self.assertEqual(response.status_code, 200)

    def test_admin_dashboard(self):
        response = self.app.get('/admin/dashboard')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()