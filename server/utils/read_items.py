import os
import xml.etree.ElementTree as ET
import re

# Importa a Tipagem da classe de Items
from server.schemas.items import Item, ItemBase, Weapon, Armor, Consumable, Resource, Mount, Furniture, Accessory, Other

def extract_name_from_locatag(locatag):
    """Extrai um nome legível de uma tag de localização, preservando informações importantes"""
    if not locatag:
        return "Unknown Item"
    
    # Se o nome já parece ser um uniquename em vez de uma tag de localização, preservá-lo
    if not locatag.startswith("@"):
        # Converte underscores para espaços para melhor legibilidade
        return locatag.replace("_", " ")
    
    # Remove apenas o prefixo @ e mantém o restante da tag
    name = locatag
    if name.startswith("@"):
        name = name[1:]  # Remove apenas o @ inicial
    
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
    return value.lower() in ('true', 'yes', '1') if isinstance(value, str) else bool(value)

def determine_item_type(tag, uniquename, category=None):
    """Determina o tipo e a classe de item com base na tag, nome único e categoria"""
    tag_lower = tag.lower()
    uniquename_lower = uniquename.lower() if uniquename else ""
    
    # Determina o tipo de item para a API
    item_class = ItemBase
    
    # Armas
    if 'weapon' in tag_lower or any(x in uniquename_lower for x in ['sword', 'axe', 'spear', 'hammer', 'mace', 'bow', 'staff', 'dagger']):
        item_class = Weapon
    
    # Armaduras
    elif 'armor' in tag_lower or any(x in uniquename_lower for x in ['head', 'armor', 'shoes', 'helmet', 'boots']):
        item_class = Armor
    
    # Recursos
    elif 'resource' in tag_lower or any(x in uniquename_lower for x in ['wood', 'fiber', 'hide', 'ore', 'rock', 'cloth', 'leather', 'metal']):
        item_class = Resource
    
    # Consumíveis
    elif 'consumable' in tag_lower or any(x in uniquename_lower for x in ['potion', 'food', 'scroll', 'rune']):
        item_class = Consumable
    
    # Montarias
    elif 'mount' in tag_lower or any(x in uniquename_lower for x in ['horse', 'direwolf', 'direboar', 'direbear']):
        item_class = Mount
    
    # Mobília
    elif 'furniture' in tag_lower or any(x in uniquename_lower for x in ['table', 'chair', 'bed', 'chest', 'cabinet']):
        item_class = Furniture
        
    # Acessórios
    elif any(x in uniquename_lower for x in ['bag', 'cape', 'backpack', 'capeitem']):
        item_class = Accessory
    
    # Categorias baseadas nas loja
    if category:
        category_lower = category.lower()
        if 'weapon' in category_lower:
            item_class = Weapon
        elif 'armor' in category_lower or 'offhand' in category_lower:
            item_class = Armor
        elif 'resource' in category_lower or 'material' in category_lower:
            item_class = Resource
        elif 'consumable' in category_lower or 'potion' in category_lower or 'food' in category_lower:
            item_class = Consumable
        elif 'mount' in category_lower:
            item_class = Mount
        elif 'furniture' in category_lower or 'decoration' in category_lower:
            item_class = Furniture
        elif 'accessory' in category_lower or 'cape' in category_lower or 'bag' in category_lower:
            item_class = Accessory
    
    return item_class

def read_items():
    """
    Lê o arquivo items.xml do Albion Online e retorna uma lista de objetos Item.
    """
    # Encontra o diretório raiz do servidor
    file_path = os.path.join(os.environ.get("TANAKAI_DUMPS", "dumps"), "items.xml")
    
    # Verifica se o arquivo items.xml existe
    if not os.path.exists(file_path):
        return {"message": "O arquivo items.xml não foi encontrado"}

    try:
        # Usando iterparse para processar arquivos grandes de forma eficiente
        items_list = []
        context = ET.iterparse(file_path, events=("end",))
        
        # Contador para gerar IDs sequenciais
        next_id = 1
        
        # Padrão para encontrar tags de itens
        item_tags = ['simpleitem', 'weapon', 'armor', 'equipment', 'consumable', 
                    'accessory', 'resource', 'mount', 'furniture', 'hideout',
                    'journalitem', 'farmableitem', 'trackingitem', 'equipmentitem',
                    'consumableitem', 'furnitureitem', 'grownitem', 'crystalleagueitem',
                    'consumablefrominventoryitem', 'validitem', 'replacementitem']
        
        # Processamento principal do arquivo XML
        for event, elem in context:
            tag = elem.tag.lower()
            
            if any(item_tag in tag for item_tag in item_tags):
                try:
                    # Extrai os atributos principais
                    uniquename = elem.get("uniquename", "")
                    
                    # Determina a classe correspondente ao tipo de item
                    item_class = determine_item_type(
                        tag, 
                        uniquename, 
                        elem.get("shopcategory", "") or elem.get("craftingcategory", "")
                    )
                    
                    # Extrai o nome a partir da tag de localização
                    namelocatag = elem.get("localizationnamelocation", "")
                    desclocatag = elem.get("localizationdescriptionlocation", "") or elem.get("descriptionlocatag", "")
                    
                    friendly_name = extract_name_from_locatag(namelocatag or uniquename)
                    description = extract_name_from_locatag(desclocatag or "")
                    
                    # Determina qualidade (padrão Normal)
                    quality = "Normal"
                    
                    # Atributos comuns a todos os itens
                    common_attrs = {
                        "uniquename": uniquename,
                        "id": next_id,
                        "name": friendly_name,
                        "description": description,
                        "tier": safe_int(elem.get("tier")),
                        "itemvalue": safe_int(elem.get("itemvalue")),
                        "itempower": safe_int(elem.get("itempower")),
                        "weight": safe_float(elem.get("weight")),
                        "maxstacksize": safe_int(elem.get("maxstacksize", 1)),
                        "enchantmentlevel": safe_int(elem.get("enchantmentlevel", 0)),
                        "uisprite": elem.get("uisprite"),
                        "descriptionlocatag": elem.get("descriptionlocatag"),
                        "shopcategory": elem.get("shopcategory"),
                        "shopsubcategory1": elem.get("shopsubcategory1"),
                        "craftingcategory": elem.get("craftingcategory"),
                        "unlockedtocraft": safe_bool(elem.get("unlockedtocraft")),
                        "unlockedtoequip": safe_bool(elem.get("unlockedtoequip")),
                        "uicraftsoundstart": elem.get("uicraftsoundstart"),
                        "uicraftsoundfinish": elem.get("uicraftsoundfinish"),
                        "quality": quality
                    }
                    
                    # Inicializa o objeto de item específico
                    if item_class == Weapon:
                        item_obj = Weapon(
                            **common_attrs,
                            slottype=elem.get("slottype"),
                            attacktype=elem.get("attacktype"),
                            twohanded=safe_bool(elem.get("twohanded")),
                            attackdamage=safe_int(elem.get("attackdamage")),
                            attackspeed=safe_float(elem.get("attackspeed")),
                            defensepenetration=safe_float(elem.get("defensepenetration")),
                            resistancepenetration=safe_float(elem.get("resistancepenetration")),
                            durability=safe_int(elem.get("durability")),
                            durabilityloss_attack=safe_int(elem.get("durabilityloss_attack")),
                            durabilityloss_spelluse=safe_int(elem.get("durabilityloss_spelluse")),
                            durabilityloss_receivedattack=safe_int(elem.get("durabilityloss_receivedattack")),
                            durabilityloss_receivedspell=safe_int(elem.get("durabilityloss_receivedspell")),
                            activespellslots=safe_int(elem.get("activespellslots")),
                            passivespellslots=safe_int(elem.get("passivespellslots")),
                            canbeovercharged=safe_bool(elem.get("canbeovercharged")),
                            mainhandanimationtype=elem.get("mainhandanimationtype"),
                            abilitypower=safe_int(elem.get("abilitypower")),
                            maxqualitylevel=safe_int(elem.get("maxqualitylevel"))
                        )
                    
                    elif item_class == Armor:
                        item_obj = Armor(
                            **common_attrs,
                            slottype=elem.get("slottype"),
                            armor=safe_int(elem.get("armor")),
                            magicresistance=safe_int(elem.get("magicresistance")),
                            energymax=safe_int(elem.get("energymax")),
                            energyregen=safe_int(elem.get("energyregen")),
                            durability=safe_int(elem.get("durability")),
                            durabilityloss_receivedattack=safe_int(elem.get("durabilityloss_receivedattack")),
                            durabilityloss_receivedspell=safe_int(elem.get("durabilityloss_receivedspell")),
                            activespellslots=safe_int(elem.get("activespellslots")),
                            passivespellslots=safe_int(elem.get("passivespellslots")),
                            abilitypower=safe_int(elem.get("abilitypower")),
                            maxqualitylevel=safe_int(elem.get("maxqualitylevel"))
                        )
                    
                    elif item_class == Consumable:
                        item_obj = Consumable(
                            **common_attrs,
                            consumespell=elem.get("consumespell"),
                            charges=safe_int(elem.get("charges")),
                            tradable=safe_bool(elem.get("tradable")),
                            uispriteoverlay1=elem.get("uispriteoverlay1"),
                            foodbuff=elem.get("foodbuff"),
                            foodbuffduration=safe_int(elem.get("foodbuffduration")),
                            energyrestore=safe_int(elem.get("energyrestore")),
                            healthrestore=safe_int(elem.get("healthrestore")),
                            abilitypower=safe_int(elem.get("abilitypower"))
                        )
                    
                    elif item_class == Resource:
                        item_obj = Resource(
                            **common_attrs,
                            resourcetype=elem.get("resourcetype"),
                            famevalue=safe_int(elem.get("famevalue")),
                            enchantmentlevelrequirement=safe_int(elem.get("enchantmentlevelrequirement")),
                            farmable=safe_bool(elem.get("farmable") or 'farmable' in tag),
                            harvestable=safe_bool(elem.get("harvestable") or 'harvestable' in tag),
                            growtime=safe_int(elem.get("growtime"))
                        )
                    
                    elif item_class == Mount:
                        item_obj = Mount(
                            **common_attrs,
                            mountcategory=elem.get("mountcategory"),
                            mounttype=elem.get("mounttype"),
                            ridingparameters=elem.get("ridingparameters"),
                            movespeed=safe_float(elem.get("movespeed")),
                            stamina=safe_int(elem.get("stamina")),
                            staminaregeneration=safe_float(elem.get("staminaregeneration")),
                            carryweight=safe_float(elem.get("carryweight")),
                            mountskin=elem.get("mountskin"),
                            mountanimationset=elem.get("mountanimationset")
                        )
                    
                    elif item_class == Furniture:
                        item_obj = Furniture(
                            **common_attrs,
                            furniturecategory=elem.get("furniturecategory"),
                            placementtype=elem.get("placementtype"),
                            placementrotationtype=elem.get("placementrotationtype"),
                            prefab=elem.get("prefab"),
                            size=elem.get("size"),
                            ishideoutdecorationitem=safe_bool(elem.get("ishideoutdecorationitem"))
                        )
                    
                    elif item_class == Accessory:
                        item_obj = Accessory(
                            **common_attrs,
                            slottype=elem.get("slottype"),
                            carryweight=safe_float(elem.get("carryweight")),
                            extraslots=safe_int(elem.get("extraslots")),
                            durability=safe_int(elem.get("durability"))
                        )
                    
                    else:  # Outros tipos de itens
                        item_obj = Other(**common_attrs)
                    
                    # Constrói o item completo
                    full_item = Item(item=item_obj)
                    
                    # Adiciona à lista de itens
                    items_list.append(full_item)
                    next_id += 1
                    
                except Exception as e:
                    print(f"Erro ao processar item '{elem.get('uniquename', 'unknown')}': {str(e)}")
                finally:
                    # Limpa o elemento para liberar memória
                    elem.clear()
        
        # Se não conseguiu processar nenhum item do arquivo, retorna erro
        if not items_list:
            erro_msg = "Nenhum item foi processado do arquivo XML."
            print(erro_msg)
            return {"message": erro_msg}
            
        print(f"Total de itens processados: {len(items_list)}")
        return items_list
    except Exception as e:
        erro_msg = f"Erro ao processar o arquivo de itens: {str(e)}"
        print(f"Erro ao ler arquivo de itens: {e}")
        return {"message": erro_msg}

if __name__ == "__main__":
    # Teste da função
    result = read_items()
    print(f"Tipo do resultado: {type(result)}")
    if not isinstance(result, dict):
        print(f"Total de itens: {len(result)}")
        for i, item in enumerate(result[:5]):  # Mostra apenas os 5 primeiros
            item_data = item.item
            print(f"Item {i+1}: {item_data.uniquename}, Nome={item_data.name}, Tier={item_data.tier}, Tipo={item_data.item_type}, Classe={type(item_data).__name__}") 