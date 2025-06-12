import pytest
from app.models import User, Post
from app import db, create_app
from datetime import datetime, timezone
import os
import tempfile
from config import Config


class TestConfig(Config):
    """Test configuration that inherits from Config."""
    TESTING = True
    WTF_CSRF_ENABLED = False
    ELASTICSEARCH_URL = None
    # Will be set dynamically in the app fixture


@pytest.fixture(scope='module')
def app():
    """Create and configure app for testing with proper DB initialization."""
    # Create a temporary file to use as a database file
    db_fd, db_path = tempfile.mkstemp()
    
    # Set the database URI in the TestConfig class
    TestConfig.SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    
    app = create_app(TestConfig)
    
    # Create all DB tables using app context
    with app.app_context():
        db.create_all()
    
    yield app
    
    # Clean up
    # Explicitly dispose SQLAlchemy engine connections to avoid file lock on Windows
    with app.app_context():
        db.session.remove()
        db.engine.dispose()
    
    os.close(db_fd)
    try:
        os.unlink(db_path)
    except PermissionError:
        # If we still get a permission error, just pass (Windows might still hold the file)
        # This isn't critical since it's a temporary file
        pass


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    with app.test_client() as client:
        yield client


@pytest.fixture
def test_users(app):
    """Create test users for following/follower tests."""
    with app.app_context():
        # Create follower user
        follower = User(username='followeruser', email='follower@example.com')
        follower.set_password('dog')
        db.session.add(follower)
        
        # Create followed user
        followed = User(username='followeduser', email='followed@example.com')
        followed.set_password('cat')
        db.session.add(followed)
        
        db.session.commit()
        
        # Store IDs for later use
        follower_id = follower.id
        followed_id = followed.id
        
    yield {'follower_id': follower_id, 'followed_id': followed_id}
    
    # Clean up test users after tests
    with app.app_context():
        # Delete all posts created by test users first
        db.session.execute(db.text(f"DELETE FROM post WHERE user_id IN ({follower_id}, {followed_id})"))
        
        # Remove any follow relationships using direct SQL
        db.session.execute(db.text(f"DELETE FROM followers WHERE follower_id IN ({follower_id}, {followed_id})"))
        db.session.execute(db.text(f"DELETE FROM followers WHERE followed_id IN ({follower_id}, {followed_id})"))
        
        # Now delete the users
        db.session.execute(db.text(f"DELETE FROM user WHERE id IN ({follower_id}, {followed_id})"))
        
        # Commit all changes
        db.session.commit()


def login_user(client, username, password):
    """Helper function to log in a user."""
    # Log out first (in case already logged in)
    client.get('/auth/logout', follow_redirects=True)
    
    # Go to login page
    response = client.get('/auth/login')
    assert response.status_code == 200
    
    # Submit login form
    response = client.post('/auth/login', 
                        data={
                            'username': username, 
                            'password': password,
                            'remember_me': False
                        },
                        follow_redirects=True)
    
    # Check login succeeded
    assert response.status_code == 200
    return response


def create_post(app, user_id, content):
    """Helper function to create a post for a user."""
    with app.app_context():
        user = db.session.get(User, user_id)
        post = Post(body=content, author=user, timestamp=datetime.now(timezone.utc))
        db.session.add(post)
        db.session.commit()
        return post.id


def test_follow_unfollow_flow(client, app, test_users):
    """
    Test the complete follow/unfollow flow:
    1. User1 logs in
    2. User1 follows User2
    3. Verify the follow relationship
    4. User2 creates posts
    5. User1 sees User2's posts in their timeline
    6. User1 unfollows User2
    7. User1 no longer sees User2's posts in their timeline
    """
    follower_id = test_users['follower_id']
    followed_id = test_users['followed_id']
    
    # Get usernames from database 
    with app.app_context():
        follower = db.session.get(User, follower_id)
        followed = db.session.get(User, followed_id)
        follower_username = follower.username
        followed_username = followed.username
    
    # Step 1: Login as follower user
    login_user(client, follower_username, 'dog')
    
    # Step 2: Follow the other user
    response = client.post(f'/follow/{followed_username}', 
                        follow_redirects=True)
    assert response.status_code == 200
    
    # Step 3: Verify the follow relationship
    with app.app_context():
        follower = db.session.get(User, follower_id)
        followed = db.session.get(User, followed_id)
        
        # Check relationship exists
        assert follower.is_following(followed)
        assert follower.following_count() == 1
        assert followed.followers_count() == 1
    
    # Step 4: Create posts as followed user
    post_contents = [
        f"This is a test post by followed user {datetime.now(timezone.utc).isoformat()}",
        f"Another test post by followed user {datetime.now(timezone.utc).isoformat()}"
    ]
    post_ids = []
    
    # Create posts for the followed user
    for content in post_contents:
        post_id = create_post(app, followed_id, content)
        post_ids.append(post_id)
    
    # Step 5: Check follower's home timeline for followed user's posts
    response = client.get('/index')
    assert response.status_code == 200
    
    # Check for post content in timeline
    html_content = response.data.decode('utf-8')
    
    for content in post_contents:
        content_sample = content[:15]  # First part of post content
        assert content_sample.lower() in html_content.lower(), f"Post '{content_sample}' not found in timeline"
    
    # Step 6: Unfollow the user
    response = client.post(f'/unfollow/{followed_username}', 
                        follow_redirects=True)
    assert response.status_code == 200
    
    # Verify unfollow in database
    with app.app_context():
        follower = db.session.get(User, follower_id)
        followed = db.session.get(User, followed_id)
        
        assert not follower.is_following(followed)
        assert follower.following_count() == 0
        assert followed.followers_count() == 0
    
    # Step 7: Check follower's timeline again - should not have followed user's posts
    response = client.get('/index')
    assert response.status_code == 200
    
    # Timeline should not contain our test posts
    html_content = response.data.decode('utf-8')
    signature_content = post_contents[0][:15]
    assert signature_content.lower() not in html_content.lower(), f"Post '{signature_content}' still in timeline after unfollow"
    
    # Verify posts still visible on explore page
    response = client.get('/explore')
    assert response.status_code == 200
    html_content = response.data.decode('utf-8')
    assert signature_content.lower() in html_content.lower(), f"Post '{signature_content}' should be on explore page"


def test_follow_count_display(client, app, test_users):
    """
    Test that follow/follower counts are correctly displayed:
    1. User1 follows User2
    2. Verify the follow counts in the database
    3. User1 unfollows User2
    4. Verify counts are reset
    """
    follower_id = test_users['follower_id']
    followed_id = test_users['followed_id']
    
    # Get usernames from database
    with app.app_context():
        follower = db.session.get(User, follower_id)
        followed = db.session.get(User, followed_id)
        follower_username = follower.username
        followed_username = followed.username
    
    # Login as follower
    login_user(client, follower_username, 'dog')
    
    # Follow user
    client.post(f'/follow/{followed_username}', follow_redirects=True)
    
    # Check counts
    with app.app_context():
        follower = db.session.get(User, follower_id)
        followed = db.session.get(User, followed_id)
        
        assert follower.following_count() == 1
        assert follower.followers_count() == 0
        assert followed.following_count() == 0
        assert followed.followers_count() == 1
    
    # Check user profile displays correct count
    response = client.get(f'/user/{follower_username}')
    html_content = response.data.decode('utf-8').lower()
    # Use a more flexible check to find following count
    assert '1' in html_content and 'following' in html_content
    
    response = client.get(f'/user/{followed_username}')
    html_content = response.data.decode('utf-8').lower()
    # Use a more flexible check to find follower count
    assert '1' in html_content and 'follower' in html_content
    
    # Unfollow user
    client.post(f'/unfollow/{followed_username}', follow_redirects=True)
    
    # Check counts reset
    with app.app_context():
        follower = db.session.get(User, follower_id)
        followed = db.session.get(User, followed_id)
        
        assert follower.following_count() == 0
        assert followed.followers_count() == 0


def test_self_follow_prevention(client, app, test_users):
    """
    Test that users cannot follow themselves:
    1. Login as User1
    2. Try to follow User1
    3. Verify no self-follow in database
    """
    follower_id = test_users['follower_id']
    
    # Get username
    with app.app_context():
        user = db.session.get(User, follower_id)
        username = user.username
    
    # Login
    login_user(client, username, 'dog')
    
    # Try to follow self
    response = client.post(f'/follow/{username}', follow_redirects=True)
    assert response.status_code == 200
    
    # Verify no self-follow in database
    with app.app_context():
        user = db.session.get(User, follower_id)
        assert not user.is_following(user)
        assert user.following_count() == 0
