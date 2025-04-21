"""Configuration settings for the ION-upload package."""

import os

# Default API endpoint
DEFAULT_API_ENDPOINT = os.environ.get("ION_API_ENDPOINT", "http://ec2-3-138-157-186.us-east-2.compute.amazonaws.com")

MODELS_LIST = SUPPORTED_MODELS = [
    "openai/gpt-4o",
    "openai/gpt-4o-mini",
    "openai/gpt-4.1",
    "openai/gpt-4.1-mini",
    "anthropic/claude-3-5-sonnet-20240620",
    "anthropic/claude-3-7-sonnet-20250219"
]

VALID_TASK_STATUSES = ["completed", "failed", "not_started"]

VALID_STATUS_FOR_VIEW = ["completed"]