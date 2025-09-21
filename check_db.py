import sqlite3
import os

def check_database_schema():
    """Check what tables exist in the database"""
    db_path = os.path.join(os.path.dirname(__file__), 'healthbridge.db')
    print(f"Checking database at: {db_path}")
    print(f"Database exists: {os.path.exists(db_path)}")
    
    if os.path.exists(db_path):
        print(f"Database size: {os.path.getsize(db_path)} bytes")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables in database:")
        for table in tables:
            print(f"  - {table[0]}")
            
        # Check users table specifically
        if any('user' in table[0].lower() for table in tables):
            # Get column info for users table
            for table in tables:
                if 'user' in table[0].lower():
                    table_name = table[0]
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    columns = cursor.fetchall()
                    print(f"\nColumns in {table_name}:")
                    for col in columns:
                        print(f"  - {col[1]} ({col[2]})")
        
    except Exception as e:
        print(f"Error checking database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_database_schema()