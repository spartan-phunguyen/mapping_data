"""
Configuration file for the Meal Mapping application
Contains all constants, settings, and configuration options
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# S3 Configuration
S3_BUCKET_NAME = "service-dietfit-20250526115059333100000001"
S3_PREFIX = "meal-images/"
AWS_REGION = os.getenv("AWS_REGION")

# Langfuse Configuration
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST")

# Time filter options
TIME_FILTER_OPTIONS = {
    "1": {"name": "Past 1 day", "days": 1},
    "2": {"name": "Past 7 days", "days": 7}, 
    "3": {"name": "Past 14 days", "days": 14},
    "4": {"name": "Past 1 month", "days": 30}
}

# Display settings
MAX_DISPLAY_ITEMS = 5  # Maximum items to show in detailed view
TABLE_WIDTH = 80
USER_ID_DISPLAY_WIDTH = 39 