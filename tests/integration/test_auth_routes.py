import pytest
from flask import url_for
from app.models import User
from app import db


def test_login_page(client):
    """Test that login page loads correctly."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Sign In' in response.data


def test_register_page(client):
    """Test that register page loads correctly."""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Register' in response.data


def test_successful_login_logout(client, test_user):
    """Test successful login and logout."""
    # Test login
    response = client.post('/auth/login', data={
        'username': test_user.username,
        'password': 'password123',
        'remember_me': False
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Home' in response.data
    
    # Test logout
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Sign In' in response.data


def test_invalid_login(client, test_user):
    """Test login with invalid credentials."""
    response = client.post('/auth/login', data={
        'username': test_user.username,
        'password': 'wrongpassword',
        'remember_me': False
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data


def test_register_new_user(client, app):
    """Test user registration process."""
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'newpassword123',
        'password2': 'newpassword123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Congratulations' in response.data
    assert b'Sign In' in response.data
    
    # Verify the user was actually created
    with app.app_context():
        user = db.session.scalar(
            db.select(User).filter_by(username='newuser'))
        assert user is not None
        assert user.email == 'newuser@example.com'
        assert user.check_password('newpassword123')


def test_register_existing_username(client, test_user):
    """Test registration with existing username."""
    response = client.post('/auth/register', data={
        'username': test_user.username,  # Already exists
        'email': 'different@example.com',
        'password': 'newpassword',
        'password2': 'newpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Please use a different username' in response.data


def test_register_existing_email(client, test_user):
    """Test registration with existing email."""
    response = client.post('/auth/register', data={
        'username': 'differentuser',
        'email': test_user.email,  # Already exists
        'password': 'newpassword',
        'password2': 'newpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Please use a different email address' in response.data


def test_register_mismatched_passwords(client):
    """Test registration with mismatched passwords."""
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password1',
        'password2': 'password2'  # Different password
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Field must be equal to password' in response.data
