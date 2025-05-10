"""
Serviço para operações CRUD com clientes.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from server.models.client import Client
from server.schemas.client import ClientCreate, ClientUpdate
from server.api.v1.client.new_os import get_identifier
from datetime import datetime

def get_client(db: Session, client_id: int) -> Optional[Client]:
    """
    Obtém um cliente pelo ID.
    """
    return db.query(Client).filter(Client.id == client_id).first()

def get_client_by_hwid(db: Session, hwid: str) -> Optional[Client]:
    """
    Obtém um cliente pelo HWID.
    """
    return db.query(Client).filter(Client.hwid == hwid).first()

def get_clients(db: Session, skip: int = 0, limit: int = 100) -> List[Client]:
    """
    Obtém todos os clientes, com paginação.
    """
    return db.query(Client).offset(skip).limit(limit).all()

def create_client(db: Session, client: ClientCreate) -> Client:
    """
    Cria um novo cliente.
    """
    db_client = Client(
        hwid=client.hwid,
        name=client.name,
        is_active=True,
        is_banned=False
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def update_client(db: Session, client_id: int, client: ClientUpdate) -> Optional[Client]:
    """
    Atualiza um cliente existente.
    """
    db_client = get_client(db, client_id)
    if not db_client:
        return None
    
    # Atualiza apenas os campos que foram fornecidos
    update_data = client.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_client, key, value)
    
    # Atualiza a data de atualização
    db_client.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_client)
    return db_client

def delete_client(db: Session, client_id: int) -> bool:
    """
    Exclui um cliente.
    """
    db_client = get_client(db, client_id)
    if not db_client:
        return False
    
    db.delete(db_client)
    db.commit()
    return True

def register_system(db: Session, name: str) -> Client:
    """
    Registra o sistema atual como um cliente.
    """
    # Obtém o identificador único do sistema
    hwid = get_identifier()
    
    # Verifica se o cliente já existe
    db_client = get_client_by_hwid(db, hwid)
    
    # Se o cliente já existe, atualiza o nome
    if db_client:
        db_client.name = name
        db_client.updated_at = datetime.now()
        db.commit()
        db.refresh(db_client)
        return db_client
    
    # Se o cliente não existe, cria um novo
    client_create = ClientCreate(hwid=hwid, name=name)
    return create_client(db, client_create)

def is_banned(db: Session, hwid: str) -> bool:
    """
    Verifica se um cliente está banido.
    """
    db_client = get_client_by_hwid(db, hwid)
    if not db_client:
        return False
    
    return db_client.is_banned

def ban_client(db: Session, client_id: int, reason: str) -> Optional[Client]:
    """
    Bane um cliente.
    """
    db_client = get_client(db, client_id)
    if not db_client:
        return None
    
    db_client.is_banned = True
    db_client.ban_reason = reason
    db_client.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_client)
    return db_client

def unban_client(db: Session, client_id: int) -> Optional[Client]:
    """
    Remove o banimento de um cliente.
    """
    db_client = get_client(db, client_id)
    if not db_client:
        return None
    
    db_client.is_banned = False
    db_client.ban_reason = None
    db_client.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_client)
    return db_client 