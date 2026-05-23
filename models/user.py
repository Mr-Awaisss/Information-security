from datetime import datetime, timezone
from bson import ObjectId
from flask_login import UserMixin
import bcrypt
from database.db import get_db

class User(UserMixin):
    """User model class implementing Flask-Login's UserMixin for session management."""
    def __init__(self, user_data):
        self.id = str(user_data.get('_id'))
        self.username = user_data.get('username')
        self.email = user_data.get('email')
        self.password_hash = user_data.get('password_hash')
        self.created_at = user_data.get('created_at', datetime.now(timezone.utc))
        self.updated_at = user_data.get('updated_at', datetime.now(timezone.utc))
        self.failed_attempts = user_data.get('failed_attempts', 0)
        self.locked_until = user_data.get('locked_until')
        self.is_active_flag = user_data.get('is_active', True)

    def get_id(self):
        """Retrieve user ID as string for Flask-Login tracking."""
        return self.id

    @property
    def is_active(self):
        """Override Flask-Login user status property."""
        return self.is_active_flag

    def is_locked(self):
        """Check if user account is currently locked out."""
        if not self.locked_until:
            return False
        
        # Ensure we are comparing offset-aware or naive datetimes consistently.
        # Store datetime values as timezone-naive UTC for MongoDB compatibility.
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        locked_until_naive = self.locked_until
        if self.locked_until.tzinfo is not None:
            locked_until_naive = self.locked_until.astimezone(timezone.utc).replace(tzinfo=None)

        if now < locked_until_naive:
            return True
        return False

    def check_password(self, password):
        """Verify the plaintext password against the stored bcrypt hash."""
        if not self.password_hash or not password:
            return False
        try:
            # Handle hash input as string/bytes securely
            hash_bytes = self.password_hash
            if isinstance(hash_bytes, str):
                hash_bytes = hash_bytes.encode('utf-8')
            
            pwd_bytes = password.encode('utf-8')
            return bcrypt.checkpw(pwd_bytes, hash_bytes)
        except Exception:
            return False

    def to_dict(self):
        """Return a dictionary format containing non-sensitive details."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'failed_attempts': self.failed_attempts,
            'locked_until': self.locked_until,
            'is_active': self.is_active_flag
        }

    @staticmethod
    def find_by_email(email):
        """Look up user by email address in MongoDB."""
        db = get_db()
        if db is None:
            return None
        
        # Force case-insensitive lookup and sanitization
        cleaned_email = str(email).strip().lower()
        user_doc = db.users.find_one({"email": cleaned_email})
        if user_doc:
            return User(user_doc)
        return None

    @staticmethod
    def find_by_id(user_id):
        """Look up user by object ID in MongoDB."""
        db = get_db()
        if db is None:
            return None
        
        try:
            user_doc = db.users.find_one({"_id": ObjectId(user_id)})
            if user_doc:
                return User(user_doc)
        except Exception:
            return None
        return None

    @staticmethod
    def create_user(username, email, password):
        """Create a new user document, hash password with bcrypt, and save in MongoDB."""
        db = get_db()
        if db is None:
            raise Exception("Database not connected")

        # Basic validations
        cleaned_username = str(username).strip()
        cleaned_email = str(email).strip().lower()
        
        # Verify user does not already exist
        if User.find_by_email(cleaned_email):
            raise ValueError("A user with this email already exists.")
        
        if db.users.find_one({"username": cleaned_username}):
            raise ValueError("Username is already taken.")

        # Hash password with bcrypt cost factor = 12
        salt = bcrypt.gensalt(rounds=12)
        pwd_bytes = password.encode('utf-8')
        hashed = bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')
        
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        user_doc = {
            "username": cleaned_username,
            "email": cleaned_email,
            "password_hash": hashed,
            "created_at": now,
            "updated_at": now,
            "failed_attempts": 0,
            "locked_until": None,
            "is_active": True
        }
        
        result = db.users.insert_one(user_doc)
        user_doc['_id'] = result.inserted_id
        return User(user_doc)
