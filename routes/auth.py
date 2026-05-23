from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from security.password import validate_password_strength
from security.bruteforce import check_lockout, record_failed_attempt, record_successful_login
from security.validators import sanitize_input, validate_email, validate_username
from utils.helpers import get_client_ip, log_security_event

auth_bp = Blueprint('auth', __name__)

# Note: Limiter will be imported here inside the decorators/functions, or imported from extensions
# To prevent circular import, we can access limiter from current_app or import it inside the module
from extensions import limiter

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    """Handle user login authentication, credentials checking, lockout enforcement."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
        
    if request.method == 'POST':
        # Retrieve and sanitize inputs
        email = sanitize_input(request.form.get('email', ''))
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))
        
        ip_address = get_client_ip(request)
        user_agent = request.headers.get('User-Agent', '')
        
        # Validation checks
        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template('login.html')
            
        if not validate_email(email):
            flash("Invalid email format.", "danger")
            return render_template('login.html')
            
        # Check if the account is currently locked out
        lockout_status = check_lockout(email)
        if lockout_status["is_locked"]:
            flash(lockout_status["message"], "danger")
            return render_template('login.html')
            
        # Authenticate user
        user = User.find_by_email(email)
        
        if user and user.check_password(password):
            # Login successful
            login_user(user, remember=remember)
            record_successful_login(email, ip_address, user_agent)
            
            # Log security event
            log_security_event(
                event_type="LOGIN_SUCCESS",
                user_id=user.id,
                ip_address=ip_address,
                details=f"User {user.username} logged in successfully."
            )
            
            flash("Welcome back! You have logged in successfully.", "success")
            
            # Flask-Login handles redirecting back to the original page requested
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('dashboard.dashboard')
            return redirect(next_page)
        else:
            # Login failed
            record_failed_attempt(email, ip_address, user_agent)
            
            # Log security event
            user_id = user.id if user else "UNKNOWN"
            log_security_event(
                event_type="LOGIN_FAILED",
                user_id=user_id,
                ip_address=ip_address,
                details=f"Failed login attempt for email: {email}"
            )
            
            # Check if account locked after this failure
            lockout_status = check_lockout(email)
            if lockout_status["is_locked"]:
                flash(lockout_status["message"], "danger")
            else:
                flash("Invalid email or password.", "danger")
                
    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def signup():
    """Handle user account registration with input validation & password strength evaluation."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
        
    if request.method == 'POST':
        # Retrieve and sanitize inputs
        username = sanitize_input(request.form.get('username', ''))
        email = sanitize_input(request.form.get('email', ''))
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        ip_address = get_client_ip(request)
        
        # Validation checks
        if not username or not email or not password or not confirm_password:
            flash("All fields are required.", "danger")
            return render_template('signup.html')
            
        if not validate_username(username):
            flash("Username must be between 3 and 30 characters and contain only letters, numbers, or underscores.", "danger")
            return render_template('signup.html')
            
        if not validate_email(email):
            flash("Invalid email format.", "danger")
            return render_template('signup.html')
            
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('signup.html')
            
        # Validate password strength
        strength_results = validate_password_strength(password)
        if not strength_results['is_valid']:
            flash("Password does not meet the security requirements.", "danger")
            for feedback_msg in strength_results['feedback']:
                flash(feedback_msg, "warning")
            return render_template('signup.html')
            
        # Attempt user creation
        try:
            new_user = User.create_user(username, email, password)
            
            # Log security event
            log_security_event(
                event_type="ACCOUNT_CREATED",
                user_id=new_user.id,
                ip_address=ip_address,
                details=f"User account created for {username} ({email})."
            )
            
            flash("Your account has been created successfully! You can now log in.", "success")
            return redirect(url_for('auth.login'))
        except ValueError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash("An unexpected error occurred. Please try again.", "danger")
            current_app.logger.error(f"Signup error: {e}")
            
    return render_template('signup.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout process, session destruction, and logging."""
    ip_address = get_client_ip(request)
    username = current_user.username
    user_id = current_user.id
    
    logout_user()
    
    # Log security event
    log_security_event(
        event_type="LOGOUT",
        user_id=user_id,
        ip_address=ip_address,
        details=f"User {username} logged out."
    )
    
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
@limiter.limit("3 per minute")
def change_password():
    """Handle secure password modification for authenticated users."""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        ip_address = get_client_ip(request)
        
        if not current_password or not new_password or not confirm_password:
            flash("All fields are required.", "danger")
            return redirect(url_for('dashboard.profile'))
            
        # Verify current password
        if not current_user.check_password(current_password):
            flash("Incorrect current password.", "danger")
            
            # Log failed password change attempt
            log_security_event(
                event_type="PASSWORD_CHANGE_FAILED",
                user_id=current_user.id,
                ip_address=ip_address,
                details="Failed password change: Incorrect current password."
            )
            return redirect(url_for('dashboard.profile'))
            
        # Match confirmation
        if new_password != confirm_password:
            flash("New passwords do not match.", "danger")
            return redirect(url_for('dashboard.profile'))
            
        # Validate strength
        strength_results = validate_password_strength(new_password)
        if not strength_results['is_valid']:
            flash("New password does not meet security requirements.", "danger")
            for feedback in strength_results['feedback']:
                flash(feedback, "warning")
            return redirect(url_for('dashboard.profile'))
            
        # Hash and update in DB
        try:
            import bcrypt
            db = get_db()
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
            
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            
            db.users.update_one(
                {"_id": ObjectId(current_user.id)},
                {"$set": {"password_hash": hashed, "updated_at": now}}
            )
            
            # Log security event
            log_security_event(
                event_type="PASSWORD_CHANGED",
                user_id=current_user.id,
                ip_address=ip_address,
                details="Password changed successfully."
            )
            
            flash("Your password has been updated successfully.", "success")
            return redirect(url_for('dashboard.profile'))
        except Exception as e:
            flash("Failed to update password. Please try again.", "danger")
            current_app.logger.error(f"Password update error: {e}")
            
    return redirect(url_for('dashboard.profile'))
