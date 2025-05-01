# Define o schema de recursos coletáveis do Albion Online
from pydantic import BaseModel, Field
from typing import Optional, List

class HarvestTier(BaseModel):
    tier: int
    item: str
    maxchargesperharvest: Optional[int] = None
    respawntimeseconds: Optional[int] = None
    harvesttimeseconds: Optional[float] = None
    requirestool: Optional[bool] = None
    startcharges: Optional[int] = None

class Harvestable(BaseModel):
    uniquename: str  # Adicionaremos o nome do recurso como uniquename
    name: Optional[str] = None  # Nome do recurso (WOOD, FIBER, etc)
    resource: Optional[str] = None  # Tipo de recurso
    tier: Optional[int] = None
    
    # Detalhes de coleta
    harvesttimeseconds: Optional[float] = None
    maxchargesperharvest: Optional[int] = None
    respawntimeseconds: Optional[int] = None
    requirestool: Optional[bool] = None
    
    # Campos para compatibilidade com API
    id: Optional[int] = Field(default=None, description="ID interno para referência")
    resource_type: Optional[str] = Field(default=None, description="Tipo de recurso (Madeira, Minério, etc)")
    location: Optional[str] = Field(default=None, description="Local típico onde é encontrado")
    item: Optional[str] = Field(default=None, description="Item produzido ao coletar") 