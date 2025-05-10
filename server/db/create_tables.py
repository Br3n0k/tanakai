"""
Script para criar as tabelas no banco de dados.
Execute-o diretamente para inicializar o banco de dados e criar as tabelas necessárias.
"""

import os
import sys

# Adiciona o diretório raiz ao path do Python se não estiver
if not os.environ.get("TANAKAI"):
    # Define o diretório base do projeto
    os.environ["TANAKAI"] = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(os.environ["TANAKAI"])

# Importa as dependências
from server.db.base import Base, engine
from server.core.config import settings

# Importa todos os modelos para que o SQLAlchemy os reconheça
from server.models.client import Client
# Importe outros modelos aqui se necessário

def create_tables():
    """
    Cria todas as tabelas no banco de dados.
    """
    # Cria as tabelas
    Base.metadata.create_all(bind=engine)
    print(f"Tabelas criadas no banco de dados: {settings.SQLALCHEMY_DATABASE_URI}")

def init_db():
    """
    Inicializa o banco de dados com dados iniciais, se necessário.
    """
    # Aqui você pode adicionar dados iniciais, se necessário
    pass

if __name__ == "__main__":
    print(f"Inicializando banco de dados ({settings.DB_TYPE})...")
    
    # Cria as tabelas
    create_tables()
    
    # Inicializa o banco de dados com dados iniciais
    init_db()
    
    print(f"Banco de dados inicializado com sucesso em: {settings.SQLALCHEMY_DATABASE_URI}")
    if settings.DB_TYPE == "sqlite" and settings.SQLALCHEMY_DATABASE_URI:
        # Extrai apenas o caminho do arquivo a partir da URI
        sqlite_file = settings.SQLALCHEMY_DATABASE_URI.replace("sqlite:///", "")
        print(f"Caminho do arquivo SQLite: {sqlite_file}") 