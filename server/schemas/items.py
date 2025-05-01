# Define o schema de itens do Albion Online
from pydantic import BaseModel, Field
from typing import Optional

class Item(BaseModel):
    uniquename: str
    tier: Optional[int] = None
    itemvalue: Optional[int] = None
    weight: Optional[float] = None
    maxstacksize: Optional[int] = None
    enchantmentlevel: Optional[int] = None
    
    # Detalhes adicionais
    shopcategory: Optional[str] = None
    shopsubcategory: Optional[str] = None
    craftingcategory: Optional[str] = None
    
    # Atributos para armas e equipamentos
    attackdamage: Optional[int] = None
    defensepenetration: Optional[float] = None
    resistancepenetration: Optional[float] = None
    armor: Optional[int] = None
    magicresistance: Optional[int] = None
    
    # Campos para compatibilidade com API
    id: Optional[int] = Field(default=None, description="ID interno para referência")
    name: Optional[str] = Field(default=None, description="Nome amigável")
    description: Optional[str] = Field(default=None, description="Descrição do item")
    quality: Optional[str] = Field(default=None, description="Qualidade do item (Normal, Bom, Excelente, etc)")
    item_type: Optional[str] = Field(default=None, description="Tipo do item (Arma, Armadura, Recurso, etc)") 