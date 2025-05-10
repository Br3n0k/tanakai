import logging
import importlib.util
from typing import Callable, Dict, Any, Tuple, Optional
from core.sniffer import UDPSniffer
from .packet_processor import PhotonPacketProcessor

class PhotonSniffer(UDPSniffer):
    """
    Sniffer especializado para captura e processamento de pacotes Photon do Albion Online.
    """
    
    def __init__(self, port: int = 5056, callback: Optional[Callable] = None):
        """
        Inicializa o sniffer Photon.
        
        Args:
            port (int): Porta UDP (padrão 5056 para Albion Online)
            callback (callable, optional): Função de callback para processamento de pacotes detectados
        """
        super().__init__(port, callback)
        self.name = "PhotonSniffer"  # Sobrescreve o nome definido na classe base
        self.photon_processor = PhotonPacketProcessor()
    
    def start(self) -> bool:
        """
        Inicia o sniffer Photon.
        
        Returns:
            bool: True se iniciado com sucesso
        """
        # Inicia o processador de pacotes Photon
        self.photon_processor.start()
        
        # Inicia o sniffer UDP
        return super().start()
    
    def stop(self) -> bool:
        """
        Para o sniffer Photon.
        
        Returns:
            bool: True se parado com sucesso
        """
        # Para o processador Photon
        self.photon_processor.stop()
        
        # Para o sniffer UDP
        return super().stop()
    
    def _process_packet(self, data: bytes, addr: Tuple) -> None:
        """
        Processa um pacote capturado usando o processador Photon.
        
        Args:
            data (bytes): Dados do pacote
            addr (tuple): Endereço de origem (IP, porta)
        """
        try:
            # Processa o pacote através do processador Photon
            result = self.photon_processor.process_packet(data, addr)
            
            # Se tiver resultado e callback, notifica
            if result and self.callback:
                self.callback("photon", result, data, addr)
                
            # Executa também os processadores registrados diretamente
            for name, processor in self.processors.items():
                try:
                    processor_result = processor(data, addr)
                    
                    # Se um processador retornar resultado, notifica via callback
                    if processor_result and self.callback:
                        self.callback(name, processor_result, data, addr)
                except Exception as e:
                    self.logger.error(f"Erro no processador '{name}': {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Erro ao processar pacote Photon: {str(e)}")
    
    def register_photon_handler(self, packet_type: int, code: int, handler_func: Callable) -> None:
        """
        Registra um handler para um tipo específico de pacote Photon.
        
        Args:
            packet_type (int): Tipo de pacote (2=Request, 3=Response, 4=Event)
            code (int): Código da operação ou evento
            handler_func (callable): Função que processa o pacote
        """
        self.photon_processor.register_handler(packet_type, code, handler_func)

