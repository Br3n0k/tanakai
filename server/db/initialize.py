"""
Script para verificar e inicializar o banco de dados automaticamente.
Este script é executado durante a inicialização da aplicação para garantir que o banco de dados 
esteja pronto antes de iniciar o servidor.
"""

import os
import sys
import logging
from sqlalchemy.exc import OperationalError
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import text

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db_initializer")

# Importa módulos necessários
from server.core.config import settings
from server.db.base import engine, Base
from server.db.create_tables import create_tables, init_db

def ensure_database_exists():
    """
    Garante que o banco de dados existe e está acessível.
    - Para SQLite: cria o arquivo e o diretório se não existirem
    - Para PostgreSQL: verifica a conexão e cria o banco se não existir
    
    Returns:
        bool: True se o banco de dados está pronto, False caso contrário
    """
    try:
        if settings.DB_TYPE == "sqlite":
            return ensure_sqlite_database()
        else:
            return ensure_postgres_database()
    except Exception as e:
        logger.error(f"Erro ao verificar banco de dados: {str(e)}")
        return False

def ensure_sqlite_database():
    """
    Garante que o arquivo SQLite e seu diretório existem.
    
    Returns:
        bool: True se o banco de dados está pronto, False caso contrário
    """
    if not settings.SQLALCHEMY_DATABASE_URI:
        logger.error("URI do banco de dados SQLite não definida")
        return False
    
    # Extrai o caminho do arquivo do banco de dados
    db_path = settings.SQLALCHEMY_DATABASE_URI.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    
    # Garante que o diretório existe
    try:
        if not os.path.exists(db_dir):
            logger.info(f"Criando diretório para o banco de dados: {db_dir}")
            os.makedirs(db_dir, exist_ok=True)
    except Exception as e:
        logger.error(f"Erro ao criar diretório do banco de dados: {str(e)}")
        return False
    
    # Verifica se o arquivo do banco de dados existe
    if not os.path.exists(db_path):
        logger.info(f"Banco de dados SQLite não encontrado. Criando em: {db_path}")
        try:
            # A criação das tabelas vai gerar o arquivo
            create_tables()
            init_db()
            logger.info(f"Banco de dados SQLite inicializado com sucesso em: {db_path}")
        except Exception as e:
            logger.error(f"Erro ao criar banco de dados SQLite: {str(e)}")
            return False
    else:
        # Verifica se o banco está acessível
        try:
            # Tenta executar uma consulta simples
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"Banco de dados SQLite verificado com sucesso: {db_path}")
        except Exception as e:
            logger.error(f"Erro ao conectar ao banco de dados SQLite: {str(e)}")
            return False
    
    return True

def ensure_postgres_database():
    """
    Garante que o banco de dados PostgreSQL existe e está acessível.
    Se não existir, tenta criá-lo.
    
    Returns:
        bool: True se o banco de dados está pronto, False caso contrário
    """
    if not settings.SQLALCHEMY_DATABASE_URI:
        logger.error("URI do banco de dados PostgreSQL não definida")
        return False
    
    # Verifica se o banco de dados existe
    try:
        # Tenta conectar diretamente ao banco
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # Se chegou até aqui, o banco já existe e está acessível
        logger.info(f"Banco de dados PostgreSQL verificado com sucesso: {settings.POSTGRES_DB}")
        
        # Verifica se as tabelas existem
        from sqlalchemy import inspect
        inspector = inspect(engine)
        if not inspector.get_table_names():
            logger.info("Banco de dados existe mas não tem tabelas. Criando tabelas...")
            create_tables()
            init_db()
        
        return True
    except OperationalError:
        # Banco não existe ou não está acessível, tenta criar
        logger.warning(f"Banco de dados PostgreSQL não acessível: {settings.POSTGRES_DB}")
        
        try:
            # Conecta ao servidor PostgreSQL sem especificar um banco de dados
            conn_string = f"host={settings.POSTGRES_SERVER} user={settings.POSTGRES_USER} password={settings.POSTGRES_PASSWORD}"
            conn = psycopg2.connect(conn_string)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            # Verifica se o banco de dados existe
            cursor = conn.cursor()
            cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{settings.POSTGRES_DB}'")
            exists = cursor.fetchone()
            
            if not exists:
                # Banco não existe, criar
                logger.info(f"Criando banco de dados PostgreSQL: {settings.POSTGRES_DB}")
                cursor.execute(f"CREATE DATABASE {settings.POSTGRES_DB}")
                cursor.close()
                conn.close()
                
                # Agora tenta criar as tabelas
                create_tables()
                init_db()
                
                logger.info(f"Banco de dados PostgreSQL criado com sucesso: {settings.POSTGRES_DB}")
                return True
            else:
                # Banco existe mas não está acessível (problema de permissão?)
                logger.error(f"O banco de dados PostgreSQL existe, mas não está acessível: {settings.POSTGRES_DB}")
                return False
            
        except Exception as e:
            logger.error(f"Erro ao criar banco de dados PostgreSQL: {str(e)}")
            return False

def check_and_initialize_database():
    """
    Função principal para verificar e inicializar o banco de dados.
    Esta função é chamada durante a inicialização da aplicação.
    
    Returns:
        bool: True se o banco de dados está pronto, False caso contrário
    """
    logger.info(f"Verificando banco de dados ({settings.DB_TYPE})...")
    
    if ensure_database_exists():
        logger.info(f"Banco de dados verificado e pronto para uso: {settings.SQLALCHEMY_DATABASE_URI}")
        return True
    else:
        logger.error(f"Não foi possível inicializar o banco de dados: {settings.SQLALCHEMY_DATABASE_URI}")
        return False

# Para testes manuais
if __name__ == "__main__":
    # Define o diretório base do projeto se não estiver definido
    if not os.environ.get("TANAKAI"):
        os.environ["TANAKAI"] = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.append(os.environ["TANAKAI"])
    
    # Testa a inicialização do banco de dados
    if check_and_initialize_database():
        print("Banco de dados inicializado com sucesso!")
    else:
        print("Erro ao inicializar o banco de dados!") 