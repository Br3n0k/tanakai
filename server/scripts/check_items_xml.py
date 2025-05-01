import os
import xml.etree.ElementTree as ET
import json

def analyze_xml_structure():
    server_dir = os.environ.get("TANAKAI_SERVER", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(server_dir, "dumps", "items.xml")
    
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
            if "<items>" in head.lower() and "</items>" not in head.lower():
                parse_text = head + "</items>"
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
            
            print(f"\nTags de itens encontradas: {', '.join(item_tags)}")
            
            # Analisa um exemplo de cada tipo de tag
            for tag in item_tags:
                items = root.findall(f".//{tag}")
                if items:
                    print(f"\n--- Exemplo de {tag} ---")
                    item = items[0]
                    print(f"Atributos: {json.dumps(item.attrib, indent=2)}")
                    
                    # Amostra de alguns atributos importantes
                    important_attrs = ['uniquename', 'tier', 'itemvalue', 'maxstacksize', 
                                     'weight', 'shopcategory', 'craftingcategory', 
                                     'localizationnamelocation']
                    
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
            print("\n--- Contagem de tipos de itens ---")
            for tag in item_tags:
                count = len(root.findall(f".//{tag}"))
                print(f"{tag}: {count} items")
            
            # Analisa os tipos de categorias existentes
            categories = {}
            for tag in item_tags:
                for item in root.findall(f".//{tag}"):
                    cat = item.get("shopcategory", "")
                    if cat:
                        categories[cat] = categories.get(cat, 0) + 1
            
            print("\n--- Categorias de itens ---")
            for cat, count in categories.items():
                print(f"{cat}: {count} items")
        
        except Exception as parse_error:
            print(f"\nErro ao analisar o XML: {parse_error}")
            print("Tentando analisar linha por linha...\n")
            
            # Análise de fallback - procura padrões em linhas
            lines = head.split('\n')
            
            patterns = {
                "<item": 0,
                "<weapon": 0,
                "<armor": 0,
                "<consumable": 0,
                "uniquename=": 0,
                "tier=": 0,
                "itemvalue=": 0,
                "maxstacksize=": 0
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