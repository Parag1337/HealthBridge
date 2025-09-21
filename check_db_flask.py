from app import create_app, db
from sqlalchemy import text

def check_database_properly():
    """Check database through Flask app context"""
    app = create_app()
    
    with app.app_context():
        try:
            # Try to query the database
            with db.engine.connect() as conn:
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
                tables = result.fetchall()
                print("Tables found:")
                for table in tables:
                    print(f"  - {table[0]}")
                    
                # Check if users table exists and has data
                if any('users' in str(table) for table in tables):
                    result = conn.execute(text("PRAGMA table_info(users);"))
                    columns = result.fetchall()
                    print("\nUsers table columns:")
                    for col in columns:
                        print(f"  - {col[1]} ({col[2]})")
                        
                    # Check if there's any data
                    result = conn.execute(text("SELECT COUNT(*) FROM users;"))
                    count = result.fetchone()[0]
                    print(f"\nUsers count: {count}")
                else:
                    print("No users table found. Creating database...")
                    db.create_all()
                    print("Database tables created!")
                    
        except Exception as e:
            print(f"Error: {e}")
            print("Trying to create database...")
            try:
                db.create_all()
                print("Database created successfully!")
            except Exception as create_error:
                print(f"Error creating database: {create_error}")

if __name__ == "__main__":
    check_database_properly()