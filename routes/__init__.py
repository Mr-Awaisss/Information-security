from .auth import auth_bp
from .dashboard import dashboard_bp

def register_blueprints(app):
    """Register application blueprints on the Flask app instance."""
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
