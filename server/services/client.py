from typing import List, Optional
from sqlalchemy.orm import Session
from server.models.client import Client
from server.schemas.client import ClientCreate, ClientUpdate

def get_client(db: Session, id: int) -> Optional[Client]:
    return db.query(Client).filter(Client.id == id).first()

def get_client_by_hwid(db: Session, hwid: str) -> Optional[Client]:
    return db.query(Client).filter(Client.hwid == hwid).first()

def get_clients(
    db: Session, skip: int = 0, limit: int = 100
) -> List[Client]:
    return db.query(Client).offset(skip).limit(limit).all()

def create_client(db: Session, obj_in: ClientCreate) -> Client:
    db_obj = Client(
        hwid=obj_in.hwid,
        name=obj_in.name,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_client(
    db: Session, *, db_obj: Client, obj_in: ClientUpdate
) -> Client:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_client(db: Session, *, id: int) -> Client:
    obj = db.query(Client).get(id)
    db.delete(obj)
    db.commit()
    return obj 