import psutil
from config import Config

def check_game_running():
    """
    Verifica se o jogo Albion Online está em execução.
    
    Returns:
        bool: True se o jogo estiver rodando, False caso contrário
    """
    config = Config()
    game_executable = config.get_config()['game_executable']
    
    # Método usando psutil (se disponível)
    try:
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                # Verifica se o nome do processo contém o nome do executável (case insensitive)
                if game_executable.lower() in proc.info['name'].lower():
                     return True
                    
                # Em alguns casos, o caminho completo do executável é mais confiável
                if proc.info['exe'] and game_executable.lower() in proc.info['exe'].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    except Exception as e:
        raise Exception(f"Psutil Failed: {e}")

    return False

