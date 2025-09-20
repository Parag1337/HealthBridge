import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database Configuration
    # Will use SQLite for development if no DATABASE_URL is set
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///healthcare.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    
    # Admin Configuration
    ADMINS = ['admin@healthbridgeai.com']
    
    # Notification API Key
    NOTIFICATION_API_KEY = os.environ.get('NOTIFICATION_API_KEY')