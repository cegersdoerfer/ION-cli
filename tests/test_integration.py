import os
import pytest
import tempfile
import subprocess
from ion_cli.config import DEFAULT_API_ENDPOINT

# Set up the test environment to use your local server
@pytest.fixture(scope="module")
def setup_test_env():
    # Store the original endpoint URL
    original_endpoint = os.environ.get("ION_API_ENDPOINT", DEFAULT_API_ENDPOINT)
    print(f"Original endpoint: {original_endpoint}")
    
    # Set the endpoint to your local server
    os.environ["ION_API_ENDPOINT"] = "http://127.0.0.1:5000/api"
    print(f"Set endpoint to: {os.environ['ION_API_ENDPOINT']}")
    
    yield
    
    # Restore the original endpoint URL if needed
    if original_endpoint != os.environ["ION_API_ENDPOINT"]:
        os.environ["ION_API_ENDPOINT"] = original_endpoint
        print(f"Restored endpoint to: {os.environ['ION_API_ENDPOINT']}")

# Integration test using the actual CLI command
def test_cli_command(setup_test_env):
    # valid test file: tests/valid_trace.txt
        
    # Run the command with error handling
    try:
        result = subprocess.run(
            ["ION-upload", "--user_email", "test@example.com", "--file", "tests/valid_trace.txt"],
            capture_output=True,
            text=True,
            check=False  # Don't raise exception on non-zero exit
        )
        
        # Print the output for debugging
        print(f"Command output: {result.stdout}")
        print(f"Command error: {result.stderr}")
        
        # Check the result
        print("Full result:", result)
        assert result.returncode == 0

        # test the list command
        result = subprocess.run(
            ["ION-upload", "--list"],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Print the output for debugging
        print(f"Command output: {result.stdout}")
        print(f"Command error: {result.stderr}")
        
        # Check the result
        assert result.returncode == 0



    except Exception as e:
        print(f"Test failed with exception: {str(e)}")
        raise 