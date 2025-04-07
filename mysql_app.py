"""
Versão do app.py configurada para usar MySQL

Para usar este arquivo:
1. Renomeie-o para app.py ou substitua o conteúdo do seu app.py atual
2. Configure corretamente o arquivo mysql_config.py
3. Execute python main.py para iniciar a aplicação
"""

import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix
import pymysql

# Importando a configuração MySQL
from mysql_config import MYSQL_DATABASE_URI

# Registrando o PyMySQL como driver para MySQL
pymysql.install_as_MySQLdb()

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

# Configure database - use MySQL
app.config["SQLALCHEMY_DATABASE_URI"] = MYSQL_DATABASE_URI
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Log de conexão
logging.info(f"Conectando ao banco de dados: {MYSQL_DATABASE_URI.replace('://', '://***:***@')}")

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