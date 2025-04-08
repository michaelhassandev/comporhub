"""Configuração para conexão com MySQL

Para utilizar este arquivo:
1. Preencha os valores das variáveis abaixo
2. Importe este arquivo no app.py
3. Substitua a string de conexão DATABASE_URL pela variável MYSQL_DATABASE_URI
"""

import urllib.parse

# Configurações do MySQL - PREENCHA ESSAS INFORMAÇÕES
MYSQL_USER = "u611629858_foodapp"
MYSQL_PASSWORD = "Asd080782@"
MYSQL_HOST = "193.203.175.174"  # Endereço do servidor MySQL remoto
MYSQL_PORT = "3306"  # porta padrão do MySQL
MYSQL_DATABASE = "u611629858_foodapp"  # nome do banco de dados

# String de conexão formatada para MySQL
MYSQL_DATABASE_URI = f"mysql+pymysql://{urllib.parse.quote_plus(MYSQL_USER)}:{urllib.parse.quote_plus(MYSQL_PASSWORD)}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"