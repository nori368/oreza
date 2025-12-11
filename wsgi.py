"""
WSGI configuration for PythonAnywhere deployment
"""

import sys
import os
from pathlib import Path

# Add your project directory to the sys.path
project_home = '/home/<username>/oreza_chat'  # ← Replace <username> with your PythonAnywhere username
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = Path(project_home) / '.env'
load_dotenv(dotenv_path=env_path)

# Import your FastAPI application
from app import app as application

# PythonAnywhere requires the WSGI application to be named 'application'
# FastAPI app is already ASGI, but we can use it with WSGI adapter

# For ASGI support (recommended for FastAPI)
# You'll need to configure PythonAnywhere to use ASGI instead of WSGI
# Or use an ASGI-to-WSGI adapter like asgiref

try:
    from asgiref.wsgi import WsgiToAsgi
    application = WsgiToAsgi(application)
except ImportError:
    # If asgiref is not available, FastAPI won't work properly with WSGI
    # You'll need to install it: pip install asgiref
    pass
