import pytest
from unittest.mock import patch, Mock
import os
from app.cli import init, update, compile
from click.testing import CliRunner

@pytest.fixture
def mock_os_system():
    """Fixture to mock os.system and return success (0) by default"""
    with patch('os.system') as mock_system:
        # Configure mock to return 0 (success) by default
        mock_system.return_value = 0
        yield mock_system

@pytest.fixture
def mock_os_remove():
    """Fixture to mock os.remove"""
    with patch('os.remove') as mock_remove:
        yield mock_remove

@pytest.fixture
def runner():
    """Fixture for CLI command testing"""
    return CliRunner()


def test_init_command_success(mock_os_system, mock_os_remove, runner):
    """Test the init command with successful execution"""
    # Execute the init command with 'es' language code
    result = runner.invoke(init, ['es'])
    
    # Verify command ran without errors
    assert result.exit_code == 0
    
    # Verify os.system was called twice with correct commands
    assert mock_os_system.call_count == 2
    mock_os_system.assert_any_call('pybabel extract -F babel.cfg -k _l -o messages.pot .')
    mock_os_system.assert_any_call('pybabel init -i messages.pot -d app/translations -l es')
    
    # Verify messages.pot was removed
    mock_os_remove.assert_called_once_with('messages.pot')


def test_init_command_extract_failure(mock_os_system, mock_os_remove, runner):
    """Test the init command with extract failure"""
    # Make the first os.system call fail
    mock_os_system.return_value = 1
    
    # Execute the command and expect an exception
    result = runner.invoke(init, ['es'], catch_exceptions=True)
    
    # Verify command failed with RuntimeError
    assert result.exit_code != 0
    # RuntimeError is caught but not displayed in output
    assert isinstance(result.exception, RuntimeError)
    assert 'extract command failed' in str(result.exception)
    
    # Verify os.system was called only once
    assert mock_os_system.call_count == 1
    
    # Verify os.remove was not called
    mock_os_remove.assert_not_called()


def test_init_command_init_failure(mock_os_system, mock_os_remove, runner):
    """Test the init command with init failure"""
    # Make the second os.system call fail
    original_side_effect = [0, 1]  # First call succeeds, second fails
    mock_os_system.side_effect = original_side_effect
    
    # Execute the command and expect an exception
    result = runner.invoke(init, ['es'], catch_exceptions=True)
    
    # Verify command failed with RuntimeError
    assert result.exit_code != 0
    # RuntimeError is caught but not displayed in output
    assert isinstance(result.exception, RuntimeError)
    assert 'init command failed' in str(result.exception)
    
    # Verify os.system was called twice
    assert mock_os_system.call_count == 2
    
    # Verify os.remove was not called
    mock_os_remove.assert_not_called()


def test_update_command_success(mock_os_system, mock_os_remove, runner):
    """Test the update command with successful execution"""
    # Execute the update command
    result = runner.invoke(update)
    
    # Verify command ran without errors
    assert result.exit_code == 0
    
    # Verify os.system was called twice with correct commands
    assert mock_os_system.call_count == 2
    mock_os_system.assert_any_call('pybabel extract -F babel.cfg -k _l -o messages.pot .')
    mock_os_system.assert_any_call('pybabel update -i messages.pot -d app/translations')
    
    # Verify messages.pot was removed
    mock_os_remove.assert_called_once_with('messages.pot')


def test_update_command_extract_failure(mock_os_system, mock_os_remove, runner):
    """Test the update command with extract failure"""
    # Make the first os.system call fail
    mock_os_system.return_value = 1
    
    # Execute the command and expect an exception
    result = runner.invoke(update, catch_exceptions=True)
    
    # Verify command failed with RuntimeError
    assert result.exit_code != 0
    # RuntimeError is caught but not displayed in output
    assert isinstance(result.exception, RuntimeError)
    assert 'extract command failed' in str(result.exception)
    
    # Verify os.remove was not called
    mock_os_remove.assert_not_called()


def test_update_command_update_failure(mock_os_system, mock_os_remove, runner):
    """Test the update command with update failure"""
    # Make the second os.system call fail
    original_side_effect = [0, 1]  # First call succeeds, second fails
    mock_os_system.side_effect = original_side_effect
    
    # Execute the command and expect an exception
    result = runner.invoke(update, catch_exceptions=True)
    
    # Verify command failed with RuntimeError
    assert result.exit_code != 0
    # RuntimeError is caught but not displayed in output
    assert isinstance(result.exception, RuntimeError)
    assert 'update command failed' in str(result.exception)
    
    # Verify os.remove was not called
    mock_os_remove.assert_not_called()


def test_compile_command_success(mock_os_system, runner):
    """Test the compile command with successful execution"""
    # Execute the compile command
    result = runner.invoke(compile)
    
    # Verify command ran without errors
    assert result.exit_code == 0
    
    # Verify os.system was called with correct command
    mock_os_system.assert_called_once_with('pybabel compile -d app/translations')


def test_compile_command_failure(mock_os_system, runner):
    """Test the compile command with failure"""
    # Make os.system call fail
    mock_os_system.return_value = 1
    
    # Execute the command and expect an exception
    result = runner.invoke(compile, catch_exceptions=True)
    
    # Verify command failed with RuntimeError
    assert result.exit_code != 0
    # RuntimeError is caught but not displayed in output
    assert isinstance(result.exception, RuntimeError)
    assert 'compile command failed' in str(result.exception)
