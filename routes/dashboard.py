from flask import Blueprint, render_template
from flask_login import login_required, current_user
from security.bruteforce import get_login_history, get_failed_attempts_count
from utils.helpers import get_security_stats

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """Render the protected user dashboard showcasing security metrics, history, and actions."""
    # Retrieve security statistics
    stats = get_security_stats(current_user.email)
    
    # Retrieve recent login attempts
    history = get_login_history(current_user.email, limit=10)
    
    return render_template(
        'dashboard.html',
        stats=stats,
        login_history=history
    )

@dashboard_bp.route('/profile')
@login_required
def profile():
    """Render the user profile details page including full history logs and password alteration option."""
    # Retrieve login history
    history = get_login_history(current_user.email, limit=50)
    
    # Retrieve total failed attempts count
    failed_count = get_failed_attempts_count(current_user.email)
    
    return render_template(
        'profile.html',
        login_history=history,
        failed_count=failed_count
    )
