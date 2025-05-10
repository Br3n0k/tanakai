"""
Endpoints para gerenciamento de clientes.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from server.db.base import get_db
from server.schemas.client import Client as ClientSchema, ClientCreate, ClientUpdate
from server.services import client as client_service
from server.api.v1.client.new_os import get_identifier

router = APIRouter()

@router.get("/", response_model=List[ClientSchema])
def read_clients(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Retorna uma lista de clientes.
    """
    return client_service.get_clients(db, skip=skip, limit=limit)

@router.post("/", response_model=ClientSchema)
def create_new_client(
    client: ClientCreate, 
    db: Session = Depends(get_db)
):
    """
    Cria um novo cliente.
    """
    db_client = client_service.get_client_by_hwid(db, client.hwid)
    if db_client:
        raise HTTPException(
            status_code=400,
            detail="Cliente com este HWID já existe"
        )
    return client_service.create_client(db, client)

@router.post("/register", response_model=ClientSchema)
def register_client(
    data: Dict[str, str], 
    db: Session = Depends(get_db)
):
    """
    Registra o sistema atual como um cliente.
    """
    name = data.get("name", "Unnamed Client")
    return client_service.register_system(db, name)

@router.get("/current", response_model=ClientSchema)
def get_current_client(
    db: Session = Depends(get_db)
):
    """
    Retorna informações sobre o cliente atual com base no HWID do sistema.
    """
    hwid = get_identifier()
    db_client = client_service.get_client_by_hwid(db, hwid)
    if not db_client:
        raise HTTPException(
            status_code=404,
            detail="Cliente não registrado"
        )
    return db_client

@router.post("/verify", response_model=Dict[str, Any])
def verify_client(
    db: Session = Depends(get_db)
):
    """
    Verifica se o cliente atual está registrado e válido.
    """
    hwid = get_identifier()
    db_client = client_service.get_client_by_hwid(db, hwid)
    
    if not db_client:
        return {
            "registered": False,
            "active": False,
            "banned": False,
            "message": "Cliente não registrado"
        }
    
    if not db_client.is_active:
        return {
            "registered": True,
            "active": False,
            "banned": db_client.is_banned,
            "message": "Conta desativada"
        }
    
    if db_client.is_banned:
        return {
            "registered": True,
            "active": True,
            "banned": True,
            "message": f"Conta banida: {db_client.ban_reason or 'Motivo não especificado'}"
        }
    
    return {
        "registered": True,
        "active": True,
        "banned": False,
        "message": "Cliente válido",
        "client_id": db_client.id,
        "name": db_client.name
    }

@router.get("/{client_id}", response_model=ClientSchema)
def read_client(
    client_id: int, 
    db: Session = Depends(get_db)
):
    """
    Retorna um cliente específico pelo ID.
    """
    db_client = client_service.get_client(db, client_id)
    if not db_client:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado"
        )
    return db_client

@router.put("/{client_id}", response_model=ClientSchema)
def update_client_endpoint(
    client_id: int, 
    client: ClientUpdate, 
    db: Session = Depends(get_db)
):
    """
    Atualiza um cliente existente.
    """
    db_client = client_service.update_client(db, client_id, client)
    if not db_client:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado"
        )
    return db_client

@router.delete("/{client_id}", response_model=Dict[str, bool])
def delete_client_endpoint(
    client_id: int, 
    db: Session = Depends(get_db)
):
    """
    Exclui um cliente.
    """
    success = client_service.delete_client(db, client_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado"
        )
    return {"success": True}

@router.post("/{client_id}/ban", response_model=ClientSchema)
def ban_client_endpoint(
    client_id: int, 
    data: Dict[str, str], 
    db: Session = Depends(get_db)
):
    """
    Bane um cliente.
    """
    reason = data.get("reason", "Motivo não especificado")
    db_client = client_service.ban_client(db, client_id, reason)
    if not db_client:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado"
        )
    return db_client

@router.post("/{client_id}/unban", response_model=ClientSchema)
def unban_client_endpoint(
    client_id: int, 
    db: Session = Depends(get_db)
):
    """
    Remove o banimento de um cliente.
    """
    db_client = client_service.unban_client(db, client_id)
    if not db_client:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado"
        )
    return db_client 