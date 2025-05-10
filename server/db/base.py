from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from server.core.config import settings

# Verificamos se a URI do banco de dados está configurada
database_uri = settings.SQLALCHEMY_DATABASE_URI or ""

# Em desenvolvimento, habilitamos o echo para ajudar na depuração
if settings.ENV == "development" and settings.DB_TYPE == "sqlite":
    engine = create_engine(database_uri, pool_pre_ping=True, echo=True)
else:
    engine = create_engine(database_uri, pool_pre_ping=True)

# Configuração da sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Gerador para obter uma sessão do banco de dados.
    Garante que a sessão é fechada após o uso.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 