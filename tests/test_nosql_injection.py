from security.validators import sanitize_input, sanitize_query

def test_sanitize_dollar_operator():
    """Verify that sanitize_input removes leading dollar signs to prevent NoSQL operator injection."""
    injection = "$gt"
    sanitized = sanitize_input(injection)
    assert sanitized == "gt"

def test_sanitize_nested_injection():
    """Verify that recursive sanitize_input drops keys starting with $ in dictionaries."""
    payload = {
        "username": "admin",
        "password": {
            "$ne": "null"
        }
    }
    sanitized = sanitize_input(payload)
    # The key $ne should be excluded
    assert "password" in sanitized
    assert sanitized["password"] == {}

def test_sanitize_normal_input():
    """Verify that safe inputs are not altered during sanitization."""
    safe_str = "user_name_123"
    assert sanitize_input(safe_str) == safe_str
    
    email = "test@example.com"
    assert sanitize_input(email) == email

def test_query_sanitization():
    """Verify that sanitize_query filters out NoSQL commands in nested structures."""
    malicious_query = {
        "email": {"$regex": ".*"},
        "active": True
    }
    sanitized = sanitize_query(malicious_query)
    # The key $regex is stripped
    assert "email" in sanitized
    assert sanitized["email"] == {}
    assert sanitized["active"] is True
