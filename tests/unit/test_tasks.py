import unittest
from unittest.mock import patch, MagicMock, call
import json
from datetime import datetime, timezone
from flask import current_app
from app import create_app, db
from app.models import User, Post, Task
from app.tasks import _set_task_progress, export_posts
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    ELASTICSEARCH_URL = None
    REDIS_URL = None


class TasksTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create a test user with posts
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('password')
        db.session.add(self.user)
        
        # Create some test posts
        post1 = Post(body='Test post 1', author=self.user, 
                    timestamp=datetime.now(timezone.utc))
        post2 = Post(body='Test post 2', author=self.user,
                    timestamp=datetime.now(timezone.utc))
        db.session.add_all([post1, post2])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @patch('app.tasks.get_current_job')
    def test_set_task_progress(self, mock_get_job):
        """Test setting task progress"""
        # Setup mocks
        mock_job = MagicMock()
        mock_job.get_id.return_value = 'test_job_id'
        mock_job.meta = {}
        mock_get_job.return_value = mock_job
        
        # Create a task in the database
        task = Task(id='test_job_id', name='test_task', user=self.user, complete=False)
        db.session.add(task)
        db.session.commit()
        
        # Call the function
        _set_task_progress(50)
        
        # Assertions
        mock_job.save_meta.assert_called_once()
        self.assertEqual(mock_job.meta['progress'], 50)
        
        # Check the task is updated in the database
        task = db.session.get(Task, 'test_job_id')
        self.assertEqual(task.complete, False)
        
        # Test completion (100%)
        _set_task_progress(100)
        task = db.session.get(Task, 'test_job_id')
        self.assertEqual(task.complete, True)

    @patch('app.tasks.send_email')
    @patch('app.tasks._set_task_progress')
    @patch('app.tasks.get_current_job')
    @patch('time.sleep')  # Mock sleep to speed up test
    def test_export_posts(self, mock_sleep, mock_get_job, mock_set_progress, mock_send_email):
        """Test export posts functionality"""
        # Use the actual admin email from the config
        # Call the function
        export_posts(self.user.id)
        
        # Check progress was set
        # Initial, progress updates for 2 posts, and final 100%
        expected_calls = [call(0), call(50), call(100), call(100)]
        mock_set_progress.assert_has_calls(expected_calls)
        
        # Check email was sent
        mock_send_email.assert_called_once()
        
        # Verify email details
        call_args = mock_send_email.call_args
        self.assertEqual(call_args[1]['recipients'], [self.user.email])
        # Don't test the exact email, just verify it's used
        self.assertEqual(call_args[1]['sender'], current_app.config['ADMINS'][0])
        
        # Check attachment was created
        attachments = call_args[1]['attachments']
        self.assertEqual(len(attachments), 1)
        attachment_data = attachments[0]
        self.assertEqual(attachment_data[0], 'posts.json')
        self.assertEqual(attachment_data[1], 'application/json')
        
        # Verify JSON format
        json_data = json.loads(attachment_data[2])
        self.assertIn('posts', json_data)
        posts = json_data['posts']
        self.assertEqual(len(posts), 2)
        self.assertEqual(posts[0]['body'], 'Test post 1')
        self.assertEqual(posts[1]['body'], 'Test post 2')

    @patch('app.tasks.send_email')
    @patch('app.tasks._set_task_progress')
    def test_export_posts_exception_handling(self, mock_set_progress, mock_send_email):
        """Test error handling in export_posts"""
        # Make send_email raise an exception
        mock_send_email.side_effect = Exception("Test exception")
        
        # Call function
        export_posts(self.user.id)
        
        # Should still set final progress to 100%
        mock_set_progress.assert_called_with(100)


if __name__ == '__main__':
    unittest.main()
