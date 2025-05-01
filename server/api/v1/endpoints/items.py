from typing import List, Union, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query

import os

# Verifica se a variável de ambiente existe, caso contrário define o diretório atual
if "TANAKAI_SERVER" not in os.environ:
    os.environ["TANAKAI_SERVER"] = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from server.utils.read_items import read_items
from server.schemas.items import Item

router = APIRouter()

@router.get("/", response_model=List[Item])
def get_items(
    tier: int = Query(None, description="Filtrar por tier"),
    item_type: str = Query(None, description="Filtrar por tipo de item (Arma, Armadura, Recurso, etc)"),
    name: str = Query(None, description="Pesquisar por nome")
):
    """
    Retorna a lista de todos os itens disponíveis.
    Opcionalmente pode filtrar por tier, tipo ou nome.
    """
    result = read_items()
    
    # Verifica se retornou uma mensagem de erro
    if isinstance(result, dict) and "message" in result:
        raise HTTPException(status_code=404, detail=result["message"])
    
    # Aplica filtros se especificados
    filtered_items = result
    
    if tier is not None:
        filtered_items = [item for item in filtered_items if item.tier == tier]
        
    if item_type:
        filtered_items = [item for item in filtered_items if item.item_type and item.item_type.lower() == item_type.lower()]
        
    if name:
        filtered_items = [item for item in filtered_items if name.lower() in item.name.lower()]
    
    return filtered_items

@router.get("/{item_id}", response_model=Item)
def get_item(item_id: int):
    """
    Retorna um item específico pelo ID.
    """
    result = read_items()
    
    # Verifica se retornou uma mensagem de erro
    if isinstance(result, dict) and "message" in result:
        raise HTTPException(status_code=404, detail=result["message"])
    
    # Busca o item pelo ID
    try:
        found_item = next((item for item in result if getattr(item, 'id', None) == item_id), None)
        if found_item:
            return found_item
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar itens: {str(e)}")
    
    raise HTTPException(status_code=404, detail=f"Item com ID {item_id} não encontrado")
