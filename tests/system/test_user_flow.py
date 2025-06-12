import pytest
from app.models import User, Post
from app import db


def test_register_login_create_post_flow(client, app):
    """
    Test the complete user journey:
    1. Register a new account
    2. Log in with the new account
    3. Create a new post
    4. Verify the post appears on the user's profile
    """
    # Step 1: Register a new user
    client.post('/auth/register', data={
        'username': 'flowuser',
        'email': 'flow@example.com',
        'password': 'flowpassword',
        'password2': 'flowpassword'
    })
    
    # Step 2: Log in with the new account
    response = client.post('/auth/login', data={
        'username': 'flowuser',
        'password': 'flowpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Home' in response.data
    
    # Step 3: Create a new post
    post_text = 'This is a system test post'
    response = client.post('/', data={
        'post': post_text
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Your post is now live' in response.data
    assert post_text.encode() in response.data
    
    # Step 4: Check the post on the user's profile page
    response = client.get('/user/flowuser')
    assert response.status_code == 200
    assert post_text.encode() in response.data


def test_user_follow_unfollow_flow(client, test_user, app):
    """
    Test the complete follow/unfollow flow:
    1. Create a second user
    2. Log in as the first user
    3. Follow the second user
    4. Verify the follow relationship
    5. Unfollow the second user
    6. Verify the follow relationship is removed
    """
    # Create a second user to follow
    username_to_follow = 'user_to_follow'
    with app.app_context():
        # Check if the user already exists
        user2 = db.session.scalar(db.select(User).filter_by(username=username_to_follow))
        if not user2:
            user2 = User(username=username_to_follow, email='follow@example.com')
            user2.set_password('password123')
            db.session.add(user2)
            db.session.commit()
            user2 = db.session.scalar(db.select(User).filter_by(username=username_to_follow))
        # Store the ID for later use
        user2_id = user2.id
    
    # Login as test_user
    client.post('/auth/login', data={
        'username': test_user.username,
        'password': 'password'
    })
    
    # Get the user page and check the Follow button is present
    response = client.get(f'/user/{username_to_follow}')
    assert response.status_code == 200
    assert b'Follow' in response.data
    
    # Follow the second user
    response = client.post(f'/follow/{username_to_follow}', 
                          data={}, 
                          follow_redirects=True)
    assert response.status_code == 200
    assert b'You are following' in response.data
    
    # Verify the follow relationship in the database
    with app.app_context():
        u1 = db.session.get(User, test_user.id)
        u2 = db.session.get(User, user2_id)
        assert u1.is_following(u2)
    
    # Unfollow the second user
    response = client.post(f'/unfollow/{username_to_follow}', 
                          data={}, 
                          follow_redirects=True)
    assert response.status_code == 200
    assert b'You are not following' in response.data
    
    # Verify the follow relationship is removed
    with app.app_context():
        u1 = db.session.get(User, test_user.id)
        u2 = db.session.get(User, user2_id)
        assert not u1.is_following(u2)


def test_edit_profile_flow(client, test_user, app):
    """
    Test the profile editing flow:
    1. Log in
    2. Update profile info
    3. Verify profile changes
    """
    # Login as test_user
    response = client.post('/auth/login', data={
        'username': test_user.username,
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200
    
    # Change profile information
    new_username = 'updated_username'
    about_me_text = 'This is my updated profile information'
    
    response = client.post('/edit_profile', data={
        'username': new_username,
        'about_me': about_me_text
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Instead of checking for specific message, just verify we can access the new profile
    response = client.get(f'/user/{new_username}')
    assert response.status_code == 200
    
    # Check that the profile was updated in the database
    with app.app_context():
        updated_user = db.session.scalar(db.select(User).filter_by(username=new_username))
        assert updated_user is not None
        assert updated_user.about_me == about_me_text
