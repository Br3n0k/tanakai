import logging
import json

# Configuração de logging
logger = logging.getLogger("TanakaiCallback")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', 
                                datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def handle_detection(processor_name, result, data, addr):
    """
    Função de callback padrão para processar detecções do sniffer
    
    Args:
        processor_name (str): Nome do processador que identificou o pacote
        result (dict): Resultado do processamento
        data (bytes): Dados brutos do pacote
        addr (tuple): Endereço de origem (IP, porta)
    """
    try:
        # Log da detecção
        source_ip, source_port = addr
        
        # Loga informações básicas
        logger.info(f"Detecção: {processor_name} de {source_ip}:{source_port}")
        
        # Manipula diferentes tipos de detecção
        if result.get("type") == "player":
            _handle_player_detection(result)
        elif result.get("type") == "item":
            _handle_item_detection(result)
        elif result.get("type") == "combat":
            _handle_combat_detection(result)
        else:
            logger.info(f"Tipo desconhecido: {json.dumps(result, indent=2)}")
            
    except Exception as e:
        logger.error(f"Erro ao processar callback: {str(e)}")

def _handle_player_detection(result):
    """
    Processa detecções de jogadores
    
    Args:
        result (dict): Dados do jogador detectado
    """
    player_id = result.get("id")
    position = result.get("position", {})
    x, y = position.get("x", 0), position.get("y", 0)
    
    logger.info(f"Jogador detectado - ID: {player_id}, Posição: ({x:.1f}, {y:.1f})")
    
    # Aqui você pode implementar lógica adicional, como:
    # - Atualizar um mapa com a posição do jogador
    # - Verificar se é um jogador inimigo
    # - Enviar alertas para o usuário

def _handle_item_detection(result):
    """
    Processa detecções de itens
    
    Args:
        result (dict): Dados do item detectado
    """
    item_id = result.get("id")
    item_type = result.get("item_type")
    tier = result.get("tier")
    
    logger.info(f"Item detectado - ID: {item_id}, Tipo: {item_type}, Tier: {tier}")
    
    # Aqui você pode implementar lógica adicional, como:
    # - Atualizar um inventário de recursos visíveis
    # - Alertar sobre itens valiosos

def _handle_combat_detection(result):
    """
    Processa detecções de eventos de combate
    
    Args:
        result (dict): Dados do evento de combate detectado
    """
    attacker_id = result.get("attacker_id")
    target_id = result.get("target_id")
    damage = result.get("damage")
    
    logger.info(f"Combate detectado - Atacante: {attacker_id}, Alvo: {target_id}, Dano: {damage:.1f}")
    
    # Aqui você pode implementar lógica adicional, como:
    # - Calcular DPS
    # - Atualizar estatísticas de combate
    # - Detectar padrões de ataque 