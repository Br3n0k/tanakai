from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from server.api import deps
from server.schemas.client import Client, ClientCreate, ClientUpdate
from server.services import client as client_service

router = APIRouter()

@router.get("/", response_model=List[Client])
def read_clients(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retorna lista de clientes.
    """
    clients = client_service.get_clients(db, skip=skip, limit=limit)
    return clients

@router.post("/", response_model=Client)
def create_client(
    *,
    db: Session = Depends(deps.get_db),
    client_in: ClientCreate,
):
    """
    Cria novo cliente.
    """
    client = client_service.get_client_by_hwid(db, hwid=client_in.hwid)
    if client:
        raise HTTPException(
            status_code=400,
            detail="Cliente com este HWID já existe.",
        )
    client = client_service.create_client(db, obj_in=client_in)
    return client

@router.get("/{client_id}", response_model=Client)
def read_client(
    *,
    db: Session = Depends(deps.get_db),
    client_id: int,
):
    """
    Retorna cliente por ID.
    """
    client = client_service.get_client(db, id=client_id)
    if not client:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado",
        )
    return client

@router.put("/{client_id}", response_model=Client)
def update_client(
    *,
    db: Session = Depends(deps.get_db),
    client_id: int,
    client_in: ClientUpdate,
):
    """
    Atualiza cliente.
    """
    client = client_service.get_client(db, id=client_id)
    if not client:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado",
        )
    client = client_service.update_client(db, db_obj=client, obj_in=client_in)
    return client

@router.delete("/{client_id}", response_model=Client)
def delete_client(
    *,
    db: Session = Depends(deps.get_db),
    client_id: int,
):
    """
    Remove cliente.
    """
    client = client_service.get_client(db, id=client_id)
    if not client:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado",
        )
    client = client_service.delete_client(db, id=client_id)
    return client 