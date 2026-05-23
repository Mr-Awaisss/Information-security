import sys
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure, PyMongoError
from flask import current_app, g

class Database:
    """MongoDB client wrapper class to maintain database connectivity."""
    def __init__(self):
        self.client = None
        self.db = None

    def init_db(self, app):
        """Initialize the MongoDB connection using the flask application configuration."""
        try:
            mongo_uri = app.config.get('MONGO_URI', 'mongodb://localhost:27017/secure_auth_db')
            # Extract database name from URI, default to secure_auth_db if not specified
            db_name = mongo_uri.split('/')[-1]
            if not db_name or '?' in db_name:
                db_name = 'secure_auth_db'
            
            # Configure MongoClient with timeouts to prevent hanging
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            # Verify connectivity
            self.client.admin.command('ping')
            
            self.db = self.client[db_name]
            app.logger.info(f"Successfully connected to MongoDB database: {db_name}")
            
            # Initialize indexes
            self.init_indexes()
        except ConnectionFailure as e:
            app.logger.error(f"Failed to connect to MongoDB server: {e}")
            # Do not crash immediately, but log failure.
        except Exception as e:
            app.logger.error(f"Error during MongoDB initialization: {e}")

    def get_db(self):
        """Retrieve the database instance. Check Flask context or local instance."""
        # If inside a Flask application context, store/retrieve from 'g'
        try:
            if current_app:
                if 'db' not in g:
                    if self.db is None:
                        # Attempt to initialize on-the-fly if client is missing
                        self.init_db(current_app)
                    g.db = self.db
                return g.db
        except RuntimeError:
            # Raised if outside application context (e.g. running tests or scripts)
            pass
        return self.db

    def init_indexes(self):
        """Create indexes in MongoDB collections for query optimization and constraints."""
        if self.db is None:
            return
        
        try:
            # Users Collection Indexes
            # Unique email constraint prevents duplicate registration
            self.db.users.create_index("email", unique=True)
            self.db.users.create_index("username", unique=True)
            
            # Login Attempts Collection Indexes
            # Compound index on user/email and timestamp for lockout verification
            self.db.login_attempts.create_index([("email", ASCENDING), ("timestamp", ASCENDING)])
            self.db.login_attempts.create_index("timestamp")
            
            # Security Logs Collection Indexes
            self.db.security_logs.create_index("timestamp")
            self.db.security_logs.create_index("user_id")
            
            print("Successfully initialized database indexes.")
        except PyMongoError as e:
            print(f"Error initializing indexes: {e}", file=sys.stderr)

# Global database manager instance
db_manager = Database()

def init_db(app):
    db_manager.init_db(app)

def get_db():
    return db_manager.get_db()
