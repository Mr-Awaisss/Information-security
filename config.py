import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration loading from environment variables."""
    # Flask application settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-secret-key-must-change-in-prod-12345')
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # MongoDB configuration
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/secure_auth_db')
    
    # Session security settings
    SESSION_LIFETIME = int(os.environ.get('SESSION_LIFETIME_MINUTES', 30))
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=SESSION_LIFETIME)
    
    # Session Cookie Security Flags
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Prevents client-side scripts from accessing session cookie
    SESSION_COOKIE_SAMESITE = 'Lax' # Helps mitigate CSRF attacks
    
    # CSRF settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # Token valid for 1 hour
    
    # Security / Lockout settings
    MAX_LOGIN_ATTEMPTS = int(os.environ.get('MAX_LOGIN_ATTEMPTS', 5))
    LOCKOUT_DURATION = timedelta(minutes=int(os.environ.get('LOCKOUT_DURATION_MINUTES', 15)))
