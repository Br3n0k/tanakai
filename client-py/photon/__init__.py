"""
Módulo Photon - Implementação para comunicação com o protocolo Photon usado pelo Albion Online.
"""

from .sniffer import PhotonSniffer
from .packet_processor import PhotonPacketProcessor
from .processors import (
    get_default_processors,
    process_player_detection,
    process_item_detection,
    process_combat_detection
)
from .callback import PhotonCallback, handle_detection

# Constantes de tipo de pacote
PACKET_TYPE_OPERATION_REQUEST = 2
PACKET_TYPE_OPERATION_RESPONSE = 3
PACKET_TYPE_EVENT = 4

__all__ = [
    "PhotonSniffer", 
    "PhotonPacketProcessor",
    "PhotonCallback",
    "get_default_processors",
    "process_player_detection",
    "process_item_detection", 
    "process_combat_detection",
    "handle_detection",
    "PACKET_TYPE_OPERATION_REQUEST",
    "PACKET_TYPE_OPERATION_RESPONSE",
    "PACKET_TYPE_EVENT"
]
