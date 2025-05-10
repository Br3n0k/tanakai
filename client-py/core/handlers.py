import sys
import signal
from asyncio.log import logger

class Handlers:
    def __init__(self, sniffer = None):

        # Define o sniffer
        self.sniffer = sniffer if sniffer else None

    # Registra o manipulador de sinais para CTRL+C (SIGINT) e SIGTERM
    def signal_handler(self):

        # Registra o manipulador de sinais para CTRL+C (SIGINT) e SIGTERM
        signal.signal(signal.SIGINT, self.sniffer_handler)
        signal.signal(signal.SIGTERM, self.sniffer_handler)

    def sniffer_handler(self, signum, frame):
        """
        Manipulador de sinal para encerramento limpo
        """
        logger.info("Sinal de encerramento recebido, encerrando...")
        
        # Para o sniffer se estiver rodando
        if self.sniffer and self.sniffer.running:
            self.sniffer.stop()
    
        # Encerra o programa
        sys.exit(0)