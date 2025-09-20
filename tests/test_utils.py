import unittest
from app.utils.database import get_db_connection
from app.utils.auth import generate_password_hash, verify_password

class TestUtils(unittest.TestCase):

    def test_generate_password_hash(self):
        password = "test_password"
        hashed_password = generate_password_hash(password)
        self.assertNotEqual(password, hashed_password)
        self.assertTrue(verify_password(password, hashed_password))

    def test_db_connection(self):
        conn = get_db_connection()
        self.assertIsNotNone(conn)
        conn.close()

if __name__ == '__main__':
    unittest.main()