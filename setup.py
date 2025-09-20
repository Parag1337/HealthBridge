#!/usr/bin/env python3
"""
HealthBridge AI Setup Script
Automated setup for the Smart Healthcare Application
"""

import os
import sys
import subprocess
import platform

def print_banner():
    """Print the setup banner"""
    print("=" * 60)
    print("🏥 HealthBridge AI - Smart Healthcare Application")
    print("=" * 60)
    print("🚀 Starting automated setup process...")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("📋 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Incompatible")
        print("   Please install Python 3.8 or higher")
        return False

def check_pip():
    """Check if pip is available"""
    print("📋 Checking pip installation...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print("✅ pip is installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip is not installed")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    print("⚙️  Setting up environment configuration...")
    
    if os.path.exists('.env'):
        print("ℹ️  .env file already exists - skipping creation")
        return True
    
    env_content = """# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USERNAME=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=healthbridge_db

# Flask Configuration
SECRET_KEY=your-secret-key-change-this-in-production
FLASK_ENV=development
FLASK_APP=run.py
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file created")
        print("⚠️  Please update .env file with your MySQL credentials")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def check_mysql():
    """Check if MySQL is available"""
    print("🗄️  Checking MySQL availability...")
    
    # Try to import MySQLdb to check if MySQL client is available
    try:
        import MySQLdb
        print("✅ MySQL client libraries are available")
        return True
    except ImportError:
        print("⚠️  MySQL client libraries not found")
        print("   Please install MySQL client:")
        
        system = platform.system().lower()
        if system == "windows":
            print("   - Download and install MySQL from https://dev.mysql.com/downloads/mysql/")
        elif system == "darwin":  # macOS
            print("   - brew install mysql")
        else:  # Linux
            print("   - sudo apt-get install mysql-server mysql-client (Ubuntu/Debian)")
            print("   - sudo yum install mysql-server mysql-client (CentOS/RHEL)")
        
        return False

def setup_database():
    """Setup database"""
    print("🗄️  Database setup...")
    print("ℹ️  Please ensure:")
    print("   1. MySQL server is running")
    print("   2. Database 'healthbridge_db' exists")
    print("   3. .env file has correct database credentials")
    print()
    
    response = input("Would you like to reset the database schema? (y/N): ").lower().strip()
    if response == 'y':
        try:
            subprocess.run([sys.executable, "reset_db.py"], check=True)
            print("✅ Database schema reset successfully")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Database reset failed: {e}")
            print("   You may need to setup the database manually")
    else:
        print("⏭️  Skipping database reset")

def create_test_accounts():
    """Create test accounts"""
    print("👥 Creating test accounts...")
    
    response = input("Would you like to create test accounts? (Y/n): ").lower().strip()
    if response != 'n':
        try:
            subprocess.run([sys.executable, "create_test_accounts.py"], check=True)
            print("✅ Test accounts created successfully")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Failed to create test accounts: {e}")
    else:
        print("⏭️  Skipping test account creation")

def print_completion_message():
    """Print setup completion message"""
    print()
    print("=" * 60)
    print("🎉 Setup completed!")
    print("=" * 60)
    print("📋 Next steps:")
    print("1. Update .env file with your MySQL credentials")
    print("2. Ensure MySQL server is running")
    print("3. Create database 'healthbridge_db' in MySQL")
    print("4. Run: python run.py")
    print("5. Open: http://127.0.0.1:5000")
    print()
    print("📚 Test Accounts (if created):")
    print("   Patient: testpatient@demo.com / demo123")
    print("   Doctor: testdoctor@demo.com / demo123")
    print()
    print("🆘 Need help? Check README.md or GitHub issues")
    print("=" * 60)

def main():
    """Main setup function"""
    print_banner()
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    if not check_pip():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Setup configuration
    create_env_file()
    
    # Check MySQL
    check_mysql()
    
    # Setup database
    setup_database()
    
    # Create test accounts
    create_test_accounts()
    
    # Print completion message
    print_completion_message()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed with error: {e}")
        sys.exit(1)