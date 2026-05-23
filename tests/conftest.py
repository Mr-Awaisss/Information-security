import pytest
from app import create_app
from database.db import get_db, init_db
from models.user import User

from config import Config
from datetime import timedelta

class TestConfig(Config):
    """Testing configuration overriding defaults."""
    SECRET_KEY = 'testing-secret-key-12345'
    TESTING = True
    MONGO_URI = 'mongodb://localhost:27017/secure_auth_test_db'
    WTF_CSRF_ENABLED = False  # Disabled for unit testing form submissions
    DEBUG = False
    
    # Speed up lockout tests by shortening thresholds
    MAX_LOGIN_ATTEMPTS = 5
    SESSION_LIFETIME_MINUTES = 1
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=1)
    LOCKOUT_DURATION_MINUTES = 1
    LOCKOUT_DURATION = timedelta(minutes=1)
    
    # Disable rate limiting during tests
    RATELIMIT_ENABLED = False

@pytest.fixture(scope='session')
def app():
    """Create and configure a Flask application for testing."""
    app = create_app(TestConfig)
    
    # Establish application context temporarily to initialize indexes
    with app.app_context():
        db = get_db()
        if db is not None:
            db.client.drop_database('secure_auth_test_db')
            # Initialize indexes
            from database.db import db_manager
            db_manager.init_indexes()
            
    yield app
    
    # Teardown: Drop test database after tests complete
    with app.app_context():
        db = get_db()
        if db is not None:
            db.client.drop_database('secure_auth_test_db')

@pytest.fixture(scope='function', autouse=True)
def clean_context(app):
    """Ensure a fresh application context and clean Flask globals for every test."""
    with app.app_context():
        yield

@pytest.fixture(scope='function')
def client(app):
    """Retrieve a Flask test client."""
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app):
    """Retrieve a Flask CLI test runner."""
    return app.test_cli_runner()

@pytest.fixture(scope='function')
def init_database(app):
    """Reset database collections prior to running a test case."""
    db = get_db()
    if db is not None:
        db.users.delete_many({})
        db.login_attempts.delete_many({})
        db.security_logs.delete_many({})
    yield db

@pytest.fixture(scope='function')
def sample_user(app, init_database):
    """Generate and return a sample user record in the test database."""
    username = "testuser"
    email = "test@example.com"
    password = "Test@123456_Password"
    
    user = User.create_user(username, email, password)
    return user
