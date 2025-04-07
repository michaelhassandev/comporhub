"""
Script para testar a conexão com o banco de dados MySQL

Antes de executar este script:
1. Configure corretamente o arquivo mysql_config.py
2. Certifique-se de que o banco de dados MySQL está acessível
"""

import logging
import pymysql
import os
import sys

# Configuração de logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Tenta importar a configuração MySQL
try:
    from mysql_config import MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE
    logging.info(f"Configuração MySQL carregada para {MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}")
except ImportError:
    logging.error("Arquivo mysql_config.py não encontrado ou mal formatado.")
    sys.exit(1)

def testar_conexao_mysql():
    """Testa a conexão com o banco de dados MySQL"""
    try:
        # Tenta estabelecer uma conexão com o MySQL
        conn = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            port=int(MYSQL_PORT),
            database=MYSQL_DATABASE,
            connect_timeout=5
        )
        
        logging.info("Conexão com MySQL estabelecida com sucesso!")
        
        # Verifica se as tabelas existem
        with conn.cursor() as cursor:
            # Verifica as tabelas existentes
            cursor.execute("SHOW TABLES")
            tabelas = cursor.fetchall()
            
            if tabelas:
                logging.info(f"Tabelas encontradas no banco de dados: {[t[0] for t in tabelas]}")
                
                # Verifica a estrutura da tabela user
                if ('user',) in tabelas:
                    cursor.execute("DESCRIBE `user`")
                    colunas_user = cursor.fetchall()
                    logging.info(f"Estrutura da tabela 'user': {colunas_user}")
                
                # Verifica a estrutura da tabela composition
                if ('composition',) in tabelas:
                    cursor.execute("DESCRIBE `composition`")
                    colunas_composition = cursor.fetchall()
                    logging.info(f"Estrutura da tabela 'composition': {colunas_composition}")
            else:
                logging.warning("Não foram encontradas tabelas no banco de dados.")
                logging.info("Você precisa criar as tabelas usando o script SQL fornecido.")
        
        # Fecha a conexão
        conn.close()
        return True
        
    except Exception as e:
        logging.error(f"Erro ao conectar ao MySQL: {e}")
        return False

if __name__ == "__main__":
    print("===============================")
    print("Teste de Conexão com MySQL")
    print("===============================")
    
    resultado = testar_conexao_mysql()
    
    if resultado:
        print("\n✅ A conexão com o MySQL foi estabelecida com sucesso!")
        print("O banco de dados está configurado corretamente.")
    else:
        print("\n❌ Falha ao conectar ao MySQL.")
        print("Verifique as informações em mysql_config.py e certifique-se de que:")
        print("1. O servidor MySQL está em execução")
        print("2. As credenciais estão corretas")
        print("3. O banco de dados existe")
        print("4. O MySQL aceita conexões do IP da sua máquina")