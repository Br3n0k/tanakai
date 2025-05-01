import os
import xml.etree.ElementTree as ET
import json

def analyze_xml_structure():
    file_path = os.path.join(os.environ["TANAKAI_DUMPS"], "mobs.xml")
    
    if not os.path.exists(file_path):
        return "Arquivo não encontrado: " + file_path
    
    try:
        # Informações sobre o arquivo
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        print(f"Arquivo: {file_path}")
        print(f"Tamanho: {file_size_mb:.2f} MB")
        
        # Abre e lê apenas o início do arquivo para detectar a estrutura
        with open(file_path, 'r', encoding='utf-8') as file:
            head = file.read(20000)  # Aumentado para 20KB
        
        print("\n--- Primeiros 200 caracteres ---")
        print(head[:200])
        print("..." if len(head) > 200 else "")
        
        # Tenta obter a raiz e analisar o primeiro mob
        try:
            # Adiciona um fechamento para o XML truncado, se necessário
            if "<mobs>" in head and "</mobs>" not in head:
                parse_text = head + "</mobs>"
            else:
                parse_text = head
                
            root = ET.fromstring(parse_text)
            
            print("\n--- Estrutura do XML ---")
            print(f"Tag raiz: {root.tag}")
            print(f"Atributos da raiz: {root.attrib}")
            
            # Encontra todos os tipos de tags únicas
            all_tags = set()
            for elem in root.iter():
                all_tags.add(elem.tag)
            
            print(f"\nTags encontradas: {', '.join(all_tags)}")
            
            # Procura elementos mob em várias localizações possíveis
            mobpaths = [".//mob", "./mob", "mob", "./*"]
            mob_found = False
            
            for path in mobpaths:
                mob_elems = root.findall(path)
                
                if mob_elems:
                    print(f"\nEncontrados {len(mob_elems)} elementos em '{path}'")
                    first_mob = mob_elems[0]
                    
                    # Mostra detalhes do primeiro elemento encontrado
                    print(f"Tag do elemento: {first_mob.tag}")
                    print(f"Atributos: {json.dumps(first_mob.attrib, indent=2)}")
                    
                    # Verifica filhos
                    children = list(first_mob)
                    if children:
                        print("\nFilhos do elemento:")
                        for child in children:
                            print(f"- {child.tag}: {child.text}")
                    
                    mob_found = True
                    break
            
            if not mob_found:
                print("\nNenhum elemento 'mob' encontrado, mostrando os primeiros elementos:")
                for i, child in enumerate(list(root)[:5]):
                    print(f"{i+1}. Tag: {child.tag}, Atributos: {child.attrib}")
        
        except Exception as parse_error:
            print(f"\nErro ao analisar o XML: {parse_error}")
            print("Tentando analisar linha por linha...\n")
            
            # Análise de fallback - procura padrões em linhas
            lines = head.split('\n')
            
            patterns = {
                "<mob": 0,
                "id=": 0,
                "name=": 0,
                "level=": 0,
                "health=": 0,
                "damage=": 0
            }
            
            for line in lines:
                for pattern in patterns:
                    if pattern in line:
                        patterns[pattern] += 1
                        
                        # Mostra alguns exemplos
                        if patterns[pattern] <= 3:
                            print(f"Exemplo ({pattern}): {line.strip()}")
            
            print("\nContagem de padrões encontrados:")
            for pattern, count in patterns.items():
                print(f"- {pattern}: {count}")
        
        return "Análise concluída"
    except Exception as e:
        return f"Erro na análise: {str(e)}"

if __name__ == "__main__":
    print(analyze_xml_structure()) 