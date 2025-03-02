"""Configuration settings for the ION-upload package."""

import os

# Default API endpoint
DEFAULT_API_ENDPOINT = os.environ.get("ION_API_ENDPOINT", "http://127.0.0.1:5000/api")

MODELS_LIST = SUPPORTED_MODELS = [
    "openai/gpt-4o",
    "openai/gpt-4o-mini",
    "anthropic/claude-3-5-sonnet-20240620",
    "anthropic/claude-3-7-sonnet-20250219"
]

VALID_TASK_STATUSES = ["completed", "failed", "not_started"]

VALID_STATUS_FOR_VIEW = ["completed"]