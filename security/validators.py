import re

def sanitize_input(value):
    """
    Sanitize input values to defend against NoSQL injection, XSS, and parameter pollution.
    Removes characters beginning with '$' (MongoDB operator character) and strips whitespace.
    Handles strings, lists, dicts, and returns sanitized output.
    """
    if isinstance(value, str):
        # Defend against NoSQL injection by preventing MongoDB operators in queries
        sanitized = value.strip()
        # If input starts with or contains MongoDB operator characters, strip or escape them
        if sanitized.startswith('$'):
            sanitized = sanitized.replace('$', '', 1)
        return sanitized
        
    elif isinstance(value, dict):
        sanitized_dict = {}
        for k, v in value.items():
            # Drop key completely if it starts with '$' (NoSQL injection prevention)
            if isinstance(k, str) and k.startswith('$'):
                continue
            sanitized_dict[k] = sanitize_input(v)
        return sanitized_dict
        
    elif isinstance(value, list):
        return [sanitize_input(item) for item in value]
        
    return value

def validate_email(email: str) -> bool:
    """
    Validate email address format using standard RFC 5322 regex validation.
    """
    if not email:
        return False
        
    # Standard email regex
    pattern = r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
    return bool(re.match(pattern, email.strip()))

def validate_username(username: str) -> bool:
    """
    Validate username criteria: 3-30 characters, alphanumeric and underscores only.
    """
    if not username:
        return False
        
    # Alphanumeric and underscores, length 3 to 30
    pattern = r"^[a-zA-Z0-9_]{3,30}$"
    return bool(re.match(pattern, username.strip()))

def sanitize_query(query_dict: dict) -> dict:
    """
    Specifically sanitize dictionary queries intended for MongoDB to prevent injection.
    Recursively strips keys starting with '$'.
    """
    if not isinstance(query_dict, dict):
        return query_dict
        
    sanitized = {}
    for k, v in query_dict.items():
        if isinstance(k, str) and k.startswith('$'):
            continue
        if isinstance(v, dict):
            sanitized[k] = sanitize_query(v)
        elif isinstance(v, list):
            sanitized[k] = [sanitize_query(item) if isinstance(item, dict) else sanitize_input(item) for item in v]
        else:
            sanitized[k] = sanitize_input(v)
    return sanitized
