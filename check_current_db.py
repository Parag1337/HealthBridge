from app import create_app, db
from sqlalchemy import text

def check_current_database():
    """Check what database we're actually connected to"""
    app = create_app()
    
    with app.app_context():
        print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        try:
            with db.engine.connect() as conn:
                # Check if this is MySQL or SQLite
                try:
                    result = conn.execute(text("SELECT VERSION();"))  # MySQL command
                    version = result.fetchone()[0]
                    print(f"Connected to MySQL version: {version}")
                    
                    # Show tables in MySQL
                    result = conn.execute(text("SHOW TABLES;"))
                    tables = result.fetchall()
                    print("MySQL Tables:")
                    for table in tables:
                        print(f"  - {table[0]}")
                        
                    # Check users table structure
                    if any('users' in str(table) for table in tables):
                        result = conn.execute(text("DESCRIBE users;"))
                        columns = result.fetchall()
                        print("\nUsers table structure:")
                        for col in columns:
                            print(f"  - {col[0]} ({col[1]})")
                            
                except Exception:
                    # Must be SQLite
                    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
                    tables = result.fetchall()
                    print("SQLite Tables:")
                    for table in tables:
                        print(f"  - {table[0]}")
                        
        except Exception as e:
            print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_current_database()