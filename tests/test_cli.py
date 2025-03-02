
from unittest.mock import patch, mock_open, MagicMock

from ion_cli.cli import (
    validate_file, validate_email, upload_file, 
    check_user_verified, main
)


# Test validate_file function
def test_validate_file_nonexistent():
    with patch('os.path.exists', return_value=False):
        assert validate_file('nonexistent.txt') is False


def test_validate_file_binary():
    with patch('os.path.exists', return_value=True):
        with patch('builtins.open', mock_open(read_data='\0binary data')):
            assert validate_file('binary.txt') is False


def test_validate_file_unicode_error():
    with patch('os.path.exists', return_value=True):
        with patch('builtins.open', side_effect=UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid')):
            assert validate_file('invalid_encoding.txt') is False


def test_validate_file_valid():
    with patch('os.path.exists', return_value=True):
        with patch('builtins.open', mock_open(read_data='valid text content')):
            assert validate_file('valid.txt') is True


# Test validate_email function
def test_validate_email_invalid_no_at():
    assert validate_email('invalid-email.com') is False


def test_validate_email_invalid_no_dot():
    assert validate_email('invalid@emailcom') is False


def test_validate_email_valid():
    assert validate_email('valid@email.com') is True


# Test upload_file function
def test_upload_file_success():
    with patch('builtins.open', mock_open(read_data='file content')):
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            assert upload_file('file.txt', 'user@example.com') is True


def test_upload_file_failure():
    with patch('builtins.open', mock_open(read_data='file content')):
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.text = 'Bad request'
            mock_post.return_value = mock_response
            
            assert upload_file('file.txt', 'user@example.com') is False


# Test check_user_verified function
def test_check_user_verified_no_email():
    with patch.dict('os.environ', {}, clear=True):
        assert check_user_verified() is None


def test_check_user_verified_from_env():
    with patch.dict('os.environ', {'ION_USER_EMAIL': 'user@example.com'}):
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "user_id": "1234567890"
            }
            mock_post.return_value = mock_response
            
            assert check_user_verified() == "1234567890"


def test_check_user_verified_success():
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "user_id": "1234567890"
        }
        mock_post.return_value = mock_response
        
        assert check_user_verified('user@example.com') == "1234567890"


def test_check_user_verified_failure():
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response
        
        assert check_user_verified('user@example.com') is None


# Test main function
def test_main_no_email():
    with patch.dict('os.environ', {}, clear=True):
        assert main(['--file', 'file.txt']) == 1


def test_main_no_file():
    with patch('ion_upload.cli.check_user_verified', return_value=True):
        with patch.dict('os.environ', {'ION_USER_EMAIL': 'user@example.com'}):
            assert main(['--user_email', 'user@example.com']) == 1


def test_main_invalid_file():
    with patch('ion_upload.cli.check_user_verified', return_value=True):
        with patch('ion_upload.cli.validate_file', return_value=False):
            assert main(['--user_email', 'user@example.com', '--file', 'invalid.txt']) == 1


def test_main_invalid_email():
    with patch('ion_upload.cli.check_user_verified', return_value=True):
        with patch('ion_upload.cli.validate_file', return_value=True):
            with patch('ion_upload.cli.validate_email', return_value=False):
                assert main(['--user_email', 'invalid', '--file', 'file.txt']) == 1


def test_main_success():
    with patch('ion_upload.cli.check_user_verified', return_value=True):
        with patch('ion_upload.cli.validate_file', return_value=True):
            with patch('ion_upload.cli.validate_email', return_value=True):
                with patch('ion_upload.cli.upload_file', return_value=True):
                    assert main(['--user_email', 'user@example.com', '--file', 'file.txt']) == 0


def test_main_no_args():
    with patch.dict('os.environ', {}, clear=True):
        assert main([]) == 1 