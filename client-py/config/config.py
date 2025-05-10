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
        
        Args:
            config_file (str, optional): Caminho para o arquivo de configuração.
                                         Se não for especificado, usa o padrão.
        """
        # Informações do cliente
        self.version = "1.0.0"
        self.author = "N0k"
        self.name = "Tanakai"
        self.description = "Albion Online Sniffer"
        self.cfg_file = "config.tanakai"
        self.config_file = os.path.join( os.environ["TANAKAI_PY_CLIENT"],  self.cfg_file)

        # Verficia se o arquivo de configuração existe
        if not os.path.exists(self.config_file):
            self.set_config()
            self.save_config()

        # Carrega as configurações do arquivo de configuração
        self.load_config()

    def get_config(self):
        """
        Retorna as configurações do cliente como um dicionário.
        
        Returns:
            dict: Dicionário contendo todas as configurações
        """
        return {
            "game_executable": self.game_executable,
            "game_path": self.game_path,
            "server": self.server
        }

    def set_config(self):
        """
        Define as configurações padrão do cliente.
        """
        # Informações do servidor
        self.server = "http://127.0.0.1:8000/"
        
        
        # Configurações do jogo
        self.game_executable = "Albion-Online.exe"
        self.game_path = ""
    
    def save_config(self):
        """
        Salva as configurações atuais em um arquivo.
        """
        user_config = self.get_config()

        # Garante que o arquivo de configuração existe
        try:
            with open(self.config_file, 'w') as f:
                json.dump(user_config, f, indent=4)
            return True
        except Exception as e:
            print(f"Erro ao salvar configurações: {str(e)}")
            return False
    
    def load_config(self):
        """
        Carrega as configurações do arquivo JSON.
        Se o arquivo não existir ou ocorrer algum erro, mantém as configurações padrão.
        """
        if not os.path.exists(self.config_file):
            return False
            
        try:
            with open(self.config_file, 'r') as f:
                user_config = json.load(f)
                    
            if "game_path" in user_config:
                self.game_path = user_config["game_path"]

            if "game_executable" in user_config:
                self.game_executable = user_config["game_executable"]

            if "server" in user_config:
                self.server = user_config["server"]

            return True
        except Exception as e:
            print(f"Erro ao carregar configurações: {str(e)}")
            return False


