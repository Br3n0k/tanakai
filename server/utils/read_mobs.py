import os
import xml.etree.ElementTree as ET
import re

# Importa a Tipagem da classe de Mobs
from server.schemas.mobs import Mob, MobSpell, MobLoot

def extract_name_from_locatag(locatag):
    """Extrai um nome legível de uma tag de localização"""
    if not locatag:
        return "Unknown Mob"
    
    # Remove o prefixo @MOB_ se existir
    name = locatag.replace("@MOB_", "")
    
    # Substitui underscores por espaços
    name = name.replace("_", " ")
    
    # Remove códigos como T4, etc.
    name = re.sub(r'T\d+', '', name)
    
    # Limpa espaços extras
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name

def safe_int(value, default=None):
    """Converte um valor para inteiro de forma segura, lidando com valores de ponto flutuante"""
    if not value:
        return default
    try:
        # Tenta converter diretamente para inteiro
        return int(value)
    except ValueError:
        try:
            # Se falhar, tenta converter para float e depois para inteiro
            return int(float(value))
        except (ValueError, TypeError):
            return default

def safe_float(value, default=None):
    """Converte um valor para float de forma segura"""
    if not value:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_bool(value, default=None):
    """Converte um valor para boolean de forma segura"""
    if not value:
        return default
    return value.lower() in ('true', 'yes', '1')

def read_mobs():
    """
    Lê o arquivo mobs.xml do Albion Online e retorna uma lista de objetos Mob.
    """
    # Encontra o diretório raiz do servidor
    file_path = os.path.join(os.environ["TANAKAI_DUMPS"], "mobs.xml")
    
    # Verifica se o arquivo mobs.xml existe
    if not os.path.exists(file_path):
        return {"message": "O arquivo mobs.xml não foi encontrado"}

    try:
        # Usando iterparse para processar arquivos grandes de forma eficiente
        mobs_list = []
        context = ET.iterparse(file_path, events=("end",))
        
        # Contador para gerar IDs sequenciais
        next_id = 1
        
        # Processamento principal do arquivo XML
        for event, elem in context:
            if elem.tag == "Mob":  # Tag Mob com M maiúsculo no Albion
                try:
                    # Extrai os atributos principais
                    uniquename = elem.get("uniquename", "")
                    mobtypecategory = elem.get("mobtypecategory")
                    npchostility = elem.get("npchostility")
                    faction = elem.get("faction")
                    
                    # Atributos numéricos
                    tier = safe_int(elem.get("tier"))
                    abilitypower = safe_int(elem.get("abilitypower"))
                    fame = safe_int(elem.get("fame"))
                    attackdamage = safe_int(elem.get("attackdamage"))
                    hitpointsmax = safe_int(elem.get("hitpointsmax"))
                    hitpointsregeneration = safe_int(elem.get("hitpointsregeneration"))
                    energymax = safe_int(elem.get("energymax"))
                    energyregeneration = safe_int(elem.get("energyregeneration"))
                    physicalarmor = safe_int(elem.get("physicalarmor"))
                    magicresistance = safe_int(elem.get("magicresistance"))
                    crowdcontrolresistance = safe_int(elem.get("crowdcontrolresistance"))
                    respawntimesecondsmin = safe_int(elem.get("respawntimesecondsmin"))
                    respawntimesecondsmax = safe_int(elem.get("respawntimesecondsmax"))
                    maxcharges = safe_int(elem.get("maxcharges"))
                    timeperchargeseconds = safe_int(elem.get("timeperchargeseconds"))
                    aggrodelayafterspawn = safe_int(elem.get("aggrodelayafterspawn"))
                    energyreward = safe_int(elem.get("energyreward"))
                    mobvalue = safe_int(elem.get("mobvalue"))
                    
                    # Valores de ponto flutuante
                    movespeed = safe_float(elem.get("movespeed"))
                    attackmovespeed = safe_float(elem.get("attackmovespeed"))
                    meleeattackdamagetime = safe_float(elem.get("meleeattackdamagetime"))
                    attackspeed = safe_float(elem.get("attackspeed"))
                    roamingradius = safe_float(elem.get("roamingradius"))
                    roamingidletimemin = safe_float(elem.get("roamingidletimemin"))
                    roamingidletimemax = safe_float(elem.get("roamingidletimemax"))
                    aggroradius = safe_float(elem.get("aggroradius"))
                    pursuiradius = safe_float(elem.get("pursuitradius"))  # Corrigido para o nome correto no schema
                    alertradius = safe_float(elem.get("alertradius"))
                    collisionradius = safe_float(elem.get("collisionradius"))
                    attackcollisionradius = safe_float(elem.get("attackcollisionradius"))
                    attackrange = safe_float(elem.get("attackrange"))
                    prefabscale = safe_float(elem.get("prefabscale"))
                    damageaggrofactor = safe_float(elem.get("damageaggrofactor"))
                    healingaggrofactor = safe_float(elem.get("healingaggrofactor"))
                    shieldaggrofactor = safe_float(elem.get("shieldaggrofactor"))
                    silvermodifier = safe_float(elem.get("silvermodifier"))
                    
                    # Outros atributos
                    prefab = elem.get("prefab")
                    attacktype = elem.get("attacktype")
                    avatar = elem.get("avatar")
                    avatarring = elem.get("avatarring")
                    lootprefab = elem.get("lootprefab")
                    energyrewardspell = elem.get("energyrewardspell")
                    alertsfactions = elem.get("alertsfactions")
                    dangerstate = elem.get("dangerstate")
                    immunetoforcedmovement = safe_bool(elem.get("immunetoforcedmovement"))
                    namelocatag = elem.get("namelocatag")
                    
                    # Extrai o nome a partir da tag de localização
                    friendly_name = extract_name_from_locatag(namelocatag)
                    
                    # Processar habilidades (spells)
                    spells = []
                    ai_element = elem.find("AI/Behaviour")
                    if ai_element is not None:
                        for spell_elem in ai_element.findall("Spell"):
                            spell = MobSpell(
                                name=spell_elem.get("name"),
                                target=spell_elem.get("target"),
                                cooldowntillnextcast=safe_float(spell_elem.get("cooldowntillnextcast"))
                            )
                            spells.append(spell)
                    
                    # Processar loot
                    loot_items = []
                    loot_element = elem.find("Loot")
                    if loot_element is not None:
                        # Processar itens Harvestable
                        for harvest_elem in loot_element.findall("Harvestable"):
                            loot_item = MobLoot(
                                type="Harvestable",
                                name=harvest_elem.get("type"),
                                tier=harvest_elem.get("tier")
                            )
                            loot_items.append(loot_item)
                        
                        # Processar referências de loot
                        for ref_elem in loot_element.findall("LootListReference"):
                            loot_item = MobLoot(
                                type="LootListReference",
                                name=ref_elem.get("name"),
                                chance=safe_float(ref_elem.get("chance"))
                            )
                            loot_items.append(loot_item)
                    
                    # Cria um objeto Mob com os dados extraídos
                    mob_data = {
                        # Atributos principais
                        "uniquename": uniquename,
                        "mobtypecategory": mobtypecategory,
                        "npchostility": npchostility,
                        "tier": tier,
                        "faction": faction,
                        
                        # Atributos de combate
                        "abilitypower": abilitypower,
                        "attackdamage": attackdamage,
                        "hitpointsmax": hitpointsmax,
                        "hitpointsregeneration": hitpointsregeneration,
                        "energymax": energymax,
                        "energyregeneration": energyregeneration,
                        "attacktype": attacktype,
                        "attackrange": attackrange,
                        "attackspeed": attackspeed,
                        "attackmovespeed": attackmovespeed,
                        "meleeattackdamagetime": meleeattackdamagetime,
                        "physicalarmor": physicalarmor,
                        "magicresistance": magicresistance,
                        "crowdcontrolresistance": crowdcontrolresistance,
                        
                        # Atributos de comportamento
                        "movespeed": movespeed,
                        "roamingradius": roamingradius,
                        "roamingidletimemin": roamingidletimemin,
                        "roamingidletimemax": roamingidletimemax,
                        "aggroradius": aggroradius,
                        "pursuiradius": pursuiradius,
                        "alertradius": alertradius,
                        "collisionradius": collisionradius,
                        "attackcollisionradius": attackcollisionradius,
                        
                        # Atributos de aparência
                        "prefab": prefab,
                        "prefabscale": prefabscale,
                        "avatar": avatar,
                        "avatarring": avatarring,
                        
                        # Atributos de recompensa
                        "fame": fame,
                        "silvermodifier": silvermodifier,
                        "lootprefab": lootprefab,
                        "energyrewardspell": energyrewardspell,
                        "energyreward": energyreward,
                        "mobvalue": mobvalue,
                        
                        # Atributos de respawn
                        "respawntimesecondsmin": respawntimesecondsmin,
                        "respawntimesecondsmax": respawntimesecondsmax,
                        "maxcharges": maxcharges,
                        "timeperchargeseconds": timeperchargeseconds,
                        
                        # Atributos adicionais
                        "aggrodelayafterspawn": aggrodelayafterspawn,
                        "damageaggrofactor": damageaggrofactor,
                        "healingaggrofactor": healingaggrofactor,
                        "shieldaggrofactor": shieldaggrofactor,
                        "alertsfactions": alertsfactions,
                        "dangerstate": dangerstate,
                        "immunetoforcedmovement": immunetoforcedmovement,
                        "namelocatag": namelocatag,
                        
                        # Habilidades e loot
                        "spells": spells if spells else None,
                        "loot": loot_items if loot_items else None,
                        
                        # Campos para compatibilidade
                        "id": next_id,
                        "name": friendly_name,
                        "level": tier,  # O nível é basicamente o tier no Albion
                        "health": hitpointsmax,
                        "damage": attackdamage
                    }
                    
                    mobs_list.append(Mob(**mob_data))
                    next_id += 1
                    
                except Exception as e:
                    print(f"Erro ao processar mob '{elem.get('uniquename', 'unknown')}': {e}")
                finally:
                    # Limpa o elemento para liberar memória
                    elem.clear()
        
        # Se não conseguiu processar nenhum mob do arquivo, retorna erro
        if not mobs_list:
            erro_msg = "Nenhum mob foi processado do arquivo XML."
            print(erro_msg)
            return {"message": erro_msg}
            
        print(f"Total de mobs processados: {len(mobs_list)}")
        return mobs_list
    except Exception as e:
        erro_msg = f"Erro ao processar o arquivo: {str(e)}"
        print(f"Erro ao ler arquivo de mobs: {e}")
        return {"message": erro_msg}

if __name__ == "__main__":
    # Teste da função
    result = read_mobs()
    print(f"Tipo do resultado: {type(result)}")
    if not isinstance(result, dict):
        print(f"Total de mobs: {len(result)}")
        for i, mob in enumerate(result[:5]):  # Mostra apenas os 5 primeiros
            print(f"Mob {i+1}: {mob.uniquename}, Nome={mob.name}, Tier={mob.tier}, HP={mob.hitpointsmax}, Dano={mob.attackdamage}")
            if mob.spells:
                print(f"  Habilidades: {len(mob.spells)}")
                for spell in mob.spells[:2]:  # Mostra apenas as 2 primeiras habilidades
                    print(f"    - {spell.name} (alvo: {spell.target})")
            if mob.loot:
                print(f"  Loot: {len(mob.loot)} itens")
                for loot in mob.loot[:2]:  # Mostra apenas os 2 primeiros itens de loot
                    print(f"    - {loot.name} (tipo: {loot.type}, chance: {loot.chance})")
    else:
        print(f"Erro: {result['message']}")
