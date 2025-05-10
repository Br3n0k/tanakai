from typing import List, Union, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query

import os

# Verifica se a variável de ambiente existe, caso contrário define o diretório atual
if "TANAKAI_SERVER" not in os.environ:
    os.environ["TANAKAI_SERVER"] = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from server.utils.read_harvestables import read_harvestables
from server.schemas.harvestables import Harvestable

router = APIRouter()

@router.get("/", response_model=List[Harvestable])
def get_harvestables(
    tier: int = Query(None, description="Filtrar por tier"),
    resource_type: str = Query(None, description="Filtrar por tipo de recurso (Madeira, Minério, etc)"),
    location: str = Query(None, description="Filtrar por localização")
):
    """
    Retorna a lista de todos os recursos coletáveis disponíveis.
    Opcionalmente pode filtrar por tier, tipo de recurso ou localização.
    """
    result = read_harvestables()
    
    # Verifica se retornou uma mensagem de erro
    if isinstance(result, dict) and "message" in result:
        raise HTTPException(status_code=404, detail=result["message"])
    
    # Aplica filtros se especificados
    filtered_harvestables = result
    
    if tier is not None:
        filtered_harvestables = [h for h in filtered_harvestables if h.tier == tier]
        
    if resource_type:
        filtered_harvestables = [h for h in filtered_harvestables if h.resource_type and h.resource_type.lower() == resource_type.lower()]
        
    if location:
        filtered_harvestables = [h for h in filtered_harvestables if h.location and h.location.lower() == location.lower()]
    
    return filtered_harvestables

@router.get("/{harvestable_id}", response_model=Harvestable)
def get_harvestable(harvestable_id: int):
    """
    Retorna um recurso coletável específico pelo ID.
    """
    result = read_harvestables()
    
    # Verifica se retornou uma mensagem de erro
    if isinstance(result, dict) and "message" in result:
        raise HTTPException(status_code=404, detail=result["message"])
    
    # Busca o recurso coletável pelo ID
    try:
        found_harvestable = next((h for h in result if getattr(h, 'id', None) == harvestable_id), None)
        if found_harvestable:
            return found_harvestable
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar recursos coletáveis: {str(e)}")
    
    raise HTTPException(status_code=404, detail=f"Recurso coletável com ID {harvestable_id} não encontrado") 