import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Add the project root to sys.path to fix imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set up mocks for external services
patch('redis.Redis', return_value=MagicMock()).start()
patch('flask_mail.Mail', return_value=MagicMock()).start()
patch('elasticsearch.Elasticsearch', return_value=MagicMock()).start()
patch('rq.Queue', return_value=MagicMock()).start()

# Now we can safely import
import config
from app import create_app, db
from app.models import User, Post


class TestConfig(config.Config):
    TESTING = True
    SERVER_NAME = 'localhost.localdomain'
    APPLICATION_ROOT = '/'
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # Use in-memory SQLite for tests
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing
    ELASTICSEARCH_URL = None  # Disable Elasticsearch for testing
    REDIS_URL = None  # Disable Redis
    MAIL_SERVER = None  # Disable email
    LANGUAGES = ['en']  # Simplify languages
    POSTS_PER_PAGE = 3  # Smaller pagination for faster tests
    ELASTICSEARCH_TIMEOUT = 0.01  # Fast timeout for search tests


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app(TestConfig)
    
    # Create a test context
    with app.app_context():
        # Create all database tables
        db.create_all()
        yield app
        # Clean up after test
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    with app.test_client() as client:
        with app.app_context():
            # Ensure database is set up
            db.create_all()
            yield client


@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """Create a test user for the tests."""
    with app.app_context():
        # Check if user exists first to avoid duplicate key errors
        user = db.session.scalar(db.select(User).filter_by(username='testuser'))
        if not user:
            user = User(username='testuser', email='testuser@example.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
        # Always refresh the user to ensure it's attached to the current session
        user_id = user.id
        # Get a fresh instance from the database to avoid detached instance errors
        return db.session.scalar(db.select(User).filter_by(id=user_id))


@pytest.fixture
def test_post(app, test_user):
    """Create a test post for the tests."""
    with app.app_context():
        # Check if post exists first to avoid duplicate key errors
        post = db.session.scalar(db.select(Post).filter_by(body='This is a test post'))
        if not post:
            post = Post(body='This is a test post', author=test_user)
            db.session.add(post)
            db.session.commit()
        # Always refresh the post to ensure it's attached to the current session
        post_id = post.id
        # Get a fresh instance to avoid detached instance errors
        return db.session.scalar(db.select(Post).filter_by(id=post_id))


@pytest.fixture
def auth_client(client, test_user, app):
    """Returns an authenticated client."""
    with app.app_context():
        # Ensure user is attached to current session
        user = db.session.scalar(db.select(User).filter_by(id=test_user.id))
        client.post('/auth/login', data={
            'username': user.username,
            'password': 'password'
        }, follow_redirects=True)
        return client
