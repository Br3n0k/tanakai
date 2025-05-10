import os
import sys
import webbrowser
import logging
import platform
import importlib.util

# Configuração de logging
logger = logging.getLogger("TanakaiNpcap")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', 
                                 datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

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

def is_windows():
    """
    Verifica se o sistema operacional é Windows
    
    Returns:
        bool: True se for Windows, False caso contrário
    """
    return platform.system().lower() == "windows"

def is_linux():
    """
    Verifica se o sistema operacional é Linux
    
    Returns:
        bool: True se for Linux, False caso contrário
    """
    return platform.system().lower() == "linux"

def is_macos():
    """
    Verifica se o sistema operacional é macOS
    
    Returns:
        bool: True se for macOS, False caso contrário
    """
    return platform.system().lower() == "darwin"

def is_scapy_available():
    """
    Verifica se o Scapy está disponível
    
    Returns:
        bool: True se o Scapy estiver disponível, False caso contrário
    """
    try:
        return importlib.util.find_spec("scapy") is not None
    except ImportError:
        return False

def is_packet_capture_available():
    """
    Verifica se a biblioteca de captura de pacotes está disponível no sistema.
    Primeiro verifica o Scapy, depois as bibliotecas nativas.
    
    Returns:
        bool: True se alguma biblioteca estiver disponível, False caso contrário
    """
    # Primeiro verifica se o Scapy está disponível (funciona em todas as plataformas)
    if is_scapy_available():
        logger.info("Biblioteca Scapy encontrada para captura de pacotes")
        return True
    
    logger.info("Scapy não encontrado, verificando bibliotecas nativas...")
    
    # Se o Scapy não estiver disponível, verifica as bibliotecas nativas
    if is_windows():
        # No Windows, verifica se o Npcap está instalado
        return is_npcap_installed()
    elif is_linux():
        # No Linux, verifica se o libpcap está instalado
        return os.path.exists(LIBPCAP_SO_LINUX) or os.path.exists(LIBPCAP_A_LINUX)
    elif is_macos():
        # No macOS, verifica se o libpcap está instalado
        return os.path.exists(LIBPCAP_DYLIB_MAC)
    else:
        # Para outros sistemas, assume que não está disponível
        return False

def is_npcap_installed():
    """
    Verifica se o Npcap está instalado verificando a existência das DLLs necessárias
    
    Returns:
        bool: True se o Npcap estiver instalado, False caso contrário
    """
    if not is_windows():
        logger.warning("Verificação do Npcap só é suportada no Windows")
        return False
    
    # Verifica se o diretório Npcap existe
    if not os.path.isdir(NPCAP_DIR_WIN):
        logger.warning(f"Diretório Npcap não encontrado: {NPCAP_DIR_WIN}")
        return False
    
    # Verifica se as DLLs essenciais existem
    if not os.path.exists(NPCAP_WPCAP_DLL_WIN):
        logger.warning(f"DLL wpcap.dll não encontrada: {NPCAP_WPCAP_DLL_WIN}")
        return False
    
    if not os.path.exists(NPCAP_PACKET_DLL_WIN):
        logger.warning(f"DLL Packet.dll não encontrada: {NPCAP_PACKET_DLL_WIN}")
        return False
    
    # Se chegou até aqui, todas as verificações passaram
    logger.info("Npcap encontrado com todas as DLLs necessárias")
    return True

def open_npcap_download():
    """
    Abre a página de download do Npcap no navegador padrão
    """
    logger.info(f"Abrindo página de download do Npcap: {NPCAP_DOWNLOAD_URL}")
    webbrowser.open(NPCAP_DOWNLOAD_URL)

def check_and_prompt_npcap():
    """
    Verifica se alguma biblioteca de captura de pacotes está disponível 
    e, se não estiver, exibe instruções para instalação
    
    Returns:
        bool: True se alguma biblioteca estiver disponível, False caso contrário
    """
    if is_packet_capture_available():
        return True
    
    # Instrução comum para todas as plataformas
    print("\n" + "="*60)
    print("ATENÇÃO: Biblioteca de captura de pacotes não encontrada!")
    print("O Tanakai requer uma biblioteca de captura para funcionar corretamente.")
    
    # Se não estiver disponível, exibe uma mensagem específica para cada plataforma
    if is_windows():
        logger.error("Nenhuma biblioteca de captura de pacotes encontrada. Tentando instalar o Scapy...")
        
        # Tenta instalar o Scapy automaticamente
        try:
            print("Tentando instalar o Scapy automaticamente...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "scapy>=2.5.0"])
            print("Scapy instalado com sucesso!")
            print("Reinicie o Tanakai para usar a biblioteca instalada.")
            return False
        except Exception as e:
            logger.error(f"Falha ao instalar Scapy: {str(e)}")
            
            # Se falhar, sugere o Npcap
            logger.error("Redirecionando para a página de download do Npcap...")
            open_npcap_download()
            print("Não foi possível instalar o Scapy automaticamente.")
            print("Uma página de download do Npcap foi aberta no seu navegador.")
            print("Após instalar o Npcap, instale o Scapy com:")
            print("pip install scapy>=2.5.0")
            print("Reinicie o Tanakai após a instalação.")
    
    elif is_linux():
        print("No Linux, instale o libpcap e o Scapy com os seguintes comandos:")
        print("sudo apt-get install libpcap-dev  # Para distribuições baseadas em Debian/Ubuntu")
        print("sudo yum install libpcap-devel    # Para distribuições baseadas em RHEL/CentOS")
        print("pip install scapy>=2.5.0          # Para instalar o Scapy")
    
    elif is_macos():
        print("No macOS, instale o libpcap e o Scapy com os seguintes comandos:")
        print("brew install libpcap")
        print("pip install scapy>=2.5.0")
    
    else:
        print("Sistema operacional não reconhecido.")
        print("Tente instalar o Scapy manualmente com: pip install scapy>=2.5.0")
    
    print("="*60 + "\n")
    return False
