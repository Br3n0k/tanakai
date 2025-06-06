from typing import Generator
from server.db.base import SessionLocal

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close() 