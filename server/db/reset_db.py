"""
Script para resetar o banco de dados SQLite.
Use com cuidado - esse script apaga o banco de dados atual e cria um novo vazio.
"""

import os
import sys
import shutil

# Adiciona o diretório raiz ao path do Python se não estiver
if not os.environ.get("TANAKAI"):
    # Define o diretório base do projeto
    os.environ["TANAKAI"] = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(os.environ["TANAKAI"])

from server.core.config import settings
from server.db.create_tables import create_tables, init_db

def reset_sqlite_db():
    """
    Apaga e recria o banco de dados SQLite.
    """
    if settings.DB_TYPE != "sqlite" or not settings.SQLALCHEMY_DATABASE_URI:
        print("Essa função só pode ser usada com SQLite!")
        return False
    
    # Extrai o caminho do arquivo do banco de dados
    db_path = settings.SQLALCHEMY_DATABASE_URI.replace("sqlite:///", "")
    
    # Verifica se o arquivo existe
    if os.path.exists(db_path):
        # Faz backup antes de apagar
        backup_path = f"{db_path}.bak"
        try:
            shutil.copy2(db_path, backup_path)
            print(f"Backup criado em: {backup_path}")
        except Exception as e:
            print(f"Erro ao criar backup: {str(e)}")
        
        # Apaga o arquivo
        try:
            os.remove(db_path)
            print(f"Banco de dados apagado: {db_path}")
        except Exception as e:
            print(f"Erro ao apagar banco de dados: {str(e)}")
            return False
    
    # Recria o banco de dados
    try:
        print("Recriando o banco de dados...")
        create_tables()
        init_db()
        print("Banco de dados reinicializado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao recriar o banco de dados: {str(e)}")
        return False

if __name__ == "__main__":
    # Verifica se o usuário realmente quer resetar o banco de dados
    confirm = input("ATENÇÃO: Isso vai apagar o banco de dados atual. Continuar? (s/N): ")
    
    if confirm.lower() == "s":
        reset_sqlite_db()
    else:
        print("Operação cancelada.") 