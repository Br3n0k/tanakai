from typing import List, Union, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from server.utils.read_mobs import read_mobs
from server.schemas.mobs import Mob

router = APIRouter()

@router.get("/", response_model=List[Mob])
def get_mobs(
    tier: Optional[int] = Query(None, description="Filtrar por tier"),
    category: Optional[str] = Query(None, description="Filtrar por categoria (boss, standard, etc)"),
    hostility: Optional[str] = Query(None, description="Filtrar por hostilidade (hostile, passive, etc)"),
    faction: Optional[str] = Query(None, description="Filtrar por facção (KEEPER, UNDEAD, etc)"),
    limit: int = Query(100, description="Número máximo de mobs a retornar")
):
    """
    Retorna a lista de mobs disponíveis com opções de filtro.
    """
    result = read_mobs()
    
    # Verifica se retornou uma mensagem de erro
    if isinstance(result, dict) and "message" in result:
        raise HTTPException(status_code=404, detail=result["message"])
    
    # Aplica filtros se fornecidos
    filtered_mobs = result
    
    if tier is not None:
        filtered_mobs = [mob for mob in filtered_mobs if getattr(mob, 'tier', None) == tier]
        
    if category is not None:
        filtered_mobs = [mob for mob in filtered_mobs 
                        if getattr(mob, 'mobtypecategory', None) 
                        and category.lower() in getattr(mob, 'mobtypecategory', '').lower()]
        
    if hostility is not None:
        filtered_mobs = [mob for mob in filtered_mobs 
                        if getattr(mob, 'npchostility', None) 
                        and hostility.lower() in getattr(mob, 'npchostility', '').lower()]
        
    if faction is not None:
        filtered_mobs = [mob for mob in filtered_mobs 
                        if getattr(mob, 'faction', None) 
                        and faction.lower() in getattr(mob, 'faction', '').lower()]
    
    # Limita o número de resultados
    if limit > 0:
        limited_results = []
        count = 0
        for mob in filtered_mobs:
            limited_results.append(mob)
            count += 1
            if count >= limit:
                break
        return limited_results
    else:
        return filtered_mobs

@router.get("/stats", response_model=Dict[str, Any])
def get_mob_stats():
    """
    Retorna estatísticas gerais sobre os mobs disponíveis.
    """
    result = read_mobs()
    
    # Verifica se retornou uma mensagem de erro
    if isinstance(result, dict) and "message" in result:
        raise HTTPException(status_code=404, detail=result["message"])
    
    # Contagem por tier
    tiers = {}
    for mob in result:
        mob_tier = getattr(mob, 'tier', None)
        if mob_tier:
            tier_key = f"T{mob_tier}"
            tiers[tier_key] = tiers.get(tier_key, 0) + 1
    
    # Contagem por categoria
    categories = {}
    for mob in result:
        category = getattr(mob, 'mobtypecategory', None)
        if category:
            categories[category] = categories.get(category, 0) + 1
    
    # Contagem por facção
    factions = {}
    for mob in result:
        faction = getattr(mob, 'faction', None)
        if faction:
            factions[faction] = factions.get(faction, 0) + 1
    
    # Contagem por hostilidade
    hostility = {}
    for mob in result:
        hostile = getattr(mob, 'npchostility', None)
        if hostile:
            hostility[hostile] = hostility.get(hostile, 0) + 1
    
    return {
        "total_mobs": len(result),
        "by_tier": tiers,
        "by_category": categories,
        "by_faction": factions,
        "by_hostility": hostility
    }

@router.get("/{mob_id}", response_model=Mob)
def get_mob(mob_id: int):
    """
    Retorna um mob específico pelo ID.
    """
    result = read_mobs()
    
    # Verifica se retornou uma mensagem de erro
    if isinstance(result, dict) and "message" in result:
        raise HTTPException(status_code=404, detail=result["message"])
    
    # Busca o mob pelo ID
    try:
        found_mob = next((mob for mob in result if getattr(mob, 'id', None) == mob_id), None)
        if found_mob:
            return found_mob
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar mobs: {str(e)}")
    
    raise HTTPException(status_code=404, detail=f"Mob com ID {mob_id} não encontrado")

@router.get("/search/{term}", response_model=List[Mob])
def search_mobs(term: str, limit: int = Query(20, description="Número máximo de mobs a retornar")):
    """
    Pesquisa mobs por termo no nome ou uniquename.
    """
    result = read_mobs()
    
    # Verifica se retornou uma mensagem de erro
    if isinstance(result, dict) and "message" in result:
        raise HTTPException(status_code=404, detail=result["message"])
    
    # Busca por termo no nome ou uniquename
    term = term.lower()
    found_mobs = []
    count = 0
    
    for mob in result:
        name = getattr(mob, 'name', '')
        uniquename = getattr(mob, 'uniquename', '')
        namelocatag = getattr(mob, 'namelocatag', '')
        
        if ((name and term in name.lower()) or 
            (uniquename and term in uniquename.lower()) or
            (namelocatag and term in namelocatag.lower())):
            found_mobs.append(mob)
            count += 1
            
            if count >= limit:
                break
    
    if not found_mobs:
        raise HTTPException(status_code=404, detail=f"Nenhum mob encontrado para o termo '{term}'")
    
    return found_mobs 