from datetime import datetime, timezone
from database.db import get_db

def get_client_ip(request):
    """
    Extract client IP address from HTTP request.
    Handles proxy headers (X-Forwarded-For) if the app is behind a reverse proxy.
    """
    if request.headers.getlist("X-Forwarded-For"):
        # The list may contain multiple IPs (client, proxy1, proxy2). The client is the first one.
        ip = request.headers.getlist("X-Forwarded-For")[0].split(',')[0].strip()
    else:
        ip = request.remote_addr
    return ip

def log_security_event(event_type, user_id, ip_address, details):
    """
    Log a security event in the database for auditing and monitoring.
    """
    db = get_db()
    if db is None:
        return
        
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    log_doc = {
        "event_type": event_type,
        "user_id": user_id,
        "ip_address": ip_address,
        "timestamp": now,
        "details": details
    }
    try:
        db.security_logs.insert_one(log_doc)
    except Exception as e:
        print(f"Failed to log security event: {e}")

def format_datetime(dt):
    """
    Format a datetime object for user-friendly display in templates.
    """
    if not dt:
        return "N/A"
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def get_security_stats(user_email):
    """
    Calculate and return security statistics for a user.
    """
    db = get_db()
    if db is None:
        return {
            "total_logins": 0,
            "failed_logins": 0,
            "last_login": "N/A",
            "account_age": "N/A"
        }
        
    cleaned_email = str(user_email).strip().lower()
    
    # Get total successful login attempts
    total_logins = db.login_attempts.count_documents({"email": cleaned_email, "success": True})
    
    # Get total failed login attempts
    failed_logins = db.login_attempts.count_documents({"email": cleaned_email, "success": False})
    
    # Find last successful login
    last_login_doc = db.login_attempts.find_one(
        {"email": cleaned_email, "success": True},
        sort=[("timestamp", -1)]
    )
    
    # Find the user record for created_at
    user_doc = db.users.find_one({"email": cleaned_email})
    
    last_login = "N/A"
    if last_login_doc:
        last_login = format_datetime(last_login_doc["timestamp"])
        
    account_age = "N/A"
    if user_doc and "created_at" in user_doc:
        created_at = user_doc["created_at"]
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        delta = now - created_at
        if delta.days == 0:
            account_age = "Created Today"
        else:
            account_age = f"{delta.days} Days"
            
    return {
        "total_logins": total_logins,
        "failed_logins": failed_logins,
        "last_login": last_login,
        "account_age": account_age
    }
