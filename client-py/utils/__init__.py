"""
Utilitários gerais para o cliente Tanakai.
"""

# Funções específicas para o jogo Albion Online
from .functions import check_folder, find_file

# Re-exportações das funções movidas para os novos módulos
from core.system import check_and_prompt_npcap
from photon.processors import get_default_processors
from photon.callback import handle_detection

__all__ = [
    "check_folder",
    "find_file",
    "get_default_processors",
    "handle_detection",
    "check_and_prompt_npcap"
]