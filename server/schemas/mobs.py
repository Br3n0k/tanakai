# Define o schema do mob do Albion Online
from pydantic import BaseModel, Field
from typing import Optional, List

class MobSpell(BaseModel):
    name: str
    target: Optional[str] = None
    cooldowntillnextcast: Optional[float] = None

class MobLoot(BaseModel):
    type: Optional[str] = None
    name: Optional[str] = None
    tier: Optional[str] = None
    chance: Optional[float] = None

class Mob(BaseModel):
    # Atributos principais
    uniquename: str
    mobtypecategory: Optional[str] = None
    npchostility: Optional[str] = None
    tier: Optional[int] = None
    faction: Optional[str] = None
    
    # Atributos de combate
    abilitypower: Optional[int] = None
    attackdamage: Optional[int] = None
    hitpointsmax: Optional[int] = None
    hitpointsregeneration: Optional[int] = None
    energymax: Optional[int] = None
    energyregeneration: Optional[int] = None
    attacktype: Optional[str] = None
    attackrange: Optional[float] = None
    attackspeed: Optional[float] = None
    attackmovespeed: Optional[float] = None
    meleeattackdamagetime: Optional[float] = None
    physicalarmor: Optional[int] = None
    magicresistance: Optional[int] = None
    crowdcontrolresistance: Optional[int] = None
    
    # Atributos de comportamento
    movespeed: Optional[float] = None
    roamingradius: Optional[float] = None
    roamingidletimemin: Optional[float] = None
    roamingidletimemax: Optional[float] = None
    aggroradius: Optional[float] = None
    pursuiradius: Optional[float] = None
    alertradius: Optional[float] = None
    collisionradius: Optional[float] = None
    attackcollisionradius: Optional[float] = None
    
    # Atributos de aparência
    prefab: Optional[str] = None
    prefabscale: Optional[float] = None
    avatar: Optional[str] = None
    avatarring: Optional[str] = None
    
    # Atributos de recompensa
    fame: Optional[int] = None
    silvermodifier: Optional[float] = None
    lootprefab: Optional[str] = None
    energyrewardspell: Optional[str] = None
    energyreward: Optional[int] = None
    mobvalue: Optional[int] = None
    
    # Atributos de respawn
    respawntimesecondsmin: Optional[int] = None
    respawntimesecondsmax: Optional[int] = None
    maxcharges: Optional[int] = None
    timeperchargeseconds: Optional[int] = None
    
    # Atributos adicionais
    aggrodelayafterspawn: Optional[int] = None
    damageaggrofactor: Optional[float] = None
    healingaggrofactor: Optional[float] = None
    shieldaggrofactor: Optional[float] = None
    alertsfactions: Optional[str] = None
    dangerstate: Optional[str] = None
    immunetoforcedmovement: Optional[bool] = None
    namelocatag: Optional[str] = None
    
    # Habilidades e loot
    spells: Optional[List[MobSpell]] = None
    loot: Optional[List[MobLoot]] = None
    
    # Campos adicionais para compatibilidade com o ID original
    id: Optional[int] = Field(default=None, description="ID interno para referência")
    name: Optional[str] = Field(default=None, description="Nome amigável")
    level: Optional[int] = Field(default=None, description="Nível derivado do tier")
    health: Optional[int] = Field(default=None, description="Equivalente a hitpointsmax")
    damage: Optional[int] = Field(default=None, description="Equivalente a attackdamage")
