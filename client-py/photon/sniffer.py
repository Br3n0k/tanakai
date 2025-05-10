import logging
import importlib.util

class PhotonSniffer:
    """
    Classe para sniffer de pacotes UDP Photon utilizados pelo Albion Online
    """
    def __init__(self, port=5056, callback=None):
        self.port = port
        self.running = False
        self.callback = callback
        self.packet_processors = {}
        self.logger = self._setup_logger()

    def _setup_logger(self):
        """Configura o logger para o sniffer"""
        logger = logging.getLogger("PhotonSniffer")
        logger.setLevel(logging.INFO)
        
        # Cria handler para console
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', 
                                     datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger

    def start(self):
        """Inicia o sniffer em uma thread separada"""
        if self.running:
            self.logger.warning("Sniffer já está em execução")
            return False
        
        try:
            # Se o Scapy estiver disponível, usa ele
            if self.use_scapy:
                return self._start_scapy_sniffer()
            else:
                # Caso contrário, usa o socket UDP padrão
                return self._start_socket_sniffer()
        except Exception as e:
            self.logger.error(f"Erro ao iniciar sniffer: {str(e)}")
            if self.socket:
                self.socket.close()
                self.socket = None
            self.running = False
            return False
        
    def stop(self):
        """Para o sniffer e libera recursos"""
        if not self.running:
            return
        
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None
        
        if self.socket:
            self.socket.close()
            self.socket = None
        
        self.logger.info("Sniffer encerrado")

