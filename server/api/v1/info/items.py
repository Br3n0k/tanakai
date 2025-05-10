from typing import List, Union, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from server.utils.read_items import read_items
from server.schemas.items import Item, Weapon, Armor, Consumable, Resource, Mount, Furniture, ItemBase, Accessory, Other

router = APIRouter()

@router.get("/", response_model=List[Item])
def get_items(
    tier: Optional[int] = Query(None, description="Filtrar por tier"),
    item_type: Optional[str] = Query(None, description="Filtrar por tipo de item (Arma, Armadura, Recurso, etc)"),
    name: Optional[str] = Query(None, description="Pesquisar por nome"),
    uniquename: Optional[str] = Query(None, description="Pesquisar pelo nome único exato"),
    limit: int = Query(1000, description="Número máximo de itens a retornar (0 para todos)")
):
    """
    Retorna a lista de itens disponíveis.
    Opcionalmente pode filtrar por tier, tipo, nome ou uniquename.
    """
    result = read_items()
    
    # Verifica se retornou uma mensagem de erro
    if isinstance(result, dict) and "message" in result:
        raise HTTPException(status_code=404, detail=result["message"])
    
    # Aplica filtros se especificados
    filtered_items = result
    
    if tier is not None:
        filtered_items = [item for item in filtered_items if getattr(getattr(item, 'item', None), 'tier', None) == tier]
        
    if item_type:
        filtered_items = [item for item in filtered_items 
                        if getattr(getattr(item, 'item', None), 'item_type', None) 
                        and getattr(getattr(item, 'item', None), 'item_type', '').lower() == item_type.lower()]
        
    if name:
        filtered_items = [item for item in filtered_items 
                        if getattr(getattr(item, 'item', None), 'name', None) 
                        and name.lower() in getattr(getattr(item, 'item', None), 'name', '').lower()]
                        
    if uniquename:
        filtered_items = [item for item in filtered_items 
                       if getattr(getattr(item, 'item', None), 'uniquename', None) 
                       and uniquename.lower() == getattr(getattr(item, 'item', None), 'uniquename', '').lower()]
    
    # Limita o número de resultados (0 retorna todos)
    if limit > 0:
        limited_results = []
        for i, item in enumerate(filtered_items):
            if i >= limit:
                break
            limited_results.append(item)
        return limited_results
    else:
        return filtered_items

@router.get("/stats", response_model=Dict[str, Any])
def get_item_stats():
    """
    Retorna estatísticas gerais sobre os itens disponíveis.
    """
    result = read_items()
    
    # Verifica se retornou uma mensagem de erro
    if isinstance(result, dict) and "message" in result:
        raise HTTPException(status_code=404, detail=result["message"])
    
    # Contagem por tier
    tiers = {}
    for item in result:
        if getattr(getattr(item, 'item', None), 'tier', None):
            tier_key = f"T{getattr(getattr(item, 'item', None), 'tier', None)}"
            tiers[tier_key] = tiers.get(tier_key, 0) + 1
    
    # Contagem por tipo
    types = {}
    for item in result:
        if getattr(getattr(item, 'item', None), 'item_type', None):
            types[getattr(getattr(item, 'item', None), 'item_type', None)] = types.get(getattr(getattr(item, 'item', None), 'item_type', None), 0) + 1
    
    # Contagem por categoria
    categories = {}
    for item in result:
        if getattr(getattr(item, 'item', None), 'shopcategory', None):
            categories[getattr(getattr(item, 'item', None), 'shopcategory', None)] = categories.get(getattr(getattr(item, 'item', None), 'shopcategory', None), 0) + 1
    
    # Contagem por classe
    classes = {
        "ItemBase": 0,
        "Weapon": 0,
        "Armor": 0,
        "Consumable": 0,
        "Resource": 0,
        "Mount": 0,
        "Furniture": 0,
        "Accessory": 0,
        "Other": 0
    }
    
    for item in result:
        item_data = getattr(item, 'item', None)
        if isinstance(item_data, Weapon):
            classes["Weapon"] += 1
        elif isinstance(item_data, Armor):
            classes["Armor"] += 1
        elif isinstance(item_data, Consumable):
            classes["Consumable"] += 1
        elif isinstance(item_data, Resource):
            classes["Resource"] += 1
        elif isinstance(item_data, Mount):
            classes["Mount"] += 1
        elif isinstance(item_data, Furniture):
            classes["Furniture"] += 1
        elif isinstance(item_data, Accessory):
            classes["Accessory"] += 1
        elif isinstance(item_data, Other):
            classes["Other"] += 1
        else:
            classes["ItemBase"] += 1
    
    return {
        "total_items": len(result),
        "by_tier": tiers,
        "by_type": types,
        "by_category": categories,
        "by_class": classes
    }

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
        found_item = next((item for item in result if getattr(getattr(item, 'item', None), 'id', None) == item_id), None)
        if found_item:
            return found_item
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar itens: {str(e)}")
    
    raise HTTPException(status_code=404, detail=f"Item com ID {item_id} não encontrado")

@router.get("/search/{term}", response_model=List[Item])
def search_items(term: str, limit: int = Query(20, description="Número máximo de itens a retornar")):
    """
    Pesquisa itens por termo no nome ou uniquename.
    """
    result = read_items()
    
    # Verifica se retornou uma mensagem de erro
    if isinstance(result, dict) and "message" in result:
        raise HTTPException(status_code=404, detail=result["message"])
    
    # Busca por termo no nome ou uniquename
    term = term.lower()
    found_items = []
    count = 0
    
    for item in result:
        item_data = getattr(item, 'item', None)
        name = getattr(item_data, 'name', '')
        uniquename = getattr(item_data, 'uniquename', '')
        description = getattr(item_data, 'description', '')
        
        if ((name and term in name.lower()) or 
            (uniquename and term in uniquename.lower()) or
            (description and term in description.lower())):
            found_items.append(item)
            count += 1
            
            if count >= limit:
                break
    
    if not found_items:
        raise HTTPException(status_code=404, detail=f"Nenhum item encontrado para o termo '{term}'")
    
    return found_items

@router.get("/type/{item_type}", response_model=List[Item])
def get_items_by_type(
    item_type: str, 
    tier: Optional[int] = Query(None, description="Filtrar por tier"),
    limit: int = Query(50, description="Número máximo de itens a retornar")
):
    """
    Retorna itens de um tipo específico (Arma, Armadura, Recurso, etc).
    """
    result = read_items()
    
    # Verifica se retornou uma mensagem de erro
    if isinstance(result, dict) and "message" in result:
        raise HTTPException(status_code=404, detail=result["message"])
    
    # Filtra itens por tipo
    filtered_items = [item for item in result 
                     if getattr(getattr(item, 'item', None), 'item_type', None) 
                     and getattr(getattr(item, 'item', None), 'item_type', '').lower() == item_type.lower()]
    
    # Filtra por tier se especificado
    if tier is not None:
        filtered_items = [item for item in filtered_items if getattr(getattr(item, 'item', None), 'tier', None) == tier]
    
    # Limita o número de resultados
    if limit > 0 and len(filtered_items) > limit:
        filtered_items = filtered_items[:limit]
    
    if not filtered_items:
        raise HTTPException(status_code=404, detail=f"Nenhum item do tipo '{item_type}' encontrado")
    
    return filtered_items
