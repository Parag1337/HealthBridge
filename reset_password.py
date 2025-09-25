#!/usr/bin/env python3
"""
Reset password for panzadeparag1337@gmail.com
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

try:
    from app import create_app, db
    from app.models.user import User
    
    app = create_app()
    
    with app.app_context():
        print("Password Reset for panzadeparag1337@gmail.com")
        print("=" * 50)
        
        # Find your user
        email = 'panzadeparag1337@gmail.com'
        user = User.query.filter_by(email=email).first()
        
        if user:
            print(f"User found: {user.email}")
            print(f"Role: {user.role}")
            print(f"Name: {user.first_name} {user.last_name}")
            
            # Set new password
            new_password = 'password123'
            user.set_password(new_password)
            db.session.commit()
            
            # Verify the new password works
            if user.check_password(new_password):
                print(f"\nPASSWORD RESET SUCCESSFUL!")
                print(f"=" * 50)
                print(f"NEW LOGIN CREDENTIALS:")
                print(f"   Email: {email}")
                print(f"   Password: {new_password}")
                print(f"   User Type: {user.role}")
                print(f"=" * 50)
                print(f"You can now login at: http://127.0.0.1:5000/auth/login")
            else:
                print(f"ERROR: Password verification failed!")
                
        else:
            print(f"ERROR: User {email} not found!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()