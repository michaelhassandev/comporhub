import os
import logging
import re

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix
from markupsafe import escape, Markup

# Setup logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Adiciona o filtro nl2br para converter quebras de linha em <br>
@app.template_filter('nl2br')
def nl2br(value):
    if value is None:
        return ''
    
    # Convertemos quebras de linha em <br> para exibição HTML
    text = escape(value)
    result = text.replace('\n', Markup('<br>\n'))
    return result

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 3 * 1024 * 1024  # Limite de 3MB para uploads

# Initialize extensions with app
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'main.login'

with app.app_context():
    # Import here to avoid circular imports
    import models
    import routes
    
    # Register blueprints
    app.register_blueprint(routes.bp)
    
    # Create database tables
    db.create_all()
