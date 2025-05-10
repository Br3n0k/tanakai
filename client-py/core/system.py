import os
import sys
import platform
import webbrowser
import importlib.util
import subprocess
from typing import Optional

from .base import BaseComponent
from .logger import Logger

# Logger para o módulo
logger = Logger("SystemUtils")

# Constantes
NPCAP_DOWNLOAD_URL = "https://npcap.com/#download"
NPCAP_DIR_WIN = r"C:\Windows\System32\Npcap"
NPCAP_WPCAP_DLL_WIN = os.path.join(NPCAP_DIR_WIN, "wpcap.dll")
NPCAP_PACKET_DLL_WIN = os.path.join(NPCAP_DIR_WIN, "Packet.dll")

# Caminhos Linux (libpcap)
LIBPCAP_SO_LINUX = "/usr/lib/libpcap.so.1"
LIBPCAP_A_LINUX = "/usr/lib/libpcap.a"

# Caminhos macOS
LIBPCAP_DYLIB_MAC = "/usr/lib/libpcap.dylib"

class SystemUtils(BaseComponent):
    """
    Classe para funções utilitárias relacionadas ao sistema.
    Fornece métodos para verificar o ambiente de execução e gerenciar dependências.
    """
    
    def __init__(self):
        """
        Inicializa o módulo de utilidades do sistema.
        """
        super().__init__("SystemUtils")
    
    def start(self) -> bool:
        """
        Inicializa o componente (não faz nada específico neste caso).
        
        Returns:
            bool: True sempre, pois não requer inicialização
        """
        self._running = True
        return True
    
    def stop(self) -> bool:
        """
        Finaliza o componente (não faz nada específico neste caso).
        
        Returns:
            bool: True sempre, pois não requer finalização
        """
        self._running = False
        return True
    
    def is_windows(self) -> bool:
        """
        Verifica se o sistema operacional é Windows.
        
        Returns:
            bool: True se for Windows, False caso contrário
        """
        return platform.system().lower() == "windows"
    
    def is_linux(self) -> bool:
        """
        Verifica se o sistema operacional é Linux.
        
        Returns:
            bool: True se for Linux, False caso contrário
        """
        return platform.system().lower() == "linux"
    
    def is_macos(self) -> bool:
        """
        Verifica se o sistema operacional é macOS.
        
        Returns:
            bool: True se for macOS, False caso contrário
        """
        return platform.system().lower() == "darwin"
    
    def is_scapy_available(self) -> bool:
        """
        Verifica se o Scapy está disponível.
        
        Returns:
            bool: True se o Scapy estiver disponível, False caso contrário
        """
        try:
            return importlib.util.find_spec("scapy") is not None
        except ImportError:
            return False
    
    def is_packet_capture_available(self) -> bool:
        """
        Verifica se alguma biblioteca de captura de pacotes está disponível.
        
        Returns:
            bool: True se alguma biblioteca estiver disponível
        """
        # Verifica o Scapy primeiro
        if self.is_scapy_available():
            self.logger.info("Biblioteca Scapy encontrada para captura de pacotes")
            return True
        
        self.logger.info("Scapy não encontrado, verificando bibliotecas nativas...")
        
        # Verifica bibliotecas nativas
        if self.is_windows():
            return self.is_npcap_installed()
        elif self.is_linux():
            return os.path.exists(LIBPCAP_SO_LINUX) or os.path.exists(LIBPCAP_A_LINUX)
        elif self.is_macos():
            return os.path.exists(LIBPCAP_DYLIB_MAC)
        
        return False
    
    def is_npcap_installed(self) -> bool:
        """
        Verifica se o Npcap está instalado.
        
        Returns:
            bool: True se o Npcap estiver instalado
        """
        if not self.is_windows():
            self.logger.warning("Verificação do Npcap só é suportada no Windows")
            return False
        
        # Verifica se o diretório e DLLs existem
        if not os.path.isdir(NPCAP_DIR_WIN):
            self.logger.warning(f"Diretório Npcap não encontrado: {NPCAP_DIR_WIN}")
            return False
        
        if not os.path.exists(NPCAP_WPCAP_DLL_WIN):
            self.logger.warning(f"DLL wpcap.dll não encontrada: {NPCAP_WPCAP_DLL_WIN}")
            return False
        
        if not os.path.exists(NPCAP_PACKET_DLL_WIN):
            self.logger.warning(f"DLL Packet.dll não encontrada: {NPCAP_PACKET_DLL_WIN}")
            return False
        
        self.logger.info("Npcap encontrado com todas as DLLs necessárias")
        return True
    
    def open_npcap_download(self) -> None:
        """
        Abre a página de download do Npcap no navegador padrão.
        """
        self.logger.info(f"Abrindo página de download do Npcap: {NPCAP_DOWNLOAD_URL}")
        webbrowser.open(NPCAP_DOWNLOAD_URL)
    
    def install_scapy(self) -> bool:
        """
        Tenta instalar o Scapy automaticamente.
        
        Returns:
            bool: True se instalado com sucesso
        """
        try:
            self.logger.info("Tentando instalar o Scapy automaticamente...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "scapy>=2.5.0"])
            self.logger.info("Scapy instalado com sucesso!")
            return True
        except Exception as e:
            self.logger.error(f"Falha ao instalar Scapy: {str(e)}")
            return False
    
    def check_and_prompt_npcap(self) -> bool:
        """
        Verifica se alguma biblioteca de captura está disponível e orienta o usuário se não estiver.
        
        Returns:
            bool: True se alguma biblioteca estiver disponível
        """
        if self.is_packet_capture_available():
            return True
        
        # Exibe mensagem para o usuário
        print("\n" + "="*60)
        print("ATENÇÃO: Biblioteca de captura de pacotes não encontrada!")
        print("O Tanakai requer uma biblioteca de captura para funcionar corretamente.")
        
        # Tenta resolver o problema com base no sistema operacional
        if self.is_windows():
            if self.install_scapy():
                print("Reinicie o Tanakai para usar a biblioteca instalada.")
                return False
            
            # Se falhar, orienta a instalar o Npcap
            self.open_npcap_download()
            print("Não foi possível instalar o Scapy automaticamente.")
            print("Uma página de download do Npcap foi aberta no seu navegador.")
            print("Após instalar o Npcap, instale o Scapy com:")
            print("pip install scapy>=2.5.0")
        
        elif self.is_linux():
            print("No Linux, instale o libpcap e o Scapy com os seguintes comandos:")
            print("sudo apt-get install libpcap-dev  # Para distribuições baseadas em Debian/Ubuntu")
            print("sudo yum install libpcap-devel    # Para distribuições baseadas em RHEL/CentOS")
            print("pip install scapy>=2.5.0          # Para instalar o Scapy")
        
        elif self.is_macos():
            print("No macOS, instale o libpcap e o Scapy com os seguintes comandos:")
            print("brew install libpcap")
            print("pip install scapy>=2.5.0")
        
        else:
            print("Sistema operacional não reconhecido.")
            print("Tente instalar o Scapy manualmente com: pip install scapy>=2.5.0")
        
        print("Reinicie o Tanakai após a instalação.")
        print("="*60 + "\n")
        return False


# Função auxiliar para facilitar o uso
def check_and_prompt_npcap() -> bool:
    """
    Função auxiliar que verifica se as bibliotecas de captura estão disponíveis.
    
    Returns:
        bool: True se alguma biblioteca estiver disponível
    """
    utils = SystemUtils()
    return utils.check_and_prompt_npcap() 