import json
import pytest
from app import db
from app.models import User


def test_get_user_api(client, test_user, app):
    """Test getting a user through the API."""
    # First get a token
    response = client.post('/api/tokens', auth=(test_user.username, 'password'))
    token = json.loads(response.data)['token']
    
    # Get the user via API
    response = client.get(f'/api/users/{test_user.id}',
                         headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    
    # Verify user data
    json_response = json.loads(response.data)
    assert json_response['username'] == test_user.username
    assert json_response['id'] == test_user.id


def test_get_users_api(client, test_user, app):
    """Test getting all users through the API."""
    # First get a token
    response = client.post('/api/tokens', auth=(test_user.username, 'password'))
    token = json.loads(response.data)['token']
    
    # Create additional users for testing pagination
    with app.app_context():
        # Check if the test users already exist first
        user2 = User.query.filter_by(username='testuser2').first()
        if not user2:
            user2 = User(username='testuser2', email='user2@example.com')
            user2.set_password('password')
            db.session.add(user2)
        
        user3 = User.query.filter_by(username='testuser3').first()
        if not user3:
            user3 = User(username='testuser3', email='user3@example.com')
            user3.set_password('password')
            db.session.add(user3)
            
        db.session.commit()
    
    # Get users via API - page 1, per_page=2
    response = client.get('/api/users?page=1&per_page=2',
                         headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    
    # Verify collection data
    json_response = json.loads(response.data)
    assert json_response['_meta']['total_items'] >= 3  # At least our 3 users
    assert len(json_response['items']) == 2  # 2 per page
    assert '_links' in json_response
    
    # Check if there's a next link (expected if we have more than 2 users)
    if json_response['_meta']['total_items'] > 2:
        assert 'next' in json_response['_links']
    
    # The API might include 'prev': None for the first page
    if 'prev' in json_response['_links']:
        assert json_response['_links']['prev'] is None  # For page 1, prev should be None


def test_get_followers_api(client, test_user, app):
    """Test getting a user's followers through the API."""
    # First get a token
    response = client.post('/api/tokens', auth=(test_user.username, 'password'))
    token = json.loads(response.data)['token']
    
    # Create another user that follows test_user
    follower_id = None
    with app.app_context():
        # Check if follower user already exists
        follower = User.query.filter_by(username='follower').first()
        if not follower:
            follower = User(username='follower', email='follower@example.com')
            follower.set_password('password')
            db.session.add(follower)
            db.session.commit()
        follower_id = follower.id
        
        # Get a fresh instance of test_user from the database
        db_test_user = User.query.get(test_user.id)
        
        # Make follower follow test_user if not already following
        if not follower.is_following(db_test_user):
            follower.follow(db_test_user)
            db.session.commit()
    
    # Get followers via API
    response = client.get(f'/api/users/{test_user.id}/followers',
                         headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    
    # Verify followers data
    json_response = json.loads(response.data)
    assert json_response['_meta']['total_items'] >= 1
    
    # Find the follower we created
    found_follower = False
    for item in json_response['items']:
        if item['id'] == follower_id:
            found_follower = True
            assert item['username'] == 'follower'
    assert found_follower, "Created follower was not found in the followers list"


def test_get_following_api(client, test_user, app):
    """Test getting users that a user is following through the API."""
    # First get a token
    response = client.post('/api/tokens', auth=(test_user.username, 'password'))
    token = json.loads(response.data)['token']
    
    # Create another user for test_user to follow
    followed_id = None
    with app.app_context():
        # Check if followed user already exists
        followed = User.query.filter_by(username='followed').first()
        if not followed:
            followed = User(username='followed', email='followed@example.com')
            followed.set_password('password')
            db.session.add(followed)
            db.session.commit()
        followed_id = followed.id
        
        # Get a fresh instance of test_user from the database
        db_test_user = User.query.get(test_user.id)
        
        # Make test_user follow the new user if not already following
        if not db_test_user.is_following(followed):
            db_test_user.follow(followed)
            db.session.commit()
    
    # Get following list via API
    response = client.get(f'/api/users/{test_user.id}/following',
                         headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    
    # Verify following data
    json_response = json.loads(response.data)
    assert json_response['_meta']['total_items'] >= 1
    
    # Find the followed user we created
    found_followed = False
    for item in json_response['items']:
        if item['id'] == followed_id:
            found_followed = True
            assert item['username'] == 'followed'
    assert found_followed, "Followed user was not found in the following list"


def test_create_user_api(client, app):
    """Test creating a new user through the API."""
    # Create data for new user
    user_data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'newpassword'
    }
    
    # Create user via API
    response = client.post('/api/users',
                         headers={'Content-Type': 'application/json'},
                         data=json.dumps(user_data))
    assert response.status_code == 201
    
    # Check Location header
    assert 'Location' in response.headers
    assert '/api/users/' in response.headers['Location']
    
    # Get the user ID from the Location header
    user_id = int(response.headers['Location'].split('/')[-1])
    
    # Verify user was created in DB
    with app.app_context():
        user = db.session.get(User, user_id)
        assert user is not None
        assert user.username == 'newuser'
        assert user.email == 'newuser@example.com'
        assert user.check_password('newpassword')


def test_create_user_missing_fields_api(client):
    """Test creating a user with missing required fields."""
    # Missing password
    user_data = {
        'username': 'incomplete',
        'email': 'incomplete@example.com'
    }
    
    # Try to create user via API
    response = client.post('/api/users',
                         headers={'Content-Type': 'application/json'},
                         data=json.dumps(user_data))
    assert response.status_code == 400
    
    # Just verify it's a 400 error, not the exact error message
    # since the API might not return the exact error wording we expect
    json_response = json.loads(response.data)
    assert 'error' in json_response


def test_create_user_duplicate_username_api(client, test_user):
    """Test creating a user with a duplicate username."""
    # Use existing username
    user_data = {
        'username': test_user.username,  # Already exists
        'email': 'different@example.com',
        'password': 'newpassword'
    }
    
    # Try to create user via API
    response = client.post('/api/users',
                         headers={'Content-Type': 'application/json'},
                         data=json.dumps(user_data))
    assert response.status_code == 400
    
    # Just verify it's a 400 error, not the exact error message
    json_response = json.loads(response.data)
    assert 'error' in json_response


def test_update_user_api(client, test_user, app):
    """Test updating a user through the API."""
    # First get a token
    response = client.post('/api/tokens', auth=(test_user.username, 'password'))
    token = json.loads(response.data)['token']
    
    # Update data
    update_data = {
        'about_me': 'New about me text via API'
    }
    
    # Update user via API
    response = client.put(f'/api/users/{test_user.id}',
                        headers={
                            'Authorization': f'Bearer {token}',
                            'Content-Type': 'application/json'
                        },
                        data=json.dumps(update_data))
    assert response.status_code == 200
    
    # Verify response
    json_response = json.loads(response.data)
    assert json_response['about_me'] == 'New about me text via API'
    
    # Query the database for the updated user instead of using the test_user object
    # which might be detached from the session
    with app.app_context():
        updated_user = User.query.get(test_user.id)
        assert updated_user.about_me == 'New about me text via API'


def test_update_user_unauthorized_api(client, test_user, app):
    """Test updating a different user's profile (should be unauthorized)."""
    # First get a token
    response = client.post('/api/tokens', auth=(test_user.username, 'password'))
    token = json.loads(response.data)['token']
    
    # Create another user
    with app.app_context():
        other_user = User(username='otheruser', email='other@example.com')
        other_user.set_password('password')
        db.session.add(other_user)
        db.session.commit()
        other_user_id = other_user.id
    
    # Update data
    update_data = {
        'about_me': 'Should not be allowed'
    }
    
    # Try to update other user via API
    response = client.put(f'/api/users/{other_user_id}',
                        headers={
                            'Authorization': f'Bearer {token}',
                            'Content-Type': 'application/json'
                        },
                        data=json.dumps(update_data))
    assert response.status_code == 403  # Forbidden
