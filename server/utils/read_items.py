import os
import xml.etree.ElementTree as ET
import re

# Importa a Tipagem da classe de Items
from server.schemas.items import Item

def extract_name_from_locatag(locatag):
    """Extrai um nome legível de uma tag de localização"""
    if not locatag:
        return "Unknown Item"
    
    # Remove o prefixo @ITEMS_ se existir
    name = locatag.replace("@ITEMS_", "")
    name = name.replace("@WEAPONS_", "")
    name = name.replace("@ARMOR_", "")
    
    # Substitui underscores por espaços
    name = name.replace("_", " ")
    
    # Remove códigos como T4, etc.
    name = re.sub(r'T\d+', '', name)
    
    # Limpa espaços extras
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name

def safe_int(value, default=0):
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

def safe_float(value, default=0.0):
    """Converte um valor para float de forma segura"""
    if not value:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def determine_item_type(uniquename, category=None):
    """Determina o tipo de item com base no nome único e categoria"""
    uniquename = uniquename.lower()
    
    if "sword" in uniquename or "axe" in uniquename or "spear" in uniquename or "hammer" in uniquename or "mace" in uniquename:
        return "Arma"
    elif "head" in uniquename or "armor" in uniquename or "shoes" in uniquename:
        return "Armadura"
    elif "wood" in uniquename or "fiber" in uniquename or "hide" in uniquename or "ore" in uniquename or "rock" in uniquename:
        return "Recurso"
    elif "scroll" in uniquename or "rune" in uniquename:
        return "Consumível"
    elif "potion" in uniquename:
        return "Poção"
    elif "bag" in uniquename or "cape" in uniquename:
        return "Acessório"
    
    # Categorias padrão baseadas na árvore de categorias
    if category:
        if category == "weapon":
            return "Arma"
        elif category == "armor":
            return "Armadura"
        elif category == "consumable":
            return "Consumível"
        elif category == "accessory":
            return "Acessório"
        elif category == "material":
            return "Recurso"
    
    return "Outros"

def read_items():
    """
    Lê o arquivo items.xml do Albion Online e retorna uma lista de objetos Item.
    """
    # Encontra o diretório raiz do servidor
    file_path = os.path.join(os.environ["TANAKAI_DUMPS"], "items.xml")
    
    # Verifica se o arquivo items.xml existe
    if not os.path.exists(file_path):
        return {"message": "O arquivo items.xml não foi encontrado"}

    try:
        # Usando iterparse para processar arquivos grandes de forma eficiente
        items_list = []
        context = ET.iterparse(file_path, events=("end",))
        
        # Contador para gerar IDs sequenciais
        next_id = 1
        
        # Processamento principal do arquivo XML
        for event, elem in context:
            if elem.tag in ["SimpleItem", "Weapon", "Equipment", "ConsumableItem", "Armor", "SimpleItem", "EquipmentItem"]:
                try:
                    # Extrai os atributos principais
                    uniquename = elem.get("uniquename", "")
                    
                    # Converte atributos para os tipos corretos usando funções seguras
                    tier = safe_int(elem.get("tier"))
                    itemvalue = safe_int(elem.get("itemvalue"))
                    maxstacksize = safe_int(elem.get("maxstacksize", 1))
                    weight = safe_float(elem.get("weight", 0))
                    enchantmentlevel = safe_int(elem.get("enchantmentlevel", 0))
                    
                    # Atributos para equipamentos e armas
                    attackdamage = safe_int(elem.get("attackdamage", 0))
                    armor = safe_int(elem.get("armor", 0))
                    magicresistance = safe_int(elem.get("magicresistance", 0))
                    
                    # Valores de ponto flutuante
                    defensepenetration = safe_float(elem.get("defensepenetration", 0))
                    resistancepenetration = safe_float(elem.get("resistancepenetration", 0))
                    
                    # Informações de categoria
                    shopcategory = elem.get("shopcategory", "")
                    shopsubcategory = elem.get("shopsubcategory", "")
                    craftingcategory = elem.get("craftingcategory", "")
                    
                    # Extrai o nome a partir da tag de localização
                    namelocatag = elem.get("localizationnamelocation", "")
                    desclocatag = elem.get("localizationdescriptionlocation", "")
                    
                    friendly_name = extract_name_from_locatag(namelocatag or uniquename)
                    description = extract_name_from_locatag(desclocatag or "")
                    
                    # Determina o tipo do item
                    item_type = determine_item_type(uniquename, shopcategory or craftingcategory)
                    
                    # Determina qualidade (padrão Normal)
                    quality = "Normal"
                    
                    # Cria um objeto Item com os dados extraídos
                    item_data = {
                        "uniquename": uniquename,
                        "tier": tier,
                        "itemvalue": itemvalue,
                        "weight": weight,
                        "maxstacksize": maxstacksize,
                        "enchantmentlevel": enchantmentlevel,
                        
                        # Informações de categoria
                        "shopcategory": shopcategory,
                        "shopsubcategory": shopsubcategory,
                        "craftingcategory": craftingcategory,
                        
                        # Atributos para equipamentos
                        "attackdamage": attackdamage,
                        "defensepenetration": defensepenetration,
                        "resistancepenetration": resistancepenetration,
                        "armor": armor,
                        "magicresistance": magicresistance,
                        
                        # Campos para compatibilidade com a API
                        "id": next_id,
                        "name": friendly_name,
                        "description": description,
                        "quality": quality,
                        "item_type": item_type
                    }
                    
                    items_list.append(Item(**item_data))
                    next_id += 1
                    
                except Exception as e:
                    print(f"Erro ao processar item '{elem.get('uniquename', 'unknown')}': {e}")
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
            print(f"Item {i+1}: {item.uniquename}, Nome={item.name}, Tier={item.tier}, Tipo={item.item_type}, Valor={item.itemvalue}")
    else:
        print(f"Erro: {result['message']}") 