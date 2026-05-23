from security.password import validate_password_strength, COMMON_PASSWORDS

def test_weak_password_common():
    """Verify that common passwords in blocklist are rejected immediately."""
    for common in COMMON_PASSWORDS[:5]:
        result = validate_password_strength(common)
        assert result['is_valid'] is False
        assert result['score'] == 0
        assert "common" in result['feedback'][0].lower()

def test_weak_password_short():
    """Verify that passwords under 8 characters are rejected."""
    short_pw = "Ab1!"
    result = validate_password_strength(short_pw)
    assert result['is_valid'] is False
    assert any("at least 8" in msg.lower() for msg in result['feedback'])

def test_missing_uppercase():
    """Verify that passwords missing uppercase characters are rejected."""
    pwd = "mysecurepwd123!"
    result = validate_password_strength(pwd)
    assert result['is_valid'] is False
    assert any("uppercase" in msg.lower() for msg in result['feedback'])

def test_missing_lowercase():
    """Verify that passwords missing lowercase characters are rejected."""
    pwd = "MYSECUREPWD123!"
    result = validate_password_strength(pwd)
    assert result['is_valid'] is False
    assert any("lowercase" in msg.lower() for msg in result['feedback'])

def test_missing_digit():
    """Verify that passwords missing numeric digits are rejected."""
    pwd = "Mysecurepwd!"
    result = validate_password_strength(pwd)
    assert result['is_valid'] is False
    assert any("digit" in msg.lower() for msg in result['feedback'])

def test_missing_special():
    """Verify that passwords missing special character symbols are rejected."""
    pwd = "Mysecurepwd123"
    result = validate_password_strength(pwd)
    assert result['is_valid'] is False
    assert any("special" in msg.lower() for msg in result['feedback'])

def test_strong_password_accepted():
    """Verify that a compliant strong password passes complexity check."""
    pwd = "SecUrity_P@ss_1"
    result = validate_password_strength(pwd)
    assert result['is_valid'] is True
    assert result['score'] >= 4
    assert len(result['feedback']) == 0
    assert result['strength'] in ['Strong', 'Very Strong']

def test_very_strong_password():
    """Verify that a very long compliant password scores 5 (Very Strong)."""
    pwd = "Compl3x_Password_With_Length!"
    result = validate_password_strength(pwd)
    assert result['is_valid'] is True
    assert result['score'] == 5
    assert result['strength'] == 'Very Strong'
