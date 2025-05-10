import socket
import threading
import time
from abc import abstractmethod
from typing import Callable, Dict, Any, Tuple, Optional

from .base import BaseComponent

class BaseSniffer(BaseComponent):
    """
    Classe base para sniffers de rede.
    Fornece a estrutura básica para captura de pacotes independente de protocolo.
    """
    
    def __init__(self, name: str, port: int, callback: Optional[Callable] = None):
        """
        Inicializa o sniffer base.
        
        Args:
            name (str): Nome do sniffer
            port (int): Porta para captura
            callback (callable, optional): Função de callback para processar pacotes detectados
        """
        super().__init__(name)
        self.port = port
        self.callback = callback
        self.socket = None
        self.thread = None
        self.processors: Dict[str, Callable] = {}
    
    def register_processor(self, name: str, processor_func: Callable) -> None:
        """
        Registra um processador de pacotes.
        
        Args:
            name (str): Nome identificador do processador
            processor_func (callable): Função de processamento
        """
        self.processors[name] = processor_func
        self.logger.info(f"Processador '{name}' registrado")
    
    @abstractmethod
    def _process_packet(self, data: bytes, addr: Tuple) -> None:
        """
        Processa um pacote capturado.
        
        Args:
            data (bytes): Dados do pacote
            addr (tuple): Endereço de origem (IP, porta)
        """
        pass
    
    def start(self) -> bool:
        """
        Inicia a captura de pacotes.
        
        Returns:
            bool: True se iniciado com sucesso
        """
        if self._running:
            self.logger.warning("Sniffer já está em execução")
            return False
            
        try:
            self._running = True
            self._setup_socket()
            self.thread = threading.Thread(target=self._capture_loop)
            self.thread.daemon = True
            self.thread.start()
            self.logger.info(f"Sniffer iniciado na porta {self.port}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao iniciar sniffer: {str(e)}")
            self._cleanup()
            self._running = False
            return False
    
    def stop(self) -> bool:
        """
        Para a captura de pacotes.
        
        Returns:
            bool: True se parado com sucesso
        """
        if not self._running:
            return True
            
        try:
            self._running = False
            self._cleanup()
            self.logger.info("Sniffer encerrado")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao encerrar sniffer: {str(e)}")
            return False
    
    @abstractmethod
    def _setup_socket(self) -> None:
        """
        Configura o socket para captura.
        """
        pass
    
    @abstractmethod
    def _capture_loop(self) -> None:
        """
        Loop principal de captura de pacotes.
        """
        pass
    
    def _cleanup(self) -> None:
        """
        Limpa recursos utilizados pelo sniffer.
        """
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None
            
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None


class UDPSniffer(BaseSniffer):
    """
    Implementação de sniffer para captura de pacotes UDP.
    """
    
    def __init__(self, port: int, callback: Optional[Callable] = None):
        """
        Inicializa o sniffer UDP.
        
        Args:
            port (int): Porta UDP para captura
            callback (callable, optional): Função de callback para processamento
        """
        super().__init__("UDPSniffer", port, callback)
    
    def _setup_socket(self) -> None:
        """
        Configura o socket UDP para captura.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', self.port))
        self.socket.settimeout(1.0)
    
    def _capture_loop(self) -> None:
        """
        Loop principal de captura UDP.
        """
        self.logger.info("Loop de captura de pacotes UDP iniciado")
        
        while self._running and self.socket is not None:
            try:
                data, addr = self.socket.recvfrom(65535)
                self._process_packet(data, addr)
            except socket.timeout:
                # Timeout esperado para verificar self._running periodicamente
                pass
            except Exception as e:
                if self._running:
                    self.logger.error(f"Erro na captura: {str(e)}")
                    time.sleep(0.1)
    
    def _process_packet(self, data: bytes, addr: Tuple) -> None:
        """
        Processa um pacote UDP capturado.
        
        Args:
            data (bytes): Dados do pacote
            addr (tuple): Endereço de origem (IP, porta)
        """
        try:
            # Executa todos os processadores registrados
            for name, processor in self.processors.items():
                try:
                    result = processor(data, addr)
                    
                    # Se um processador retornar resultado, notifica via callback
                    if result and self.callback:
                        self.callback(name, result, data, addr)
                except Exception as e:
                    self.logger.error(f"Erro no processador '{name}': {str(e)}")
        except Exception as e:
            self.logger.error(f"Erro ao processar pacote: {str(e)}")


# Implementação opcional para Scapy (para uso futuro)
class ScapySniffer(BaseSniffer):
    """
    Implementação de sniffer usando Scapy para captura avançada.
    Requer que o pacote scapy esteja instalado.
    """
    
    def __init__(self, port: int, callback: Optional[Callable] = None):
        """
        Inicializa o sniffer Scapy.
        
        Args:
            port (int): Porta para captura
            callback (callable, optional): Função de callback para processamento
        """
        super().__init__("ScapySniffer", port, callback)
        self._scapy_available = self._check_scapy()
    
    def _check_scapy(self) -> bool:
        """
        Verifica se o Scapy está disponível.
        
        Returns:
            bool: True se disponível
        """
        try:
            import importlib.util
            return importlib.util.find_spec("scapy") is not None
        except ImportError:
            return False
    
    def start(self) -> bool:
        """
        Inicia o sniffer Scapy.
        
        Returns:
            bool: True se iniciado com sucesso
        """
        if not self._scapy_available:
            self.logger.error("Scapy não está disponível. Instale com: pip install scapy")
            return False
            
        return super().start()
    
    def _setup_socket(self) -> None:
        """
        Não precisa configurar socket, Scapy gerencia internamente.
        """
        pass
    
    def _capture_loop(self) -> None:
        """
        Loop de captura usando Scapy.
        """
        try:
            from scapy.all import sniff, UDP
            
            self.logger.info(f"Loop de captura Scapy iniciado na porta {self.port}")
            
            # Função de callback para o Scapy
            def packet_callback(packet):
                if not self._running:
                    return
                
                # Verifica se é pacote UDP na porta alvo
                if UDP in packet and (packet[UDP].dport == self.port or packet[UDP].sport == self.port):
                    try:
                        # Extrai dados do pacote
                        data = bytes(packet[UDP].payload)
                        addr = (packet.src, packet[UDP].sport)
                        
                        # Processa o pacote
                        self._process_packet(data, addr)
                    except Exception as e:
                        self.logger.error(f"Erro ao processar pacote: {str(e)}")
            
            # Inicia captura
            sniff(
                filter=f"udp port {self.port}",
                prn=packet_callback,
                store=0,
                stop_filter=lambda _: not self._running
            )
            
        except Exception as e:
            if self._running:
                self.logger.error(f"Erro no sniffer Scapy: {str(e)}")
                self._running = False 