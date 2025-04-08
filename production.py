"""Production configuration for the Flask application

This file contains settings and configurations specific to the production environment.
It uses Waitress as the WSGI server and includes security-related configurations.
"""

import os
import sys
import logging
from waitress import serve
from waitress.adjustments import Adjustments
from app import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Production-specific settings
app.config['DEBUG'] = False
app.config['TESTING'] = False

# Security settings
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour in seconds

# File upload settings
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024  # 3MB limit for file uploads

def run_production_server():
    # Ensure a strong secret key in production
    if 'SESSION_SECRET' not in os.environ:
        print("WARNING: SESSION_SECRET not set in environment. Using a random key.")
        app.secret_key = os.urandom(24)
    
    # Security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    # Configure Waitress server
    try:
        port = int(os.environ.get('PORT', 8080))
        logging.info(f"Starting production server on port {port}...")
        
        # Configure Waitress with proper error handling
        serve(
            app,
            host='0.0.0.0',
            port=port,
            threads=int(os.environ.get('WAITRESS_THREADS', 4)),
            url_scheme='https',
            channel_timeout=300,
            cleanup_interval=30,
            connection_limit=1000,
            log_socket_errors=True,
            max_request_header_size=262144,
            max_request_body_size=1073741824,
            retry_startup=True
        )
    except Exception as e:
        logging.error(f"Failed to start production server: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    run_production_server()