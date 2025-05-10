from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Configurações básicas
    PROJECT_NAME: str = "Tanakai API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/v1"
    
    # Ambiente da aplicação
    ENV: str = os.getenv("ENV", "development")
    
    # Configurações de segurança
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 dias
    
    # Tipo de banco de dados (sqlite ou postgres)
    DB_TYPE: str = os.getenv("DB_TYPE", "sqlite")
    
    # Configurações do SQLite (para desenvolvimento)
    SQLITE_FILE: str = os.getenv("SQLITE_FILE", "tanakai.db")
    
    # Configurações do PostgreSQL (para produção)
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "tanakai")
    
    # URI do banco de dados (será definida no init)
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    # Configurações de CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    
    # Configurações de HWID
    HWID_SALT: str = os.getenv("HWID_SALT", "your-hwid-salt-here")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Define a URI do banco de dados com base no tipo escolhido
        if self.DB_TYPE == "sqlite":
            # Obtém o caminho do projeto de forma mais robusta
            # Primeiro tenta usar a variável de ambiente TANAKAI
            tanakai_dir = os.environ.get("TANAKAI")
            
            # Se não estiver definido, usa o diretório do arquivo atual
            if not tanakai_dir:
                # Diretório do arquivo atual (server/core/config.py)
                current_dir = os.path.dirname(os.path.abspath(__file__))
                # Volta dois níveis para chegar na raiz do projeto
                tanakai_dir = os.path.dirname(os.path.dirname(current_dir))
            
            # Define o diretório do banco de dados
            db_dir = os.path.join(tanakai_dir, "database")
            os.makedirs(db_dir, exist_ok=True)
            
            # Define o caminho do arquivo SQLite
            sqlite_path = os.path.join(db_dir, self.SQLITE_FILE)
            self.SQLALCHEMY_DATABASE_URI = f"sqlite:///{sqlite_path}"
        else:
            self.SQLALCHEMY_DATABASE_URI = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
            )

settings = Settings() 