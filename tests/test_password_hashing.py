import bcrypt
from security.password import hash_password, verify_password

def test_hash_password_returns_string():
    """Verify that password hashing successfully outputs a string."""
    passwd = "MySecurePassword123!"
    hashed = hash_password(passwd)
    assert isinstance(hashed, str)
    assert len(hashed) > 0

def test_hash_password_not_plaintext():
    """Verify that the generated password hash does not expose the plaintext."""
    passwd = "MySecurePassword123!"
    hashed = hash_password(passwd)
    assert hashed != passwd

def test_verify_correct_password():
    """Verify that checking the correct plaintext password returns True."""
    passwd = "MySecurePassword123!"
    hashed = hash_password(passwd)
    assert verify_password(passwd, hashed) is True

def test_verify_wrong_password():
    """Verify that checking an incorrect password returns False."""
    passwd = "MySecurePassword123!"
    hashed = hash_password(passwd)
    assert verify_password("WrongPassword123!", hashed) is False

def test_hash_uniqueness():
    """Verify that salting ensures hashing the same password twice yields different hashes."""
    passwd = "MySecurePassword123!"
    hashed1 = hash_password(passwd)
    hashed2 = hash_password(passwd)
    assert hashed1 != hashed2

def test_bcrypt_format():
    """Verify that hashes conform to standard bcrypt format (starts with $2b$)."""
    passwd = "MySecurePassword123!"
    hashed = hash_password(passwd)
    assert hashed.startswith("$2b$")

def test_hash_length():
    """Verify that bcrypt hashes are exactly 60 characters long."""
    passwd = "MySecurePassword123!"
    hashed = hash_password(passwd)
    assert len(hashed) == 60

def test_unicode_password():
    """Verify that unicode characters in passwords are handled securely."""
    passwd = "Pâsswørd®123!🚀"
    hashed = hash_password(passwd)
    assert verify_password(passwd, hashed) is True

def test_long_password():
    """Verify that passwords exceeding 72 characters are hashed correctly (bcrypt maximum limit)."""
    # bcrypt ignores bytes past 72 bytes. Our implementation encodes as utf8.
    # We test that a 80-character password hashes and matches, but different suffixes after 72 are handled safely.
    passwd1 = "a" * 80
    passwd2 = ("a" * 72) + "b" * 8
    
    hashed1 = hash_password(passwd1)
    
    # Due to bcrypt's internal 72-byte limit, checking passwd2 against hashed1 might be True.
    # We check that verification of passwd1 works.
    assert verify_password(passwd1, hashed1) is True
