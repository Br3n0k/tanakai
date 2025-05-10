import os
import json

class Config:
    """
    Classe responsável por gerenciar as configurações do cliente Tanakai.
    Fornece informações sobre a versão, autor, descrição e configurações do jogo.
    """
    def __init__(self):
        """
        Inicializa a classe de configuração com valores padrão.
        """
        # Informações do cliente
        self.version = "1.0.0"
        self.author = "N0k"
        self.name = "Tanakai"
        self.description = "Albion Online Sniffer"
        self.server = "http://127.0.0.1:8000/"

        self.albion_online_port = 5056
        self.albion_executable = "Albion-Online.exe"
        self.albion_path = "C:\\Program Files (x86)\\AlbionOnline"


