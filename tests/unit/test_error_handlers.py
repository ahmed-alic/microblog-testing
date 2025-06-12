import pytest
from flask import request, Flask
from unittest.mock import patch, Mock
from app.errors.handlers import wants_json_response, not_found_error, internal_error


def test_wants_json_response_html_preferred():
    """Test wants_json_response when HTML is preferred over JSON"""
    app = Flask(__name__)
    
    # Create test request context with accept header preferring HTML
    with app.test_request_context(headers={
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }):
        assert not wants_json_response()


def test_wants_json_response_json_preferred():
    """Test wants_json_response when JSON is preferred over HTML"""
    app = Flask(__name__)
    
    # Create test request context with accept header preferring JSON
    with app.test_request_context(headers={
        'Accept': 'application/json,text/html;q=0.9,*/*;q=0.8'
    }):
        assert wants_json_response()


def test_not_found_error_html():
    """Test 404 error handler with HTML client"""
    app = Flask(__name__)
    
    # Mock the wants_json_response function to return False (HTML client)
    with patch('app.errors.handlers.wants_json_response', return_value=False):
        # Mock render_template to avoid template rendering
        with patch('app.errors.handlers.render_template', return_value='mock 404 page') as mock_render:
            with app.test_request_context():
                response = not_found_error(Mock())
                
                # Verify render_template was called with correct template
                mock_render.assert_called_once_with('errors/404.html')
                
                # Verify response is a tuple with our mock page and 404 status
                assert response == ('mock 404 page', 404)


def test_not_found_error_json():
    """Test 404 error handler with JSON client"""
    app = Flask(__name__)
    
    # Mock the wants_json_response function to return True (JSON client)
    with patch('app.errors.handlers.wants_json_response', return_value=True):
        # Mock the API error response function
        with patch('app.errors.handlers.api_error_response', return_value={'error': 'Not found'}) as mock_api_error:
            with app.test_request_context():
                response = not_found_error(Mock())
                
                # Verify API error response was called with correct code
                mock_api_error.assert_called_once_with(404)
                
                # Verify response is the mock API error
                assert response == {'error': 'Not found'}


def test_internal_error_html():
    """Test 500 error handler with HTML client"""
    app = Flask(__name__)
    
    # Mock the database session
    with patch('app.errors.handlers.db.session') as mock_session:
        # Mock the wants_json_response function to return False (HTML client)
        with patch('app.errors.handlers.wants_json_response', return_value=False):
            # Mock render_template to avoid template rendering
            with patch('app.errors.handlers.render_template', return_value='mock 500 page') as mock_render:
                with app.test_request_context():
                    response = internal_error(Mock())
                    
                    # Verify session rollback was called
                    mock_session.rollback.assert_called_once()
                    
                    # Verify render_template was called with correct template
                    mock_render.assert_called_once_with('errors/500.html')
                    
                    # Verify response is a tuple with our mock page and 500 status
                    assert response == ('mock 500 page', 500)


def test_internal_error_json():
    """Test 500 error handler with JSON client"""
    app = Flask(__name__)
    
    # Mock the database session
    with patch('app.errors.handlers.db.session') as mock_session:
        # Mock the wants_json_response function to return True (JSON client)
        with patch('app.errors.handlers.wants_json_response', return_value=True):
            # Mock the API error response function
            with patch('app.errors.handlers.api_error_response', return_value={'error': 'Server error'}) as mock_api_error:
                with app.test_request_context():
                    response = internal_error(Mock())
                    
                    # Verify session rollback was called
                    mock_session.rollback.assert_called_once()
                    
                    # Verify API error response was called with correct code
                    mock_api_error.assert_called_once_with(500)
                    
                    # Verify response is the mock API error
                    assert response == {'error': 'Server error'}


def test_error_handlers_integration(client):
    """Integration test for error handlers"""
    # Test 404 error
    response = client.get('/nonexistent-page')
    assert response.status_code == 404
    
    # With JSON preferred
    headers = {'Accept': 'application/json,text/html;q=0.9'}
    response = client.get('/nonexistent-page', headers=headers)
    assert response.status_code == 404
    assert response.is_json
    json_data = response.get_json()
    
    # Check for error key (should be the HTTP status description)
    assert 'error' in json_data
    assert json_data['error'] == 'Not Found'  # HTTP_STATUS_CODES[404] is 'Not Found'
