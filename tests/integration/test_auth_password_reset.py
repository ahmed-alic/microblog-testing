import pytest
from flask import url_for
from unittest.mock import patch
from app import db
from app.models import User


def test_reset_password_request_page(client):
    """Test that password reset request page loads correctly."""
    response = client.get('/auth/reset_password_request')
    assert response.status_code == 200
    assert b'Reset Password' in response.data


def test_reset_password_request_submit(client, app):
    """Test submitting password reset request."""
    with patch('app.auth.routes.send_password_reset_email') as mock_send_email:
        # Submit with existing email
        with app.app_context():
            # Create a test user first
            user = User(username='resetuser', email='reset@example.com')
            user.set_password('testpassword')
            db.session.add(user)
            db.session.commit()
            
        response = client.post('/auth/reset_password_request', data={
            'email': 'reset@example.com'
        }, follow_redirects=True)
        
        # Verify response and that email was sent
        assert response.status_code == 200
        assert b'Check your email' in response.data
        mock_send_email.assert_called_once()
        
        # Submit with non-existent email
        mock_send_email.reset_mock()
        response = client.post('/auth/reset_password_request', data={
            'email': 'nonexistent@example.com'
        }, follow_redirects=True)
        
        # Should still show success message even though email doesn't exist
        # (security best practice not to reveal if email exists)
        assert response.status_code == 200
        assert b'Check your email' in response.data
        assert not mock_send_email.called


def test_reset_password_with_token(client, app):
    """Test password reset with token."""
    with app.app_context():
        # Create a test user
        user = User(username='pwresetuser', email='pwreset@example.com')
        user.set_password('oldpassword')
        db.session.add(user)
        db.session.commit()
        
        # Generate reset token
        token = user.get_reset_password_token()
    
    # Test the reset password page loads with valid token
    response = client.get(f'/auth/reset_password/{token}')
    assert response.status_code == 200
    assert b'Reset Your Password' in response.data
    
    # Submit new password
    response = client.post(f'/auth/reset_password/{token}', data={
        'password': 'newpassword123',
        'password2': 'newpassword123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Your password has been reset' in response.data
    assert b'Sign In' in response.data
    
    # Verify password was changed
    with app.app_context():
        user = db.session.scalar(db.select(User).filter_by(email='pwreset@example.com'))
        assert user is not None
        assert user.check_password('newpassword123')


def test_reset_password_invalid_token(client):
    """Test password reset with invalid token."""
    response = client.get('/auth/reset_password/invalid-token')
    assert response.status_code == 302  # Redirect to index
    
    response = client.post('/auth/reset_password/invalid-token', data={
        'password': 'newpassword',
        'password2': 'newpassword'
    })
    assert response.status_code == 302  # Redirect to index


def test_reset_password_logged_in(client, test_user):
    """Test accessing reset password when already logged in."""
    # Login first
    client.post('/auth/login', data={
        'username': test_user.username,
        'password': 'password123',
        'remember_me': False
    })
    
    # Try to access reset password request page while logged in
    response = client.get('/auth/reset_password_request')
    # In this implementation, it redirects if current_user.is_authenticated
    # Let's follow the redirect to verify we end up at the index page
    response = client.get('/auth/reset_password_request', follow_redirects=True)
    assert b'Home' in response.data
    
    # Try to access reset password page while logged in
    response = client.get('/auth/reset_password/some-token', follow_redirects=True)
    assert b'Home' in response.data  # Should show home page content after redirect


def test_login_with_next_parameter(client, test_user):
    """Test login with next parameter."""
    # Login with next parameter
    response = client.post('/auth/login?next=%2Findex', data={
        'username': test_user.username,
        'password': 'password123',
        'remember_me': False
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Home' in response.data


def test_login_with_invalid_next_parameter(client, test_user):
    """Test login with invalid next parameter (external URL)."""
    # Login with external URL in next parameter
    response = client.post('/auth/login?next=http://malicious-site.com', data={
        'username': test_user.username,
        'password': 'password123',
        'remember_me': False
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Home' in response.data  # Should redirect to home, not external site
