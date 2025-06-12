import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_babel import Babel
from app.translate import translate
from config import Config


class TestConfig(Config):
    TESTING = True
    MS_TRANSLATOR_KEY = 'test_key'  # Mock API key for testing


class TranslateTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.from_object(TestConfig)
        self.babel = Babel(self.app)
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_missing_translator_key(self):
        """Test behavior when translator key is not configured"""
        self.app.config['MS_TRANSLATOR_KEY'] = None
        result = translate('Hello', 'en', 'es')
        self.assertIn('Error: the translation service is not configured', result)

    @patch('app.translate.requests.post')
    def test_translate_error_status_code(self, mock_post):
        """Test handling of non-200 status code from translation API"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        result = translate('Hello', 'en', 'es')
        self.assertIn('Error: the translation service failed', result)

        # Verify the API was called with correct parameters
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn('translate?api-version=3.0&from=en&to=es', args[0])
        self.assertEqual(kwargs['headers']['Ocp-Apim-Subscription-Key'], 'test_key')

    @patch('app.translate.requests.post')
    def test_translate_success(self, mock_post):
        """Test successful translation"""
        # Mock a successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            'translations': [{'text': 'Hola'}]
        }]
        mock_post.return_value = mock_response

        # Call the translate function
        result = translate('Hello', 'en', 'es')
        
        # Verify results
        self.assertEqual(result, 'Hola')
        
        # Check API was called correctly
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn('/translate?api-version=3.0&from=en&to=es', args[0])
        self.assertEqual(kwargs['json'][0]['Text'], 'Hello')
        self.assertEqual(kwargs['headers']['Ocp-Apim-Subscription-Key'], 'test_key')
        self.assertEqual(kwargs['headers']['Ocp-Apim-Subscription-Region'], 'westus')


if __name__ == '__main__':
    unittest.main()
