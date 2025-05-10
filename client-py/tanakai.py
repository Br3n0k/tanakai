# Tanakai - Client
## Versão em python
import os
import signal
import sys
import time
import logging

# Impede criação dos arquivos de cache
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["PYTHONUNBUFFERED"] = "1"
sys.dont_write_bytecode = True

# Define o diretorio base do projeto
os.environ["TANAKAI_PY_CLIENT"] = os.path.dirname(os.path.abspath(__file__))

# Configurar logger principal
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Cria o logger principal
logger = logging.getLogger("Tanakai")

# Importações
from config import Config
from utils import (
    check_game_running, check_server_online, check_folder, 
    find_file, open_albion, close_albion,
    PacketSniffer, get_default_processors, handle_detection,
    check_and_prompt_npcap
)

# Variável global para o sniffer
sniffer = None

def main():
    
    
    
    # Carrega configurações
    config = Config()
    
    # Exibe a versão do cliente
    logger.info(f"Tanakai Client v{config.version}")

    # Verifica se o caminho do jogo está definido
    if not config.game_path:
        logger.info("Caminho do jogo não definido, por favor, defina-o agora (ex: C:\\Program Files (x86)\\AlbionOnline):")

        config.game_path = input("Caminho do jogo: ")

        if not check_folder(config.game_path):
            logger.error("Caminho do jogo inválido!")
            sys.exit(1)

        if not find_file(os.path.join(config.game_path, "game", config.game_executable)):
            logger.error("Executável do jogo inválido!")
            sys.exit(1)
        config.save_config()
        config.load_config()
    
    # Verifica se o servidor do Tanakai está definido
    if not config.server:
        logger.error("Servidor não definido.")
        sys.exit(1)

    # Verifica se o servidor do Tanakai está online
    if not check_server_online(config.server):
        logger.error("Servidor Tanakai não está respondendo!")
        sys.exit(1)

    # Verifica se o jogo está em execução
    if not check_game_running():
        open_albion(config.game_path)

    # Verifica se o Npcap está instalado
    logger.info("Verificando instalação do Npcap...")

    if not check_and_prompt_npcap():
        logger.error("O Npcap é necessário para a funcionalidade de captura de pacotes.")
        logger.error("Por favor, instale o Npcap e reinicie o Tanakai.")
        sys.exit(1)
    
    # Inicializa o sniffer e começa a escutar pacotes na porta 5056 UDP
    logger.info("Iniciando sniffer na porta UDP 5056...")

    # Obtém os processadores de pacotes padrão
    processors = get_default_processors()
    
    # Cria o sniffer com a função de callback
    sniffer = PacketSniffer(port=5056, callback=handle_detection)
    
    # Registra os processadores
    for name, processor_func in processors.items():
        sniffer.register_processor(name, processor_func)
    
    try:
        # Inicia o Sniffer
        sniffer.start()

        # Informa que o sniffer foi iniciado com sucesso
        logger.info("Sniffer iniciado com sucesso!")

        # Loop principal
        while True:
            # Verifica periodicamente se o jogo está rodando
            if not check_game_running():
                logger.warning("Albion Online foi fechado!")
                # Implementação futura: Tomar alguma ação quando o jogo for fechado
                
            # Dorme um pouco para não consumir CPU desnecessariamente
            time.sleep(5)
    except Exception as e:
        logger.error(f"Erro ao iniciar o sniffer: {str(e)}")
        sys.exit(1)
    
    finally:
        # Garante que o sniffer será encerrado corretamente
        if sniffer and sniffer.running:
            sniffer.stop()
            logger.info("Sniffer encerrado.")

if __name__ == "__main__":
    main()