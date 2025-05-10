import sys
import signal
from .base import BaseComponent

class SignalHandler(BaseComponent):
    """
    Componente responsável por gerenciar sinais do sistema.
    """
    
    def __init__(self, sniffer = None):
        """
        Inicializa o manipulador de sinais.
        
        Args:
            sniffer: Instância do sniffer a ser gerenciada
        """
        super().__init__("SignalHandler")
        self.sniffer = sniffer
    
    def start(self) -> bool:
        """
        Inicia o manipulador de sinais.
        
        Returns:
            bool: True se iniciado com sucesso, False caso contrário
        """
        try:
            signal.signal(signal.SIGINT, self.sniffer_handler)
            signal.signal(signal.SIGTERM, self.sniffer_handler)
            self._running = True
            self.logger.info("Handlers de sinal registrados")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao registrar handlers: {str(e)}")
            return False
    
    def stop(self) -> bool:
        """
        Para o manipulador de sinais.
        
        Returns:
            bool: True se parado com sucesso, False caso contrário
        """
        try:
            # Restaura os handlers padrão
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            self._running = False
            self.logger.info("Handlers de sinal restaurados")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao restaurar handlers: {str(e)}")
            return False
    
    def sniffer_handler(self, signum, frame):
        """
        Manipulador de sinal para encerramento limpo
        
        Args:
            signum: Número do sinal recebido
            frame: Frame atual da execução
        """
        self.logger.info("Sinal de encerramento recebido, encerrando...")
        
        # Para o sniffer se estiver rodando
        if self.sniffer and self.sniffer.is_running:
            self.sniffer.stop()
            self.logger.info("Sniffer encerrado com sucesso")
    
        # Encerra o programa
        sys.exit(0)
    
    def register_sniffer(self, sniffer):
        """
        Registra um novo sniffer para ser gerenciado
        
        Args:
            sniffer: Instância do sniffer a ser gerenciada
        """
        self.sniffer = sniffer
        self.logger.info("Novo sniffer registrado")