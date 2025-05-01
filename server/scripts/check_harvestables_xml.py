import os
import xml.etree.ElementTree as ET
import json

def analyze_xml_structure():
    server_dir = os.environ.get("TANAKAI_SERVER", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(server_dir, "dumps", "harvestables.xml")
    
    if not os.path.exists(file_path):
        return "Arquivo não encontrado: " + file_path
    
    try:
        # Informações sobre o arquivo
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        print(f"Arquivo: {file_path}")
        print(f"Tamanho: {file_size_mb:.2f} MB")
        
        # Abre e lê apenas o início do arquivo para detectar a estrutura
        with open(file_path, 'r', encoding='utf-8') as file:
            head = file.read(20000)  # Lê os primeiros 20KB
        
        print("\n--- Primeiros 300 caracteres ---")
        print(head[:300])
        print("..." if len(head) > 300 else "")
        
        # Tenta obter a raiz e analisar a estrutura
        try:
            # Adiciona um fechamento para o XML truncado, se necessário
            if "<harvestables>" in head.lower() and "</harvestables>" not in head.lower():
                parse_text = head + "</harvestables>"
            else:
                parse_text = head
                
            root = ET.fromstring(parse_text)
            
            print("\n--- Estrutura do XML ---")
            print(f"Tag raiz: {root.tag}")
            print(f"Atributos da raiz: {root.attrib}")
            
            # Encontra todos os tipos de tags únicas no primeiro nível
            item_tags = set()
            for child in root:
                item_tags.add(child.tag)
            
            print(f"\nTags de recursos coletáveis encontradas: {', '.join(item_tags)}")
            
            # Analisa um exemplo de cada tipo de tag
            for tag in item_tags:
                items = root.findall(f".//{tag}")
                if items:
                    print(f"\n--- Exemplo de {tag} ---")
                    item = items[0]
                    print(f"Atributos: {json.dumps(item.attrib, indent=2)}")
                    
                    # Amostra de alguns atributos importantes
                    important_attrs = ['uniquename', 'tier', 'enchantmentlevel', 
                                     'harvestingfame', 'harvestingmaxquantity', 
                                     'harvestingminquantity', 'harvestingtime',
                                     'resourcevalue', 'respawntime', 'size',
                                     'namelocatag']
                    
                    print("\nAtributos importantes:")
                    for attr in important_attrs:
                        if attr in item.attrib:
                            print(f"- {attr}: {item.attrib[attr]}")
                    
                    # Verifica filhos
                    children = list(item)
                    if children:
                        print("\nFilhos do elemento:")
                        for child in children[:5]:  # Limita a 5 filhos
                            print(f"- {child.tag}: {json.dumps(child.attrib, indent=2)}")
                            if list(child):
                                print(f"  (Tem {len(list(child))} sub-elementos)")
            
            # Conta quantos de cada tipo existem
            print("\n--- Contagem de tipos de recursos coletáveis ---")
            for tag in item_tags:
                count = len(root.findall(f".//{tag}"))
                print(f"{tag}: {count} recursos")
            
            # Analisa os tipos/tiers existentes
            tiers = {}
            for tag in item_tags:
                for item in root.findall(f".//{tag}"):
                    tier = item.get("tier", "")
                    if tier:
                        tiers[tier] = tiers.get(tier, 0) + 1
            
            print("\n--- Tiers de recursos coletáveis ---")
            for tier, count in tiers.items():
                print(f"Tier {tier}: {count} recursos")
            
            # Analisa padrões nos nomes únicos para identificar tipos
            name_patterns = {
                "wood": 0,
                "fiber": 0,
                "hide": 0,
                "ore": 0,
                "rock": 0,
                "tree": 0,
                "stone": 0,
                "plant": 0
            }
            
            for tag in item_tags:
                for item in root.findall(f".//{tag}"):
                    uniquename = item.get("uniquename", "").lower()
                    for pattern in name_patterns:
                        if pattern in uniquename:
                            name_patterns[pattern] += 1
            
            print("\n--- Padrões nos nomes únicos ---")
            for pattern, count in name_patterns.items():
                print(f"{pattern}: {count} recursos")
        
        except Exception as parse_error:
            print(f"\nErro ao analisar o XML: {parse_error}")
            print("Tentando analisar linha por linha...\n")
            
            # Análise de fallback - procura padrões em linhas
            lines = head.split('\n')
            
            patterns = {
                "<harvestable": 0,
                "<resource": 0,
                "uniquename=": 0,
                "tier=": 0,
                "harvestingfame=": 0,
                "harvestingtime=": 0,
                "resourcevalue=": 0,
                "respawntime=": 0
            }
            
            for line in lines:
                for pattern in patterns:
                    if pattern in line.lower():
                        patterns[pattern] += 1
                        
                        # Mostra alguns exemplos
                        if patterns[pattern] <= 2:
                            print(f"Exemplo ({pattern}): {line.strip()}")
            
            print("\nContagem de padrões encontrados:")
            for pattern, count in patterns.items():
                print(f"- {pattern}: {count}")
        
        return "Análise concluída"
    except Exception as e:
        return f"Erro na análise: {str(e)}"

if __name__ == "__main__":
    print(analyze_xml_structure()) 