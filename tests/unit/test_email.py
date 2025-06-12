import unittest
from unittest.mock import patch, MagicMock, call
from flask import Flask
from flask_mail import Message
from app.email import send_email, send_async_email


class EmailTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch('app.email.mail')
    def test_send_async_email(self, mock_mail):
        """Test the async email helper function"""
        # Create mock message
        msg = MagicMock()
        
        # Call function
        send_async_email(self.app, msg)
        
        # Verify
        mock_mail.send.assert_called_once_with(msg)

    @patch('app.email.mail')
    def test_send_email_sync(self, mock_mail):
        """Test synchronous email sending"""
        # Call function with sync=True
        send_email(
            subject='Test Subject',
            sender='test@example.com',
            recipients=['recipient@example.com'],
            text_body='Test text',
            html_body='<p>Test HTML</p>',
            sync=True
        )
        
        # Verify
        mock_mail.send.assert_called_once()
        msg = mock_mail.send.call_args[0][0]
        self.assertEqual(msg.subject, 'Test Subject')
        self.assertEqual(msg.sender, 'test@example.com')
        self.assertEqual(msg.recipients, ['recipient@example.com'])
        self.assertEqual(msg.body, 'Test text')
        self.assertEqual(msg.html, '<p>Test HTML</p>')

    @patch('app.email.Thread')
    def test_send_email_async(self, mock_thread):
        """Test asynchronous email sending"""
        # Call function with default sync=False
        send_email(
            subject='Test Subject',
            sender='test@example.com',
            recipients=['recipient@example.com'],
            text_body='Test text',
            html_body='<p>Test HTML</p>'
        )
        
        # Verify thread was started
        mock_thread.assert_called_once()
        thread_call = mock_thread.call_args
        self.assertEqual(thread_call[1]['target'], send_async_email)
        
        # Verify message parameters - we can only check that args[1] is a Message object
        # since we can't easily mock Flask's current_app._get_current_object()
        self.assertIsInstance(thread_call[1]['args'][1], Message)
        msg = thread_call[1]['args'][1]
        self.assertEqual(msg.subject, 'Test Subject')
        self.assertEqual(msg.sender, 'test@example.com')
        self.assertEqual(msg.recipients, ['recipient@example.com'])
        self.assertEqual(msg.body, 'Test text')
        self.assertEqual(msg.html, '<p>Test HTML</p>')

    @patch('app.email.Message')
    @patch('app.email.mail')
    def test_send_email_with_attachments(self, mock_mail, mock_message_class):
        """Test email sending with attachments"""
        # Create test attachments
        attachments = [
            ('file1.txt', 'text/plain', 'File 1 content'),
            ('file2.pdf', 'application/pdf', b'Binary content')
        ]
        
        # Setup mock message
        mock_msg = MagicMock()
        mock_message_class.return_value = mock_msg
        
        # Call function
        send_email(
            subject='Test Subject',
            sender='test@example.com',
            recipients=['recipient@example.com'],
            text_body='Test text',
            html_body='<p>Test HTML</p>',
            attachments=attachments,
            sync=True  # Use sync for easier verification
        )
        
        # Verify
        mock_mail.send.assert_called_once_with(mock_msg)
        
        # Check message creation
        mock_message_class.assert_called_once_with(
            'Test Subject', 
            sender='test@example.com', 
            recipients=['recipient@example.com']
        )
        
        # Check message body setup
        self.assertEqual(mock_msg.body, 'Test text')
        self.assertEqual(mock_msg.html, '<p>Test HTML</p>')
        
        # Check that attach was called for each attachment
        expected_calls = [
            call(*attachments[0]),
            call(*attachments[1])
        ]
        self.assertEqual(mock_msg.attach.call_args_list, expected_calls)


if __name__ == '__main__':
    unittest.main()
