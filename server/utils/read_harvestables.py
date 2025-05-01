import os
import xml.etree.ElementTree as ET
import re

# Importa a Tipagem da classe de Harvestables
from server.schemas.harvestables import Harvestable, HarvestTier

def extract_name_from_locatag(locatag):
    """Extrai um nome legível de uma tag de localização"""
    if not locatag:
        return "Unknown Resource"
    
    # Remove o prefixo @HARVESTABLE_ se existir
    name = locatag.replace("@HARVESTABLE_", "")
    name = name.replace("@RESOURCES_", "")
    
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

def safe_bool(value, default=False):
    """Converte um valor para boolean de forma segura"""
    if not value:
        return default
    if isinstance(value, bool):
        return value
    return value.lower() in ('true', 'yes', '1', 't', 'y')

def determine_resource_type(name, resource):
    """Determina o tipo de recurso com base no nome e tipo"""
    resource_name = (name or "").lower()
    resource_type = (resource or "").lower()
    
    if "wood" in resource_name or "wood" in resource_type:
        return "Madeira"
    elif "rock" in resource_name or "stone" in resource_name or "rock" in resource_type:
        return "Pedra"
    elif "fiber" in resource_name or "fiber" in resource_type:
        return "Fibra"
    elif "hide" in resource_name or "hide" in resource_type:
        return "Couro"
    elif "ore" in resource_name or "ore" in resource_type:
        return "Minério"
    
    return "Outros"

def determine_location(name, resource):
    """Determina locais típicos com base no nome e tipo"""
    resource_name = (name or "").lower()
    resource_type = (resource or "").lower()
    
    if "forest" in resource_name or "wood" in resource_name or "tree" in resource_name:
        return "Floresta"
    elif "mountain" in resource_name or "highland" in resource_name or "rock" in resource_name:
        return "Montanhas"
    elif "swamp" in resource_name or "marsh" in resource_name:
        return "Pântano"
    elif "steppe" in resource_name or "highland" in resource_name:
        return "Estepe"
    
    return "Qualquer lugar"

def read_harvestables():
    """
    Lê o arquivo harvestables.xml do Albion Online e retorna uma lista de objetos Harvestable.
    """
    # Encontra o diretório raiz do servidor
    file_path = os.path.join(os.environ["TANAKAI_DUMPS"], "harvestables.xml")
    
    # Verifica se o arquivo harvestables.xml existe
    if not os.path.exists(file_path):
        return {"message": "O arquivo harvestables.xml não foi encontrado"}

    try:
        # Lista para armazenar os recursos
        harvestables_list = []
        
        # Contador para gerar IDs sequenciais
        next_id = 1
        
        # Abre e lê o arquivo XML
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Encontra todos os elementos Harvestable
        for harvestable_elem in root.findall(".//Harvestable"):
            try:
                # Extrai os atributos principais
                name = harvestable_elem.get("name", "")
                resource = harvestable_elem.get("resource", "")
                
                # Gera um uniquename com base no nome
                uniquename = f"{name}_{resource}"
                
                # Encontra os tiers deste tipo de recurso
                for tier_elem in harvestable_elem.findall("Tier"):
                    tier_num = safe_int(tier_elem.get("tier", 0))
                    item = tier_elem.get("item", "")
                    
                    if tier_num == 0 or not item:
                        continue  # Pula se não tiver tier ou item válido
                    
                    # Extrai detalhes do tier
                    harvesttimeseconds = safe_float(tier_elem.get("harvesttimeseconds", 0))
                    maxchargesperharvest = safe_int(tier_elem.get("maxchargesperharvest", 0))
                    respawntimeseconds = safe_int(tier_elem.get("respawntimeseconds", 0))
                    requirestool = safe_bool(tier_elem.get("requirestool", False))
                    
                    # Determina o tipo do recurso e localização
                    resource_type = determine_resource_type(name, resource)
                    location = determine_location(name, resource)
                    
                    # Cria um ID único para o recurso combinado com tier
                    uniquename_with_tier = f"{uniquename}_T{tier_num}"
                    
                    # Cria um objeto Harvestable com os dados extraídos
                    harvestable_data = {
                        "uniquename": uniquename_with_tier,
                        "name": name,
                        "resource": resource,
                        "tier": tier_num,
                        
                        # Detalhes de coleta
                        "harvesttimeseconds": harvesttimeseconds,
                        "maxchargesperharvest": maxchargesperharvest,
                        "respawntimeseconds": respawntimeseconds,
                        "requirestool": requirestool,
                        
                        # Campos para compatibilidade com a API
                        "id": next_id,
                        "resource_type": resource_type,
                        "location": location,
                        "item": item
                    }
                    
                    harvestables_list.append(Harvestable(**harvestable_data))
                    next_id += 1
                    
            except Exception as e:
                print(f"Erro ao processar harvestable '{name}': {e}")
        
        # Se não conseguiu processar nenhum recurso do arquivo, retorna erro
        if not harvestables_list:
            erro_msg = "Nenhum recurso coletável foi processado do arquivo XML."
            print(erro_msg)
            return {"message": erro_msg}
            
        print(f"Total de recursos coletáveis processados: {len(harvestables_list)}")
        return harvestables_list
    except Exception as e:
        erro_msg = f"Erro ao processar o arquivo de recursos coletáveis: {str(e)}"
        print(f"Erro ao ler arquivo de recursos coletáveis: {e}")
        return {"message": erro_msg}

if __name__ == "__main__":
    # Teste da função
    result = read_harvestables()
    print(f"Tipo do resultado: {type(result)}")
    if not isinstance(result, dict):
        print(f"Total de recursos coletáveis: {len(result)}")
        for i, harvestable in enumerate(result[:5]):  # Mostra apenas os 5 primeiros
            print(f"Recurso {i+1}: {harvestable.uniquename}, Nome={harvestable.name}, Tier={harvestable.tier}, Tipo={harvestable.resource_type}, Item={harvestable.item}")
    else:
        print(f"Erro: {result['message']}") 