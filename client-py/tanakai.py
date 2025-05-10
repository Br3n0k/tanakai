# Tanakai - Client
## Versão em python
import os
import sys
import time

# Impede criação dos arquivos de cache
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["PYTHONUNBUFFERED"] = "1"
sys.dont_write_bytecode = True

# Define o diretorio base do projeto
os.environ["TANAKAI_PY_CLIENT"] = os.path.dirname(os.path.abspath(__file__))

# Importações
from config import Config
from core.logger import Logger
from core.manager import ComponentManager
from core.handlers import SignalHandler
from core.system import check_and_prompt_npcap
from photon import (
    PhotonSniffer, 
    get_default_processors, 
    handle_detection
)

# Inicializa o logger principal
logger = Logger("Tanakai")

def main():
    # Carrega configurações
    config = Config()
    
    # Exibe a versão do cliente
    logger.info(f"Tanakai Client v{config.version}")

    # Verifica se o Npcap está instalado
    logger.info("Verificando instalação do Npcap...")

    if not check_and_prompt_npcap():
        logger.error("O Npcap é necessário para a funcionalidade de captura de pacotes.")
        logger.error("Por favor, instale o Npcap e reinicie o Tanakai.")
        sys.exit(1)
    
    # Inicializa o gerenciador de componentes
    manager = ComponentManager()
    
    # Inicializa o sniffer
    logger.info("Iniciando sniffer na porta UDP 5056...")
    sniffer = PhotonSniffer(port=5056, callback=handle_detection)
    
    # Registra os processadores de pacotes
    processors = get_default_processors()
    for name, processor_func in processors.items():
        sniffer.register_processor(name, processor_func)
    
    # Registra os componentes no gerenciador
    manager.register_component(sniffer)
    manager.register_component(SignalHandler(sniffer))
    
    try:
        # Inicia todos os componentes
        if not manager.start_all():
            logger.error("Falha ao iniciar componentes")
            sys.exit(1)
        
        logger.info("Sistema iniciado com sucesso!")
            
    except Exception as e:
        logger.error(f"Erro durante a execução: {str(e)}")
        sys.exit(1)
        
    finally:
        # Garante que todos os componentes serão encerrados
        manager.stop_all()
        logger.info("Sistema encerrado.")

if __name__ == "__main__":
    main()