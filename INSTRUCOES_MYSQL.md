# Instruções para Conectar a Aplicação ao MySQL

## 1. Configuração do Banco de Dados MySQL

Primeiro, execute o script SQL abaixo no seu servidor MySQL para criar as tabelas necessárias:

```sql
-- Cria a tabela de usuários
CREATE TABLE `user` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cria a tabela de composições
CREATE TABLE `composition` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    music_name VARCHAR(100) NOT NULL,
    description TEXT,
    genre VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES `user` (id) ON DELETE CASCADE
);

-- Adiciona índices para melhorar a performance
CREATE INDEX idx_composition_user_id ON `composition` (user_id);
CREATE INDEX idx_user_email ON `user` (email);
CREATE INDEX idx_user_username ON `user` (username);
```

## 2. Pacotes Necessários

Certifique-se de ter os seguintes pacotes instalados:

```
pip install pymysql cryptography
```

## 3. Configuração da Aplicação

### Passo 1: Edite o arquivo `mysql_config.py`

Abra o arquivo `mysql_config.py` e substitua as credenciais com seus dados de acesso MySQL:

```python
MYSQL_USER = "seu_usuario"
MYSQL_PASSWORD = "sua_senha"
MYSQL_HOST = "seu_host_mysql"
MYSQL_PORT = "3306"
MYSQL_DATABASE = "composer_hub"
```

### Passo 2: Modifique o arquivo `app.py`

Edite o arquivo `app.py` da seguinte forma:

```python
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
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database - use MySQL
app.config["SQLALCHEMY_DATABASE_URI"] = MYSQL_DATABASE_URI
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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
```

## 4. Execução da Aplicação

Após realizar as configurações acima, execute a aplicação normalmente:

```
python main.py
```

## Verificação da Conexão

Se você quiser verificar se a conexão com o MySQL está funcionando corretamente, adicione o seguinte código em um arquivo temporário e execute-o:

```python
from app import app, db
from flask import current_app

with app.app_context():
    try:
        # Tenta executar uma query simples
        result = db.session.execute(db.text("SELECT 1"))
        print("Conexão com o banco de dados estabelecida com sucesso!")
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
```

## Migração de Dados (Opcional)

Se você precisar migrar dados de um banco PostgreSQL para o MySQL, você pode usar ferramentas como pgloader ou escrever scripts Python personalizados para essa tarefa.