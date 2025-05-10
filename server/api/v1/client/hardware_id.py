"""
Endpoints para obter informações de hardware e identificação de sistema.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from server.api.v1.client.new_os import get_system_identifier, get_identifier

router = APIRouter()

@router.get("/identifier", response_model=Dict[str, Any])
async def get_hardware_identifier():
    """
    Obtém o identificador único da máquina com informações completas do sistema.
    
    Returns:
        Dict[str, Any]: Um dicionário contendo o identificador único e informações do sistema
    """
    try:
        return get_system_identifier()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter identificador do sistema: {str(e)}")

@router.get("/identifier/simple", response_model=Dict[str, str])
async def get_simple_identifier():
    """
    Obtém apenas o identificador único da máquina sem informações adicionais.
    
    Returns:
        Dict[str, str]: Um dicionário contendo apenas o identificador único
    """
    try:
        return {"identifier": get_identifier()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter identificador do sistema: {str(e)}")

@router.post("/verify_identifier", response_model=Dict[str, bool])
async def verify_identifier(data: Dict[str, str]):
    """
    Verifica se o identificador fornecido corresponde ao identificador atual do sistema.
    
    Args:
        data: Dicionário contendo o identificador a ser verificado
        
    Returns:
        Dict[str, bool]: Resultado da verificação (match: True/False)
    """
    try:
        client_identifier = data.get("identifier", "")
        if not client_identifier:
            raise HTTPException(status_code=400, detail="Identificador não fornecido")
            
        system_identifier = get_identifier()
        return {"match": client_identifier == system_identifier}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao verificar identificador: {str(e)}") 