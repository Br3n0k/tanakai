import struct
import json
from typing import Dict, Any, Tuple, Optional, Callable

from core.base import BaseComponent

class PhotonPacketProcessor(BaseComponent):
    """
    Processador de pacotes Photon para o jogo Albion Online.
    Analisa e extrai informações dos pacotes UDP Photon.
    """
    
    # Tipos de pacotes Photon
    PACKET_TYPE_OPERATION_REQUEST = 2
    PACKET_TYPE_OPERATION_RESPONSE = 3
    PACKET_TYPE_EVENT = 4
    
    # Operações conhecidas
    OPERATION_JOIN = 255
    OPERATION_LEAVE = 254
    OPERATION_MOVE = 12
    
    # Eventos conhecidos
    EVENT_JOIN = 255
    EVENT_LEAVE = 254
    EVENT_SPAWN = 2
    
    def __init__(self):
        """
        Inicializa o processador de pacotes Photon.
        """
        super().__init__("PhotonPacketProcessor")
        self._processors: Dict[str, Callable] = {}
    
    def start(self) -> bool:
        """
        Inicializa o processador.
        
        Returns:
            bool: True sempre, pois não requer inicialização especial
        """
        self._running = True
        return True
    
    def stop(self) -> bool:
        """
        Para o processador.
        
        Returns:
            bool: True sempre, pois não requer limpeza especial
        """
        self._running = False
        return True
    
    def register_handler(self, packet_type: int, code: int, handler_func: Callable):
        """
        Registra uma função para processar um tipo específico de pacote.
        
        Args:
            packet_type (int): Tipo de pacote (2=OperationRequest, 3=OperationResponse, 4=Event)
            code (int): Código da operação ou evento
            handler_func (callable): Função que processa o pacote
        """
        key = f"{packet_type}_{code}"
        self._processors[key] = handler_func
        self.logger.info(f"Handler registrado para pacote tipo={packet_type}, código={code}")
    
    def process_packet(self, data: bytes, addr: Tuple) -> Optional[Dict[str, Any]]:
        """
        Processa um pacote Photon.
        
        Args:
            data (bytes): Dados do pacote
            addr (tuple): Endereço de origem (IP, porta)
            
        Returns:
            Optional[Dict[str, Any]]: Informações extraídas do pacote ou None se não for relevante
        """
        try:
            # Verifica se parece um pacote Photon válido
            if len(data) < 12:  # Tamanho mínimo do cabeçalho Photon
                return None
                
            # Extrai o tipo de pacote (byte 2)
            packet_type = data[2]
            
            # Processa com base no tipo
            if packet_type == self.PACKET_TYPE_OPERATION_REQUEST:
                return self._process_operation_request(data, addr)
            elif packet_type == self.PACKET_TYPE_OPERATION_RESPONSE:
                return self._process_operation_response(data, addr)
            elif packet_type == self.PACKET_TYPE_EVENT:
                return self._process_event(data, addr)
                
            return None
        
        except Exception as e:
            self.logger.error(f"Erro ao processar pacote Photon: {str(e)}")
            return None
    
    def _process_operation_request(self, data: bytes, addr: Tuple) -> Optional[Dict[str, Any]]:
        """
        Processa um pacote de requisição de operação.
        
        Args:
            data (bytes): Dados do pacote
            addr (tuple): Endereço de origem
            
        Returns:
            Optional[Dict[str, Any]]: Informações extraídas ou None
        """
        try:
            # O código de operação está no byte 12
            operation_code = data[12] if len(data) > 12 else 0
            
            # Chama o handler específico se existir
            key = f"{self.PACKET_TYPE_OPERATION_REQUEST}_{operation_code}"
            if key in self._processors:
                return self._processors[key](data, addr)
            
            # Processamento básico se não houver handler específico
            return {
                "type": "operation_request",
                "code": operation_code,
                "source": addr[0],
                "port": addr[1]
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao processar Operation Request: {str(e)}")
            return None
    
    def _process_operation_response(self, data: bytes, addr: Tuple) -> Optional[Dict[str, Any]]:
        """
        Processa um pacote de resposta de operação.
        
        Args:
            data (bytes): Dados do pacote
            addr (tuple): Endereço de origem
            
        Returns:
            Optional[Dict[str, Any]]: Informações extraídas ou None
        """
        try:
            # O código de operação está no byte 12
            operation_code = data[12] if len(data) > 12 else 0
            
            # Chama o handler específico se existir
            key = f"{self.PACKET_TYPE_OPERATION_RESPONSE}_{operation_code}"
            if key in self._processors:
                return self._processors[key](data, addr)
            
            # Processamento básico se não houver handler específico
            return {
                "type": "operation_response",
                "code": operation_code,
                "source": addr[0],
                "port": addr[1]
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao processar Operation Response: {str(e)}")
            return None
    
    def _process_event(self, data: bytes, addr: Tuple) -> Optional[Dict[str, Any]]:
        """
        Processa um pacote de evento.
        
        Args:
            data (bytes): Dados do pacote
            addr (tuple): Endereço de origem
            
        Returns:
            Optional[Dict[str, Any]]: Informações extraídas ou None
        """
        try:
            # O código de evento está no byte 12
            event_code = data[12] if len(data) > 12 else 0
            
            # Chama o handler específico se existir
            key = f"{self.PACKET_TYPE_EVENT}_{event_code}"
            if key in self._processors:
                return self._processors[key](data, addr)
            
            # Processamento básico se não houver handler específico
            return {
                "type": "event",
                "code": event_code,
                "source": addr[0],
                "port": addr[1]
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao processar Event: {str(e)}")
            return None 