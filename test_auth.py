"""
Test script to verify authentication functionality
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_patient_registration():
    """Test patient registration"""
    data = {
        'user_type': 'patient',
        'first_name': 'Test',
        'last_name': 'Patient',
        'email': 'testpatient@test.com',
        'password': 'testpass123',
        'confirm_password': 'testpass123',
        'phone': '1234567890',
        'date_of_birth': '1990-01-01',
        'gender': 'male',
        'address': '123 Test Street',
        'terms_accepted': 'on'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", data=data, allow_redirects=False)
        print(f"Patient Registration Status: {response.status_code}")
        if response.status_code == 302:
            print("✅ Patient registration successful - redirected to login")
        else:
            print(f"❌ Patient registration failed: {response.text}")
    except Exception as e:
        print(f"❌ Error testing patient registration: {e}")

def test_doctor_registration():
    """Test doctor registration"""
    data = {
        'user_type': 'doctor',
        'first_name': 'Test',
        'last_name': 'Doctor',
        'email': 'testdoctor@test.com',
        'password': 'testpass123',
        'confirm_password': 'testpass123',
        'phone': '1234567890',
        'specialization': 'general',
        'experience': '5',
        'license_number': 'TEST123',
        'qualification': 'MBBS',
        'terms_accepted': 'on'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", data=data, allow_redirects=False)
        print(f"Doctor Registration Status: {response.status_code}")
        if response.status_code == 302:
            print("✅ Doctor registration successful - redirected to login")
        else:
            print(f"❌ Doctor registration failed: {response.text}")
    except Exception as e:
        print(f"❌ Error testing doctor registration: {e}")

def test_patient_login():
    """Test patient login"""
    data = {
        'user_type': 'patient',
        'email': 'testpatient@test.com',
        'password': 'testpass123'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=data, allow_redirects=False)
        print(f"Patient Login Status: {response.status_code}")
        if response.status_code == 302:
            print("✅ Patient login successful - redirected to dashboard")
        else:
            print(f"❌ Patient login failed: {response.text}")
    except Exception as e:
        print(f"❌ Error testing patient login: {e}")

def test_doctor_login():
    """Test doctor login with sample doctor"""
    data = {
        'user_type': 'doctor',
        'email': 'doctor@healthbridge.com',
        'password': 'doctor123'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=data, allow_redirects=False)
        print(f"Doctor Login Status: {response.status_code}")
        if response.status_code == 302:
            print("✅ Doctor login successful - redirected to dashboard")
        else:
            print(f"❌ Doctor login failed: {response.text}")
    except Exception as e:
        print(f"❌ Error testing doctor login: {e}")

if __name__ == "__main__":
    print("🔬 Testing Smart Healthcare App Authentication")
    print("=" * 50)
    
    # Test registrations first
    print("\n📝 Testing Registration...")
    test_patient_registration()
    test_doctor_registration()
    
    # Test logins
    print("\n🔐 Testing Login...")
    test_patient_login()
    test_doctor_login()
    
    print("\n" + "=" * 50)
    print("✅ Testing completed!")