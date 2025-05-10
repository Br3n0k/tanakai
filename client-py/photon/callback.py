import json
from typing import Dict, Any, Optional

from core.logger import Logger
from core.base import BaseComponent

# Logger para o módulo
logger = Logger("PhotonCallback")

class PhotonCallback(BaseComponent):
    """
    Classe para manipular callbacks de pacotes Photon.
    Processa os resultados dos processadores de pacotes e executa ações apropriadas.
    """
    
    def __init__(self):
        """
        Inicializa o manipulador de callbacks.
        """
        super().__init__("PhotonCallback")
    
    def start(self) -> bool:
        """
        Inicializa o componente (não faz nada específico neste caso).
        
        Returns:
            bool: True sempre, pois não requer inicialização
        """
        self._running = True
        return True
    
    def stop(self) -> bool:
        """
        Finaliza o componente (não faz nada específico neste caso).
        
        Returns:
            bool: True sempre, pois não requer finalização
        """
        self._running = False
        return True
    
    def handle_detection(self, processor_name: str, result: Dict[str, Any], data: bytes, addr: tuple) -> None:
        """
        Função de callback para processar detecções do sniffer.
        
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
            self.logger.info(f"Detecção: {processor_name} de {source_ip}:{source_port}")
            
            # Manipula diferentes tipos de detecção
            if result.get("type") == "player":
                self._handle_player_detection(result)
            elif result.get("type") == "item":
                self._handle_item_detection(result)
            elif result.get("type") == "combat":
                self._handle_combat_detection(result)
            else:
                self.logger.info(f"Tipo desconhecido: {json.dumps(result, indent=2)}")
                
        except Exception as e:
            self.logger.error(f"Erro ao processar callback: {str(e)}")
    
    def _handle_player_detection(self, result: Dict[str, Any]) -> None:
        """
        Processa detecções de jogadores.
        
        Args:
            result (dict): Dados do jogador detectado
        """
        player_id = result.get("id")
        position = result.get("position", {})
        x, y = position.get("x", 0), position.get("y", 0)
        
        self.logger.info(f"Jogador detectado - ID: {player_id}, Posição: ({x:.1f}, {y:.1f})")
        
        # Aqui você pode implementar lógica adicional, como:
        # - Atualizar um mapa com a posição do jogador
        # - Verificar se é um jogador inimigo
        # - Enviar alertas para o usuário
    
    def _handle_item_detection(self, result: Dict[str, Any]) -> None:
        """
        Processa detecções de itens.
        
        Args:
            result (dict): Dados do item detectado
        """
        item_id = result.get("id")
        item_type = result.get("item_type")
        tier = result.get("tier")
        
        self.logger.info(f"Item detectado - ID: {item_id}, Tipo: {item_type}, Tier: {tier}")
        
        # Aqui você pode implementar lógica adicional, como:
        # - Atualizar um inventário de recursos visíveis
        # - Alertar sobre itens valiosos
    
    def _handle_combat_detection(self, result: Dict[str, Any]) -> None:
        """
        Processa detecções de eventos de combate.
        
        Args:
            result (dict): Dados do evento de combate detectado
        """
        attacker_id = result.get("attacker_id")
        target_id = result.get("target_id")
        damage = result.get("damage")
        
        self.logger.info(f"Combate detectado - Atacante: {attacker_id}, Alvo: {target_id}, Dano: {damage:.1f}")
        
        # Aqui você pode implementar lógica adicional, como:
        # - Calcular DPS
        # - Atualizar estatísticas de combate
        # - Detectar padrões de ataque


# Função auxiliar para facilitar o uso
def handle_detection(processor_name: str, result: Dict[str, Any], data: bytes, addr: tuple) -> None:
    """
    Função auxiliar para manipular detecções.
    
    Args:
        processor_name (str): Nome do processador que identificou o pacote
        result (dict): Resultado do processamento
        data (bytes): Dados brutos do pacote
        addr (tuple): Endereço de origem (IP, porta)
    """
    callback = PhotonCallback()
    callback.handle_detection(processor_name, result, data, addr) 