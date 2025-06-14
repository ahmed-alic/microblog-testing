#!/usr/bin/env python
import pytest
import json
import base64
from datetime import datetime, timezone, timedelta
from app import db
from app.models import User, Post

@pytest.mark.regression
def test_password_hashing_regression(app):
    """Regression test for password hashing functionality"""
    u = User(username='regression_user')
    u.set_password('test_password')
    
    # Password should be properly hashed
    assert u.password_hash is not None
    assert u.password_hash != 'test_password'
    
    # Verification should work correctly
    assert u.check_password('test_password')
    assert not u.check_password('wrong_password')

@pytest.mark.regression
def test_user_avatar_regression(app, test_user):
    """Regression test for user avatar functionality"""
    # Test that avatar URL generation works
    assert 'gravatar.com' in test_user.avatar(128)
    
    # Different emails should generate different avatar URLs
    u1 = User(username='john', email='john@example.com')
    u2 = User(username='susan', email='susan@example.com')
    assert u1.avatar(128) != u2.avatar(128)

@pytest.mark.regression
def test_follow_unfollow_regression(app):
    """Regression test for user follow/unfollow functionality"""
    u1 = User(username='john', email='john@example.com')
    u2 = User(username='susan', email='susan@example.com')
    db.session.add_all([u1, u2])
    db.session.commit()
    
    # Test initial state
    assert not u1.is_following(u2)
    assert not u2.is_following(u1)
    
    # Test follow
    u1.follow(u2)
    db.session.commit()
    assert u1.is_following(u2)
    assert not u2.is_following(u1)
    assert u1.following_count() == 1
    assert u2.followers_count() == 1
    
    # Test unfollow
    u1.unfollow(u2)
    db.session.commit()
    assert not u1.is_following(u2)

@pytest.mark.regression
def test_login_logout_regression(client):
    """Regression test for login/logout functionality"""
    # Test login page access
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Sign In' in response.data
    
    # Create test user for login
    u = User(username='testlogin', email='testlogin@example.com')
    u.set_password('password')
    db.session.add(u)
    db.session.commit()
    
    # Test successful login
    response = client.post(
        '/auth/login',
        data={'username': 'testlogin', 'password': 'password'},
        follow_redirects=True
    )
    assert response.status_code == 200
    
    # Test logout
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Sign In' in response.data

@pytest.mark.regression
def test_api_token_regression(client):
    """Regression test for API token functionality"""
    # Create test user
    u = User(username='apiuser', email='apiuser@example.com')
    u.set_password('password')
    db.session.add(u)
    db.session.commit()
    
    # Create auth header
    credentials = base64.b64encode(b'apiuser:password').decode('utf-8')
    headers = {'Authorization': f'Basic {credentials}'}
    
    # Request token
    response = client.post('/api/tokens', headers=headers)
    assert response.status_code == 200
    json_data = json.loads(response.data)
    assert 'token' in json_data
    
@pytest.mark.regression
def test_post_creation_regression(app, client):
    """Regression test for post creation"""
    # Create and log in user
    u = User(username='postuser', email='postuser@example.com')
    u.set_password('password')
    db.session.add(u)
    db.session.commit()
    
    client.post(
        '/auth/login',
        data={'username': 'postuser', 'password': 'password'},
        follow_redirects=True
    )
    
    # Submit post
    response = client.post(
        '/',
        data={'post': 'Test regression post'},
        follow_redirects=True
    )
    
    assert response.status_code == 200
    
    # Verify post was created
    post = Post.query.filter_by(body='Test regression post').first()
    assert post is not None
    assert post.author.username == 'postuser'
