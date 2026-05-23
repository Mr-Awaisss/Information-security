import re
import bcrypt

# List of top 20 extremely common/weak passwords to block during registration
COMMON_PASSWORDS = [
    "123456", "password", "123456789", "12345678", "12345", 
    "qwerty", "1234567", "password123", "default", "admin",
    "password123!", "welcome", "letmein1", "admin123", "password!",
    "security", "p@ssword", "p@ssw0rd", "123456abc", "computer"
]

def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt with standard cost factor (12)."""
    if not password:
        raise ValueError("Password cannot be empty.")
    salt = bcrypt.gensalt(rounds=12)
    pwd_bytes = password.encode('utf-8')
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    if not password or not hashed:
        return False
    try:
        pwd_bytes = password.encode('utf-8')
        hash_bytes = hashed.encode('utf-8') if isinstance(hashed, str) else hashed
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False

def validate_password_strength(password: str) -> dict:
    """
    Check password complexity and return strength rating and validation feedback.
    
    Criteria:
      - Length >= 8 characters (essential)
      - At least one uppercase letter (essential)
      - At least one lowercase letter (essential)
      - At least one digit (essential)
      - At least one special character (essential)
      - Not in the blocklist of common passwords (essential)
    """
    feedback = []
    score = 0
    
    if not password:
        return {
            'is_valid': False,
            'score': 0,
            'strength': 'Weak',
            'feedback': ["Password cannot be empty."]
        }
        
    # Check common password list
    if password.lower() in COMMON_PASSWORDS:
        return {
            'is_valid': False,
            'score': 0,
            'strength': 'Weak',
            'feedback': ["This password is too common. Please choose a more unique password."]
        }
        
    # Check length
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Must be at least 8 characters long.")

    # Check uppercase
    if re.search(r"[A-Z]", password):
        score += 1
    else:
        feedback.append("Must contain at least one uppercase letter (A-Z).")

    # Check lowercase
    if re.search(r"[a-z]", password):
        score += 1
    else:
        feedback.append("Must contain at least one lowercase letter (a-z).")

    # Check digits
    if re.search(r"\d", password):
        score += 1
    else:
        feedback.append("Must contain at least one numerical digit (0-9).")

    # Check special character
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 1
    else:
        feedback.append("Must contain at least one special character (e.g., !, @, #, $, %, etc.).")

    # Determine validity and adjust score/strength
    is_valid = (len(feedback) == 0)
    
    if is_valid:
        if len(password) >= 12:
            score = 5
        else:
            score = 4
    else:
        # If not valid, cap the score at 3 so it's not marked as Strong or Very Strong
        score = min(3, score)

    # Determine qualitative strength string based on score
    strength_map = {
        0: 'Weak',
        1: 'Weak',
        2: 'Fair',
        3: 'Good',
        4: 'Strong',
        5: 'Very Strong'
    }
    
    strength = strength_map.get(score, 'Weak')
    
    return {
        'is_valid': is_valid,
        'score': score,
        'strength': strength,
        'feedback': feedback
    }
