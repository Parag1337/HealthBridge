#!/usr/bin/env python3
"""
Startup script for HealthBridge on Render
This script handles database initialization and starts the Flask app
"""
import os
import sys
from app import create_app, db

def initialize_database():
    """Initialize database if needed"""
    try:
        app = create_app()
        with app.app_context():
            # Test database connection
            db.engine.execute('SELECT 1')
            print("✅ Database connection successful")
            
            # Check if tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if not existing_tables:
                print("🔄 Creating database tables...")
                db.create_all()
                print("✅ Database tables created successfully!")
            else:
                print(f"📋 Database already initialized with {len(existing_tables)} tables")
            
            return True
            
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        print("This is normal if the database doesn't exist yet on Render")
        return False

def start_app():
    """Start the Flask application"""
    try:
        app = create_app()
        
        # Get port from environment (Render sets this automatically)
        port = int(os.environ.get('PORT', 5000))
        
        print(f"🚀 Starting HealthBridge on port {port}")
        
        # Run the app
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False  # Never debug in production
        )
        
    except Exception as e:
        print(f"❌ Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    print("🏥 HealthBridge AI - Starting up...")
    
    # Try to initialize database
    db_initialized = initialize_database()
    
    if not db_initialized:
        print("⚠️  Database not initialized, but continuing with app startup")
    
    # Start the application
    start_app()