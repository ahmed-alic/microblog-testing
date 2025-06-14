import os
import tempfile
import pytest
from app import create_app, db
from app.models import User, Post, Message, Notification, Task
from datetime import datetime, timedelta
from config import Config

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost.localdomain'
    ELASTICSEARCH_URL = None

@pytest.fixture(scope='function')
def regression_db():
    """Create a fresh database for each test"""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    # Override the database URI for testing
    test_config = TestConfig()
    test_config.SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    
    # Create app with test config
    app = create_app(test_config)
    
    # Create test context and database
    with app.app_context():
        db.create_all()
        yield db
    
    # Cleanup after test
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture(scope='function')
def regression_app(regression_db):
    """Create a test app with test database"""
    # Override the database URI for testing
    test_config = TestConfig()
    test_config.SQLALCHEMY_DATABASE_URI = regression_db.engine.url
    
    # Create app with test config
    app = create_app(test_config)
    
    with app.app_context():
        yield app

@pytest.fixture(scope='function')
def regression_client(regression_app):
    """Create a test client for the app"""
    with regression_app.test_client() as client:
        yield client

@pytest.fixture(scope='function')
def seed_regression_data(regression_db):
    """Create consistent data for regression tests"""
    # Create test users
    u1 = User(username='john', email='john@example.com')
    u1.set_password('test_password')
    u2 = User(username='susan', email='susan@example.com')
    u2.set_password('test_password')
    
    # Create test posts
    p1 = Post(body="John's test post", author=u1, timestamp=datetime.utcnow())
    p2 = Post(body="Susan's test post", author=u2, timestamp=datetime.utcnow() - timedelta(days=1))
    p3 = Post(body="Another post from John", author=u1, timestamp=datetime.utcnow() - timedelta(days=2))
    
    # Set up follow relationship
    u1.follow(u2)
    
    # Add test messages
    msg1 = Message(
        sender=u1, recipient=u2, body="Test message from John to Susan",
        timestamp=datetime.utcnow()
    )
    
    # Add test notification
    n1 = Notification(
        name='unread_message_count', 
        user=u2,
        timestamp=datetime.utcnow(),
        payload_json='{"count": 1}'
    )
    
    # Add all objects to session and commit
    regression_db.session.add_all([u1, u2, p1, p2, p3, msg1, n1])
    regression_db.session.commit()
    
    return {
        'users': {'john': u1, 'susan': u2},
        'posts': [p1, p2, p3],
        'messages': [msg1],
        'notifications': [n1]
    }

def pytest_configure(config):
    """Add regression marker to pytest configuration"""
    config.addinivalue_line(
        "markers", "regression: mark test as part of regression test suite"
    )
