import time
from datetime import datetime, timezone, timedelta
from database.db import get_db
from models.user import User
from security.bruteforce import (
    record_failed_attempt, 
    record_successful_login, 
    check_lockout, 
    get_login_history, 
    get_failed_attempts_count
)

def test_initial_no_lockout(app, sample_user):
    """Verify that a newly created user has 0 failed attempts and is not locked out."""
    with app.app_context():
        user = User.find_by_email(sample_user.email)
        assert user.failed_attempts == 0
        assert user.is_locked() is False
        
        lockout = check_lockout(sample_user.email)
        assert lockout["is_locked"] is False

def test_failed_attempts_increment(app, sample_user):
    """Verify that recording failed attempts increments the user's failed attempts counter."""
    with app.app_context():
        ip = "192.168.1.100"
        record_failed_attempt(sample_user.email, ip)
        
        user = User.find_by_email(sample_user.email)
        assert user.failed_attempts == 1
        
        record_failed_attempt(sample_user.email, ip)
        user = User.find_by_email(sample_user.email)
        assert user.failed_attempts == 2

def test_lockout_triggered_at_threshold(app, sample_user):
    """Verify that user is locked out after the maximum allowed failed attempts is reached."""
    with app.app_context():
        ip = "192.168.1.100"
        max_attempts = app.config.get('MAX_LOGIN_ATTEMPTS', 5)
        
        # Simulate failed attempts up to threshold
        for _ in range(max_attempts):
            record_failed_attempt(sample_user.email, ip)
            
        user = User.find_by_email(sample_user.email)
        assert user.failed_attempts == max_attempts
        assert user.is_locked() is True
        
        # Verify check_lockout helper reports lockout
        lockout = check_lockout(sample_user.email)
        assert lockout["is_locked"] is True
        assert "locked" in lockout["message"].lower()

def test_successful_login_resets_counter(app, sample_user):
    """Verify that a successful login resets the failed attempts counter to 0."""
    with app.app_context():
        ip = "192.168.1.100"
        record_failed_attempt(sample_user.email, ip)
        record_failed_attempt(sample_user.email, ip)
        
        user = User.find_by_email(sample_user.email)
        assert user.failed_attempts == 2
        
        # Successful login reset
        record_successful_login(sample_user.email, ip)
        user = User.find_by_email(sample_user.email)
        assert user.failed_attempts == 0
        assert user.locked_until is None

def test_login_attempts_logged(app, sample_user):
    """Verify that all login attempts (success and failure) are recorded in database."""
    with app.app_context():
        ip = "192.168.1.100"
        ua = "TestBrowser/1.0"
        
        record_failed_attempt(sample_user.email, ip, ua)
        record_successful_login(sample_user.email, ip, ua)
        
        history = get_login_history(sample_user.email)
        assert len(history) == 2
        
        # Sorting is newest first
        assert history[0]["success"] is True
        assert history[1]["success"] is False
        assert history[0]["ip_address"] == ip
        assert history[0]["user_agent"] == ua
