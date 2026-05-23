from flask import session
from flask_login import current_user

def test_protected_route_without_login(app):
    """Verify that unauthenticated access to the dashboard redirects to the login screen."""
    client = app.test_client()
    response = client.get('/dashboard')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_login_creates_session(app, sample_user):
    """Verify that submitting valid credentials logs the user in and establishes a session."""
    client = app.test_client()
    response = client.post('/login', data={
        'email': sample_user.email,
        'password': 'Test@123456_Password'  # Plaintext password of conftest sample_user
    })
    
    assert response.status_code == 302
    # Verify redirected to dashboard
    assert response.headers['Location'].endswith('/dashboard')
    
    # Access dashboard with authenticated client
    dashboard_resp = client.get('/dashboard')
    assert dashboard_resp.status_code == 200
    assert b"Welcome back" in dashboard_resp.data

def test_logout_clears_session(app, sample_user):
    """Verify that logging out clears the user session and blocks access to protected paths."""
    client = app.test_client()
    # Log in first
    client.post('/login', data={
        'email': sample_user.email,
        'password': 'Test@123456_Password'
    })
    
    # Verify dashboard accessible
    assert client.get('/dashboard').status_code == 200
    
    # Log out
    logout_resp = client.get('/logout')
    assert logout_resp.status_code == 302
    
    # Verify dashboard now blocked
    assert client.get('/dashboard').status_code == 302

def test_session_cookie_httponly(app, sample_user):
    """Verify that the session cookie has HttpOnly and SameSite=Lax flags set."""
    client = app.test_client()
    response = client.post('/login', data={
        'email': sample_user.email,
        'password': 'Test@123456_Password'
    })
    
    # Search for the session cookie headers
    cookies = response.headers.getlist('Set-Cookie')
    session_cookie = None
    for cookie in cookies:
        if 'session=' in cookie:
            session_cookie = cookie
            break
            
    assert session_cookie is not None
    assert 'HttpOnly' in session_cookie
    assert 'SameSite=Lax' in session_cookie
