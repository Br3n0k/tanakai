import os
import xml.etree.ElementTree as ET
import json
import re
import sys
from collections import Counter

def analyze_xml_structure():
    file_path = os.path.join(os.environ.get("TANAKAI_DUMPS", "dumps"), "items.xml")
    
    if not os.path.exists(file_path):
        return f"Arquivo não encontrado: {file_path}"
    
    try:
        # Informações sobre o arquivo
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        print(f"Arquivo: {file_path}")
        print(f"Tamanho: {file_size_mb:.2f} MB")
        
        print("\n=== ANÁLISE DE LINHA POR LINHA ===")
        # Contadores para tags e atributos
        item_types = Counter()
        all_attributes = set()
        common_attributes = Counter()
        weapon_attributes = Counter()
        armor_attributes = Counter()
        resource_attributes = Counter()
        consumable_attributes = Counter()
        
        # Exemplos de cada tipo de item
        item_examples = {}
        
        # Padrão para encontrar tags de itens
        item_pattern = re.compile(r'<(\w+item|weapon|armor|tool|equipment|consumable|accessory|resource|mount|furniture|chest)\s')
        # Padrão para extrair atributos
        attr_pattern = re.compile(r'(\w+)="([^"]*)"')
        
        # Processamento linha por linha
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            for line_number, line in enumerate(file, 1):
                if line_number % 10000 == 0:
                    print(f"Processando linha {line_number}...")
                
                # Encontra tipos de itens
                match = item_pattern.search(line)
                if match:
                    item_type = match.group(1)
                    item_types[item_type] += 1
                    
                    # Armazena exemplo deste tipo se ainda não tivermos
                    if item_type not in item_examples and len(item_examples) < 10:
                        item_examples[item_type] = line.strip()
                    
                    # Extrai atributos
                    attributes = attr_pattern.findall(line)
                    for attr_name, attr_value in attributes:
                        all_attributes.add(attr_name)
                        common_attributes[attr_name] += 1
                        
                        # Conta atributos específicos por tipo
                        if 'weapon' in item_type:
                            weapon_attributes[attr_name] += 1
                        elif 'armor' in item_type:
                            armor_attributes[attr_name] += 1
                        elif 'resource' in item_type or 'material' in item_type:
                            resource_attributes[attr_name] += 1
                        elif 'consumable' in item_type or 'potion' in item_type:
                            consumable_attributes[attr_name] += 1
        
        # Exibe resultados
        print("\n=== TIPOS DE ITENS ENCONTRADOS ===")
        for item_type, count in item_types.most_common():
            print(f"{item_type}: {count} itens")
        
        print("\n=== ATRIBUTOS MAIS COMUNS ===")
        for attr, count in common_attributes.most_common(20):
            print(f"{attr}: {count} ocorrências")
        
        print("\n=== ATRIBUTOS ESPECÍFICOS DE ARMAS ===")
        for attr, count in weapon_attributes.most_common(15):
            print(f"{attr}: {count} ocorrências")
        
        print("\n=== ATRIBUTOS ESPECÍFICOS DE ARMADURAS ===")
        for attr, count in armor_attributes.most_common(15):
            print(f"{attr}: {count} ocorrências")
        
        print("\n=== ATRIBUTOS ESPECÍFICOS DE RECURSOS ===")
        for attr, count in resource_attributes.most_common(15):
            print(f"{attr}: {count} ocorrências")
        
        print("\n=== ATRIBUTOS ESPECÍFICOS DE CONSUMÍVEIS ===")
        for attr, count in consumable_attributes.most_common(15):
            print(f"{attr}: {count} ocorrências")
        
        print("\n=== EXEMPLOS DE TIPOS DE ITENS ===")
        for item_type, example in item_examples.items():
            print(f"\n--- {item_type} ---")
            print(example)
        
        print("\n=== SUGESTÃO DE ESQUEMA DE ITEM ===")
        # Lista com atributos mais importantes, ordenados por frequência
        important_attrs = [attr for attr, _ in common_attributes.most_common(20)]
        weapon_attrs = [attr for attr, _ in weapon_attributes.most_common(10) if attr not in important_attrs]
        armor_attrs = [attr for attr, _ in armor_attributes.most_common(10) if attr not in important_attrs]
        consumable_attrs = [attr for attr, _ in consumable_attributes.most_common(10) if attr not in important_attrs]
        
        print("class Item(BaseModel):")
        print("    # Atributos principais")
        for attr in important_attrs[:10]:
            print(f"    {attr}: Optional[str] = None")
        
        print("\n    # Atributos de armas")
        for attr in weapon_attrs[:5]:
            print(f"    {attr}: Optional[str] = None")
        
        print("\n    # Atributos de armaduras")
        for attr in armor_attrs[:5]:
            print(f"    {attr}: Optional[str] = None")
        
        print("\n    # Atributos de consumíveis")
        for attr in consumable_attrs[:5]:
            print(f"    {attr}: Optional[str] = None")
        
        return "Análise concluída"
    except Exception as e:
        return f"Erro na análise: {str(e)}"

if __name__ == "__main__":
    print(analyze_xml_structure()) 