import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Add the current directory to Python path
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.append(project_home)
    logging.info(f"Added {project_home} to Python path")

# Import your Flask app
from app import app as application

# Production settings
application.config['DEBUG'] = False
application.config['TESTING'] = False

# Security settings
application.config['SESSION_COOKIE_SECURE'] = True
application.config['SESSION_COOKIE_HTTPONLY'] = True
application.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
application.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

# Security headers
@application.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response