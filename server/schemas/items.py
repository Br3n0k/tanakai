# Define o schema de itens do Albion Online
from pydantic import BaseModel, Field
from typing import Optional, List, Union, Dict, Literal

class ItemBase(BaseModel):
    """Classe base para todos os tipos de itens do Albion Online"""
    # Atributos identificadores e básicos
    uniquename: str
    id: Optional[int] = Field(default=None, description="ID interno para referência")
    name: Optional[str] = Field(default=None, description="Nome amigável")
    description: Optional[str] = Field(default=None, description="Descrição do item")
    
    # Atributos comuns a maioria dos itens
    tier: Optional[int] = None
    itemvalue: Optional[int] = None
    itempower: Optional[int] = None
    weight: Optional[float] = None
    maxstacksize: Optional[int] = None
    enchantmentlevel: Optional[int] = None
    
    # Atributos de interface e visualização
    uisprite: Optional[str] = None
    descriptionlocatag: Optional[str] = None
    
    # Categorias e tipos
    shopcategory: Optional[str] = None
    shopsubcategory1: Optional[str] = None
    craftingcategory: Optional[str] = None
    
    # Atributos de crafting e uso
    unlockedtocraft: Optional[bool] = None
    unlockedtoequip: Optional[bool] = None
    uicraftsoundstart: Optional[str] = None
    uicraftsoundfinish: Optional[str] = None
    
    # Atributos para compatibilidade com API
    quality: Optional[str] = Field(default=None, description="Qualidade do item (Normal, Bom, Excelente, etc)")
    item_type: Literal["Base"] = "Base"

class Weapon(ItemBase):
    """Classe para armas do Albion Online"""
    # Atributos específicos de armas
    slottype: Optional[str] = None
    attacktype: Optional[str] = None
    twohanded: Optional[bool] = None
    attackdamage: Optional[int] = None
    attackspeed: Optional[float] = None
    defensepenetration: Optional[float] = None
    resistancepenetration: Optional[float] = None
    
    # Atributos de durabilidade
    durability: Optional[int] = None
    durabilityloss_attack: Optional[int] = None
    durabilityloss_spelluse: Optional[int] = None
    durabilityloss_receivedattack: Optional[int] = None
    durabilityloss_receivedspell: Optional[int] = None
    
    # Atributos de habilidades
    activespellslots: Optional[int] = None
    passivespellslots: Optional[int] = None
    canbeovercharged: Optional[bool] = None
    mainhandanimationtype: Optional[str] = None
    
    # Stats do item
    abilitypower: Optional[int] = None
    maxqualitylevel: Optional[int] = None
    
    # Discriminador
    item_type: Literal["Arma"] = "Arma"

class Armor(ItemBase):
    """Classe para armaduras do Albion Online"""
    # Atributos específicos de armaduras
    slottype: Optional[str] = None
    armor: Optional[int] = None
    magicresistance: Optional[int] = None
    energymax: Optional[int] = None
    energyregen: Optional[int] = None
    
    # Atributos de durabilidade
    durability: Optional[int] = None
    durabilityloss_receivedattack: Optional[int] = None
    durabilityloss_receivedspell: Optional[int] = None
    
    # Atributos de habilidades
    activespellslots: Optional[int] = None
    passivespellslots: Optional[int] = None
    
    # Stats do item
    abilitypower: Optional[int] = None
    maxqualitylevel: Optional[int] = None
    
    # Discriminador
    item_type: Literal["Armadura"] = "Armadura"

class Consumable(ItemBase):
    """Classe para itens consumíveis do Albion Online"""
    # Atributos específicos de consumíveis
    consumespell: Optional[str] = None
    charges: Optional[int] = None
    tradable: Optional[bool] = None
    uispriteoverlay1: Optional[str] = None
    
    # Efeitos do consumível
    foodbuff: Optional[str] = None
    foodbuffduration: Optional[int] = None
    energyrestore: Optional[int] = None
    healthrestore: Optional[int] = None
    
    # Atributos específicos de poções
    abilitypower: Optional[int] = None
    
    # Discriminador
    item_type: Literal["Consumível"] = "Consumível"

class Resource(ItemBase):
    """Classe para recursos do Albion Online"""
    # Atributos específicos de recursos
    resourcetype: Optional[str] = None
    famevalue: Optional[int] = None
    enchantmentlevelrequirement: Optional[int] = None
    
    # Atributos específicos para recursos farmáveis
    farmable: Optional[bool] = None
    harvestable: Optional[bool] = None
    growtime: Optional[int] = None
    
    # Discriminador
    item_type: Literal["Recurso"] = "Recurso"

class Mount(ItemBase):
    """Classe para montarias do Albion Online"""
    # Atributos específicos de montarias
    mountcategory: Optional[str] = None
    mounttype: Optional[str] = None
    ridingparameters: Optional[str] = None
    
    # Atributos de desempenho
    movespeed: Optional[float] = None
    stamina: Optional[int] = None
    staminaregeneration: Optional[float] = None
    carryweight: Optional[float] = None
    
    # Atributos visuais
    mountskin: Optional[str] = None
    mountanimationset: Optional[str] = None
    
    # Discriminador
    item_type: Literal["Montaria"] = "Montaria"

class Furniture(ItemBase):
    """Classe para móveis e decorações do Albion Online"""
    # Atributos específicos de móveis
    furniturecategory: Optional[str] = None
    placementtype: Optional[str] = None
    placementrotationtype: Optional[str] = None
    
    # Atributos de visualização
    prefab: Optional[str] = None
    size: Optional[str] = None
    ishideoutdecorationitem: Optional[bool] = None
    
    # Discriminador
    item_type: Literal["Mobília"] = "Mobília"

class Accessory(ItemBase):
    """Classe para acessórios do Albion Online"""
    # Atributos específicos de acessórios
    slottype: Optional[str] = None
    carryweight: Optional[float] = None
    extraslots: Optional[int] = None
    
    # Atributos de durabilidade
    durability: Optional[int] = None
    
    # Discriminador
    item_type: Literal["Acessório"] = "Acessório"

class Other(ItemBase):
    """Classe para outros itens do Albion Online que não se encaixam em categorias específicas"""
    # Discriminador
    item_type: Literal["Outros"] = "Outros"

# Definição do item principal que usa o discriminador
class Item(BaseModel):
    """Classe unificada que pode representar qualquer tipo de item do Albion Online"""
    # Classe que pode ser qualquer um dos tipos específicos
    item: Union[
        ItemBase, 
        Weapon, 
        Armor, 
        Consumable, 
        Resource, 
        Mount, 
        Furniture,
        Accessory,
        Other
    ] = Field(discriminator="item_type")
    
    # Atributos opcionais adicionais
    spells: Optional[List[str]] = None
    craftingRequirements: Optional[Dict[str, int]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "item": {
                    "uniquename": "T4_MAIN_ARCANESTAFF",
                    "name": "Cajado Arcano do Adepto",
                    "tier": 4,
                    "item_type": "Arma",
                    "quality": "Normal",
                    "itemvalue": 1250,
                    "weight": 1.8,
                    "attackdamage": 110,
                    "abilitypower": 100
                }
            }
        } 