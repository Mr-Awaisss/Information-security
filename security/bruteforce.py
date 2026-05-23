from datetime import datetime, timezone, timedelta
from bson import ObjectId
from database.db import get_db
from flask import current_app
from models.user import User

def record_failed_attempt(email, ip_address, user_agent=""):
    """
    Log a failed login attempt. Increment counter on the user object,
    and trigger account lockout if threshold is exceeded.
    """
    db = get_db()
    if db is None:
        return
        
    cleaned_email = str(email).strip().lower()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    
    # Save the log in login_attempts collection
    attempt_doc = {
        "email": cleaned_email,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "timestamp": now,
        "success": False
    }
    db.login_attempts.insert_one(attempt_doc)
    
    # Check if the user exists
    user = User.find_by_email(cleaned_email)
    if user:
        max_attempts = current_app.config.get('MAX_LOGIN_ATTEMPTS', 5)
        lockout_duration = current_app.config.get('LOCKOUT_DURATION', timedelta(minutes=15))
        
        # Calculate new failed attempt count
        new_attempts = user.failed_attempts + 1
        
        update_data = {
            "failed_attempts": new_attempts,
            "updated_at": now
        }
        
        # If new attempts meets or exceeds the threshold, lockout the user
        if new_attempts >= max_attempts:
            locked_until = now + lockout_duration
            update_data["locked_until"] = locked_until
            
            # Log security event
            from utils.helpers import log_security_event
            log_security_event(
                event_type="ACCOUNT_LOCKED",
                user_id=user.id,
                ip_address=ip_address,
                details=f"Account locked out due to {new_attempts} failed login attempts. Locked until {locked_until} UTC."
            )
            
        db.users.update_one({"_id": ObjectId(user.get_id())}, {"$set": update_data})

def record_successful_login(email, ip_address, user_agent=""):
    """
    Log a successful login. Reset failed attempts and clear lockout state.
    """
    db = get_db()
    if db is None:
        return
        
    cleaned_email = str(email).strip().lower()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    
    # Save log in login_attempts collection
    attempt_doc = {
        "email": cleaned_email,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "timestamp": now,
        "success": True
    }
    db.login_attempts.insert_one(attempt_doc)
    
    # Check if user exists to reset failed attempts
    user = User.find_by_email(cleaned_email)
    if user:
        db.users.update_one(
            {"_id": ObjectId(user.get_id())},
            {"$set": {
                "failed_attempts": 0,
                "locked_until": None,
                "updated_at": now
            }}
        )

def check_lockout(email):
    """
    Determine if user account is locked. Returns a dictionary with lockout state.
    """
    cleaned_email = str(email).strip().lower()
    user = User.find_by_email(cleaned_email)
    
    if not user:
        return {"is_locked": False, "remaining_seconds": 0, "message": ""}
        
    if user.is_locked():
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        locked_until_naive = user.locked_until
        if user.locked_until.tzinfo is not None:
            locked_until_naive = user.locked_until.astimezone(timezone.utc).replace(tzinfo=None)
            
        remaining = int((locked_until_naive - now).total_seconds())
        remaining_minutes = max(1, int(remaining // 60))
        
        return {
            "is_locked": True,
            "remaining_seconds": remaining,
            "message": f"Account is locked due to too many failed attempts. Try again in {remaining_minutes} minutes."
        }
        
    return {"is_locked": False, "remaining_seconds": 0, "message": ""}

def get_login_history(email, limit=20):
    """
    Retrieve login history for a given user email from database.
    """
    db = get_db()
    if db is None:
        return []
        
    cleaned_email = str(email).strip().lower()
    attempts = db.login_attempts.find({"email": cleaned_email}).sort("timestamp", -1).limit(limit)
    return list(attempts)

def get_failed_attempts_count(email):
    """
    Retrieve count of failed attempts for user.
    """
    user = User.find_by_email(email)
    return user.failed_attempts if user else 0
