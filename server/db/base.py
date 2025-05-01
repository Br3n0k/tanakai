from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from server.core.config import settings

# Corrigindo o erro de tipo adicionando verificação para garantir que a URL não seja None
database_uri = settings.SQLALCHEMY_DATABASE_URI or ""
engine = create_engine(database_uri, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 