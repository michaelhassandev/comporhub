"""
Script para exportar dados do PostgreSQL para um formato compatível com MySQL

Este script vai:
1. Conectar ao banco de dados PostgreSQL
2. Exportar os dados das tabelas para arquivos CSV
3. Gerar os comandos SQL para importar os dados no MySQL
"""

import os
import csv
from app import app, db
from models import User, Composition
import sqlalchemy as sa

# Diretório para salvar os arquivos exportados
EXPORT_DIR = 'dados_exportados'

def criar_diretorio():
    """Cria o diretório para armazenar os arquivos exportados"""
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)
        print(f"Diretório '{EXPORT_DIR}' criado.")

def exportar_usuarios():
    """Exporta os dados da tabela user para CSV"""
    file_path = os.path.join(EXPORT_DIR, 'usuarios.csv')
    
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Cabeçalho
        writer.writerow(['id', 'username', 'email', 'password_hash', 'created_at'])
        
        # Dados
        usuarios = db.session.execute(sa.select(User)).scalars().all()
        for usuario in usuarios:
            writer.writerow([
                usuario.id,
                usuario.username,
                usuario.email,
                usuario.password_hash,
                usuario.created_at.strftime('%Y-%m-%d %H:%M:%S') if usuario.created_at else None
            ])
    
    print(f"Dados de usuários exportados para {file_path}")
    return len(usuarios)

def exportar_composicoes():
    """Exporta os dados da tabela composition para CSV"""
    file_path = os.path.join(EXPORT_DIR, 'composicoes.csv')
    
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Cabeçalho
        writer.writerow(['id', 'title', 'music_name', 'description', 'genre', 'created_at', 'updated_at', 'user_id'])
        
        # Dados
        composicoes = db.session.execute(sa.select(Composition)).scalars().all()
        for comp in composicoes:
            writer.writerow([
                comp.id,
                comp.title,
                comp.music_name,
                comp.description,
                comp.genre,
                comp.created_at.strftime('%Y-%m-%d %H:%M:%S') if comp.created_at else None,
                comp.updated_at.strftime('%Y-%m-%d %H:%M:%S') if comp.updated_at else None,
                comp.user_id
            ])
    
    print(f"Dados de composições exportados para {file_path}")
    return len(composicoes)

def gerar_sql_importacao():
    """Gera comandos SQL para importar os dados no MySQL"""
    sql_file = os.path.join(EXPORT_DIR, 'importar_dados.sql')
    
    with open(sql_file, 'w', encoding='utf-8') as f:
        f.write("-- Script para importar dados no MySQL\n\n")
        
        # Desativa verificações de chaves estrangeiras
        f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")
        
        # Importação de usuários
        f.write("-- Importação de dados de usuários\n")
        f.write("LOAD DATA INFILE './usuarios.csv'\n")
        f.write("INTO TABLE `user`\n")
        f.write("FIELDS TERMINATED BY ','\n")
        f.write("ENCLOSED BY '\"'\n")
        f.write("LINES TERMINATED BY '\\n'\n")
        f.write("IGNORE 1 LINES\n")
        f.write("(id, username, email, password_hash, created_at);\n\n")
        
        # Importação de composições
        f.write("-- Importação de dados de composições\n")
        f.write("LOAD DATA INFILE './composicoes.csv'\n")
        f.write("INTO TABLE `composition`\n")
        f.write("FIELDS TERMINATED BY ','\n")
        f.write("ENCLOSED BY '\"'\n")
        f.write("LINES TERMINATED BY '\\n'\n")
        f.write("IGNORE 1 LINES\n")
        f.write("(id, title, music_name, description, genre, created_at, updated_at, user_id);\n\n")
        
        # Reativa verificações de chaves estrangeiras
        f.write("SET FOREIGN_KEY_CHECKS = 1;\n")
    
    print(f"Script SQL de importação gerado em {sql_file}")

def main():
    with app.app_context():
        print("Iniciando exportação de dados...")
        criar_diretorio()
        
        num_usuarios = exportar_usuarios()
        num_composicoes = exportar_composicoes()
        
        gerar_sql_importacao()
        
        print("\nExportação concluída com sucesso!")
        print(f"Total: {num_usuarios} usuários e {num_composicoes} composições exportados.")
        print(f"\nOs arquivos foram salvos no diretório: {os.path.abspath(EXPORT_DIR)}")
        print("\nPara importar os dados no MySQL:")
        print("1. Crie as tabelas usando o script SQL fornecido")
        print("2. Copie os arquivos CSV para o servidor MySQL")
        print("3. Execute o script 'importar_dados.sql' no MySQL")

if __name__ == "__main__":
    main()