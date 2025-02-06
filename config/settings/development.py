"""Setting file for development, stored all development specific settings"""

from .base import *
import os

# Database settings for development
DATABASES = {
    "default": {
        "ENGINE": f"django.db.backends.{os.environ.get('DB_ENGINE', 'postgresql')}",
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "postgres"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", 5432),
    }
}
openai_api_key = os.environ.get("OPENAI_API_KEY")
