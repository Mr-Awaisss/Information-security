from flask import Flask, render_template, session
from config import Config
from database.db import init_db
from models.user import User
from routes import register_blueprints
from extensions import csrf, limiter, login_manager

@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader callback function."""
    return User.find_by_id(user_id)

def create_app(config_class=Config):
    """Application factory for configuring and initializing the Flask app instance."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize database connection
    init_db(app)
    
    # Initialize extensions with the app context
    csrf.init_app(app)
    limiter.init_app(app)
    login_manager.init_app(app)
    
    # Register routes / blueprints
    register_blueprints(app)
    
    # Session Management: Make sessions permanent and secure
    @app.before_request
    def make_session_permanent():
        session.permanent = True
        app.permanent_session_lifetime = app.config.get('PERMANENT_SESSION_LIFETIME')

    # Register custom template filters
    from utils.helpers import format_datetime
    @app.template_filter('datetimeformat')
    def datetimeformat_filter(value):
        return format_datetime(value)

    # Register HTTP error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    return app

if __name__ == '__main__':
    app = create_app()
    # Runs locally on port 5000
    app.run(debug=app.config.get('DEBUG', True), host='0.0.0.0', port=5000)
