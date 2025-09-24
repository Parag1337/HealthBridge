import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database Configuration
    # Will use SQLite for development if no DATABASE_URL is set
    database_url = os.environ.get('DATABASE_URL') or 'sqlite:///healthcare.db'
    
    # Fix SSL parameter format for MySQL connections (Render compatibility)
    if database_url.startswith('mysql://'):
        # Parse the URL
        parsed = urlparse(database_url)
        
        # Handle query parameters
        if parsed.query:
            query_params = parse_qs(parsed.query)
            
            # Fix ssl-mode to ssl_mode if present
            if 'ssl-mode' in query_params:
                query_params['ssl_mode'] = query_params.pop('ssl-mode')
            
            # Rebuild the query string
            new_query = urlencode(query_params, doseq=True)
            
            # Rebuild the URL
            database_url = urlunparse((
                parsed.scheme, parsed.netloc, parsed.path,
                parsed.params, new_query, parsed.fragment
            ))
        
        # Add SSL configuration if not present
        if '?' not in database_url:
            database_url += '?ssl_mode=REQUIRED&ssl_disabled=False'
        elif 'ssl' not in database_url.lower():
            database_url += '&ssl_mode=REQUIRED&ssl_disabled=False'
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Additional MySQL engine options for better compatibility
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_timeout': 20,
        'pool_recycle': -1,
        'pool_pre_ping': True
    }
    
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
    
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or 'AIzaSyD8ZSKBHR39oWPuqknZtbvP3zxYpORoyjg'
