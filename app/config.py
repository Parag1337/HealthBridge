import os

class Config:
    SECRET_KEY = os.environ.get('mysql://root:password@localhost:3306/smart_healthcare_db') or 'dev-secret-key-change-in-production'
    
    # Database Configuration
    # Will use SQLite for development if no DATABASE_URL is set
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///healthcare.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email Configuration - Gmail SMTP
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('EMAIL_USER') or 'healthbridgeassistant@gmail.com'
    MAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD') or 'xbcj xnem snnm yish'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'healthbridgeassistant@gmail.com'
    
    # Admin Configuration
    ADMINS = ['admin@healthbridgeai.com']
    
    # Notification API Key
    NOTIFICATION_API_KEY = os.environ.get('NOTIFICATION_API_KEY')