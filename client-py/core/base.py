from abc import ABC, abstractmethod
from .logger import Logger

class BaseComponent(ABC):
    """
    Classe base abstrata para componentes do sistema Tanakai.
    Fornece funcionalidades comuns como logging e gerenciamento de estado.
    """
    
    def __init__(self, name: str):
        """
        Inicializa o componente base.
        
        Args:
            name (str): Nome do componente para identificação
        """
        self.name = name
        self.logger = Logger(name)
        self._running = False
    
    @property
    def is_running(self) -> bool:
        """
        Verifica se o componente está em execução.
        
        Returns:
            bool: True se estiver rodando, False caso contrário
        """
        return self._running
    
    @abstractmethod
    def start(self) -> bool:
        """
        Inicia o componente.
        
        Returns:
            bool: True se iniciado com sucesso, False caso contrário
        """
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """
        Para o componente.
        
        Returns:
            bool: True se parado com sucesso, False caso contrário
        """
        pass
    
    def __enter__(self):
        """
        Suporte para uso com context manager (with statement)
        """
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Suporte para uso com context manager (with statement)
        """
        self.stop() 