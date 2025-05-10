from typing import Dict, Type
from .base import BaseComponent
from .logger import Logger

class ComponentManager:
    """
    Gerenciador central de componentes do sistema Tanakai.
    Responsável por inicializar, gerenciar e encerrar componentes.
    """
    
    def __init__(self):
        """
        Inicializa o gerenciador de componentes.
        """
        self.logger = Logger("ComponentManager")
        self._components: Dict[str, BaseComponent] = {}
    
    def register_component(self, component: BaseComponent) -> bool:
        """
        Registra um novo componente no gerenciador.
        
        Args:
            component (BaseComponent): Componente a ser registrado
            
        Returns:
            bool: True se registrado com sucesso, False caso contrário
        """
        if component.name in self._components:
            self.logger.error(f"Componente '{component.name}' já registrado")
            return False
        
        self._components[component.name] = component
        self.logger.info(f"Componente '{component.name}' registrado")
        return True
    
    def get_component(self, name: str) -> BaseComponent:
        """
        Obtém um componente pelo nome.
        
        Args:
            name (str): Nome do componente
            
        Returns:
            BaseComponent: Componente solicitado
            
        Raises:
            KeyError: Se o componente não for encontrado
        """
        if name not in self._components:
            raise KeyError(f"Componente '{name}' não encontrado")
        return self._components[name]
    
    def start_all(self) -> bool:
        """
        Inicia todos os componentes registrados.
        
        Returns:
            bool: True se todos iniciados com sucesso, False caso contrário
        """
        success = True
        for name, component in self._components.items():
            try:
                if component.start():
                    self.logger.info(f"Componente '{name}' iniciado")
                else:
                    self.logger.error(f"Falha ao iniciar componente '{name}'")
                    success = False
            except Exception as e:
                self.logger.error(f"Erro ao iniciar componente '{name}': {str(e)}")
                success = False
        return success
    
    def stop_all(self) -> bool:
        """
        Para todos os componentes registrados.
        
        Returns:
            bool: True se todos parados com sucesso, False caso contrário
        """
        success = True
        for name, component in self._components.items():
            try:
                if component.stop():
                    self.logger.info(f"Componente '{name}' parado")
                else:
                    self.logger.error(f"Falha ao parar componente '{name}'")
                    success = False
            except Exception as e:
                self.logger.error(f"Erro ao parar componente '{name}': {str(e)}")
                success = False
        return success
    
    def __enter__(self):
        """
        Suporte para uso com context manager (with statement)
        """
        self.start_all()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Suporte para uso com context manager (with statement)
        """
        self.stop_all() 