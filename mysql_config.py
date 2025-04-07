"""
Configuração para conexão com MySQL

Para utilizar este arquivo:
1. Preencha os valores das variáveis abaixo
2. Importe este arquivo no app.py
3. Substitua a string de conexão DATABASE_URL pela variável MYSQL_DATABASE_URI
"""

# Configurações do MySQL - PREENCHA ESSAS INFORMAÇÕES
MYSQL_USER = "seu_usuario"
MYSQL_PASSWORD = "sua_senha"
MYSQL_HOST = "seu_host_mysql" # geralmente "localhost" para ambientes locais
MYSQL_PORT = "3306"  # porta padrão do MySQL
MYSQL_DATABASE = "composer_hub"  # nome do banco de dados

# String de conexão formatada para MySQL
MYSQL_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"