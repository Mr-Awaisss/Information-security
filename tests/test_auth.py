from models.user import User

def test_login_page_loads(client):
    """Verify that the login page loads with HTTP 200."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Sign in" in response.data

def test_signup_page_loads(client):
    """Verify that the signup page loads with HTTP 200."""
    response = client.get('/signup')
    assert response.status_code == 200
    assert b"Create Account" in response.data

def test_successful_signup(app, client, init_database):
    """Verify that submitting valid registration data creates a user and redirects."""
    with app.app_context():
        response = client.post('/signup', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'Password@12345',
            'confirm_password': 'Password@12345'
        })
        # Check redirection to login
        assert response.status_code == 302
        assert '/login' in response.headers['Location']
        
        # Verify user exists in database
        user = User.find_by_email('new@example.com')
        assert user is not None
        assert user.username == 'newuser'

def test_signup_duplicate_email(app, client, sample_user):
    """Verify that attempting to register with an existing email displays an error."""
    with app.app_context():
        response = client.post('/signup', data={
            'username': 'differentname',
            'email': sample_user.email,  # Existing email
            'password': 'Password@12345',
            'confirm_password': 'Password@12345'
        })
        assert response.status_code == 200
        # Flash message indicating user exists should be rendered
        assert b"already exists" in response.data

def test_signup_weak_password(app, client, init_database):
    """Verify that registering with a weak password fails and presents criteria warnings."""
    with app.app_context():
        response = client.post('/signup', data={
            'username': 'weakuser',
            'email': 'weak@example.com',
            'password': '123',  # Too short/common
            'confirm_password': '123'
        })
        assert response.status_code == 200
        assert b"security requirements" in response.data

def test_successful_login(client, sample_user):
    """Verify that signing in with correct credentials redirects to the dashboard."""
    response = client.post('/login', data={
        'email': sample_user.email,
        'password': 'Test@123456_Password'
    })
    assert response.status_code == 302
    assert '/dashboard' in response.headers['Location']

def test_login_wrong_password(app, sample_user):
    """Verify that login fails with incorrect credentials."""
    client = app.test_client()
    response = client.post('/login', data={
        'email': sample_user.email,
        'password': 'WrongPassword123'
    })
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data
