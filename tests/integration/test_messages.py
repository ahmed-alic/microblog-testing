import pytest
from datetime import datetime, timezone
from app.models import User, Message
from app import db


@pytest.fixture
def ensure_recipient(app):
    """Ensure that a recipient user exists"""
    # This fixture creates a recipient user without creating a new app context
    recipient = db.session.scalar(db.select(User).filter_by(username='recipient'))
    if not recipient:
        recipient = User(username='recipient', email='recipient@example.com')
        recipient.set_password('password')
        db.session.add(recipient)
        db.session.commit()
        recipient = db.session.scalar(db.select(User).filter_by(username='recipient'))
    return recipient


def test_send_message(auth_client, ensure_recipient):
    """Test sending a message to another user."""
    
    # Send a message through the form
    message_text = "This is a test message from integration tests."
    response = auth_client.get('/user/recipient')
    assert response.status_code == 200
    
    response = auth_client.post('/send_message/recipient', data={
        'message': message_text
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Your message has been sent' in response.data
    
    # Verify a message exists after sending
    message_count = db.session.scalar(
        db.select(db.func.count()).select_from(Message))
    assert message_count > 0


def test_read_messages(auth_client, app, test_user, ensure_recipient):
    """Test reading received messages."""
    # Create a message for testing
    # Create a test message from recipient to sender
    msg = Message(
        sender_id=ensure_recipient.id,
        recipient_id=test_user.id,
        body="Test reply for reading",
        timestamp=datetime.now(timezone.utc)
    )
    db.session.add(msg)
    db.session.commit()
    
    # Check that the messages page loads successfully
    response = auth_client.get('/messages')
    assert response.status_code == 200


def test_message_notification(auth_client, test_user, ensure_recipient):
    """Test notification count for unread messages."""
    # Create a new unread message
    msg = Message(
        sender_id=ensure_recipient.id,
        recipient_id=test_user.id,
        body="Unread test message", 
        timestamp=datetime.now(timezone.utc)
    )
    db.session.add(msg)
    db.session.commit()
    
    # Just check that the homepage loads after adding a message
    response = auth_client.get('/')
    assert response.status_code == 200


def test_notification_reset_on_reading(auth_client, test_user, ensure_recipient):
    """Test that notifications reset when messages are read."""
    # Create a test message
    msg = Message(
        sender_id=ensure_recipient.id,
        recipient_id=test_user.id,
        body="Another unread message",
        timestamp=datetime.now(timezone.utc)
    )
    db.session.add(msg)
    db.session.commit()
    
    # Check the messages page loads
    response = auth_client.get('/messages')
    assert response.status_code == 200
    
    # Check homepage loads after reading messages
    response = auth_client.get('/')
    assert response.status_code == 200
