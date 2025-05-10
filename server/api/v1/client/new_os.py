"""
Módulo responsável por obter um identificador único e imutável do sistema operacional.
Este identificador é usado para reconhecer a mesma instalação do sistema em diferentes execuções.
"""

import os
import platform
import subprocess
import uuid
import hashlib
import re
import json
from typing import Dict, Optional, Any

def get_windows_identifier() -> str:
    """
    Obtém identificador único do Windows usando informações do hardware e 
    do sistema que não mudam entre reinstalações ou atualizações.
    
    Returns:
        str: Hash único baseado em informações imutáveis do Windows
    """
    system_info = {}
    
    # Obtém o serial do disco rígido principal (C:)
    try:
        result = subprocess.run(
            ["wmic", "diskdrive", "get", "serialnumber"], 
            capture_output=True, 
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if result.returncode == 0:
            serial_numbers = re.findall(r'\b([A-Z0-9]{8,})\b', result.stdout)
            if serial_numbers:
                system_info["hdd_serial"] = serial_numbers[0]
    except Exception:
        pass
    
    # Obtém o serial da placa-mãe (BIOS)
    try:
        result = subprocess.run(
            ["wmic", "baseboard", "get", "serialnumber"], 
            capture_output=True, 
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if result.returncode == 0:
            serial_numbers = re.findall(r'\b([A-Z0-9]{6,})\b', result.stdout)
            if serial_numbers:
                system_info["mobo_serial"] = serial_numbers[0]
    except Exception:
        pass
    
    # Obtém o UUID da máquina
    try:
        result = subprocess.run(
            ["wmic", "csproduct", "get", "uuid"], 
            capture_output=True, 
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if result.returncode == 0:
            uuids = re.findall(r'\b([A-F0-9-]{36})\b', result.stdout)
            if uuids:
                system_info["machine_uuid"] = uuids[0]
    except Exception:
        pass
    
    # Obtém o endereço MAC da placa de rede principal
    try:
        result = subprocess.run(
            ["getmac", "/FO", "CSV", "/NH"], 
            capture_output=True, 
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if result.returncode == 0:
            macs = re.findall(r'([0-9A-F]{2}-[0-9A-F]{2}-[0-9A-F]{2}-[0-9A-F]{2}-[0-9A-F]{2}-[0-9A-F]{2})', result.stdout)
            if macs:
                system_info["mac_address"] = macs[0]
    except Exception:
        pass
    
    # Se não conseguiu obter informações suficientes, usa o ID da máquina do Windows
    if len(system_info) < 2:
        try:
            result = subprocess.run(
                ["reg", "query", "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Cryptography", "/v", "MachineGuid"], 
                capture_output=True, 
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                machine_guids = re.findall(r'([0-9a-f-]{36})', result.stdout.lower())
                if machine_guids:
                    system_info["machine_guid"] = machine_guids[0]
        except Exception:
            pass
    
    # Se ainda não tiver informações suficientes, gera um fallback
    if not system_info:
        system_info["fallback"] = str(uuid.getnode())
    
    # Cria um hash a partir das informações coletadas
    identifier = hashlib.sha256(json.dumps(system_info, sort_keys=True).encode()).hexdigest()
    return identifier

def get_linux_identifier() -> str:
    """
    Obtém identificador único do Linux usando informações do hardware e 
    do sistema que não mudam entre reinstalações ou atualizações.
    
    Returns:
        str: Hash único baseado em informações imutáveis do Linux
    """
    system_info = {}
    
    # Obtém o serial do disco rígido principal
    try:
        result = subprocess.run(
            ["lsblk", "--nodeps", "-no", "SERIAL"], 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            system_info["hdd_serial"] = result.stdout.strip().split("\n")[0]
    except Exception:
        pass
    
    # Obtém o serial do processador
    try:
        with open("/proc/cpuinfo", "r") as f:
            cpuinfo = f.read()
            serial_match = re.search(r"Serial\s+:\s+([0-9a-f]+)", cpuinfo)
            if serial_match:
                system_info["cpu_serial"] = serial_match.group(1)
    except Exception:
        pass
    
    # Obtém o UUID da máquina
    try:
        result = subprocess.run(
            ["cat", "/sys/class/dmi/id/product_uuid"], 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            system_info["machine_uuid"] = result.stdout.strip()
    except Exception:
        pass
    
    # Obtém o serial da placa-mãe
    try:
        result = subprocess.run(
            ["cat", "/sys/class/dmi/id/board_serial"], 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            system_info["mobo_serial"] = result.stdout.strip()
    except Exception:
        pass
    
    # Obtém o endereço MAC da placa de rede
    try:
        for interface in os.listdir("/sys/class/net"):
            if interface == "lo":  # Pula a interface de loopback
                continue
            try:
                with open(f"/sys/class/net/{interface}/address", "r") as f:
                    mac = f.read().strip()
                    if mac and len(mac) >= 17:  # Formato típico: 00:11:22:33:44:55
                        system_info["mac_address"] = mac
                        break
            except Exception:
                continue
    except Exception:
        pass
    
    # Se não conseguiu obter informações suficientes, usa o ID da máquina do Linux
    if len(system_info) < 2:
        try:
            result = subprocess.run(
                ["cat", "/etc/machine-id"], 
                capture_output=True, 
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                system_info["machine_id"] = result.stdout.strip()
        except Exception:
            pass
    
    # Se ainda não tiver informações suficientes, gera um fallback
    if not system_info:
        system_info["fallback"] = str(uuid.getnode())
    
    # Cria um hash a partir das informações coletadas
    identifier = hashlib.sha256(json.dumps(system_info, sort_keys=True).encode()).hexdigest()
    return identifier

def get_mac_identifier() -> str:
    """
    Obtém identificador único do macOS usando informações do hardware e 
    do sistema que não mudam entre reinstalações ou atualizações.
    
    Returns:
        str: Hash único baseado em informações imutáveis do macOS
    """
    system_info = {}
    
    # Obtém o serial do hardware (SerialNumber)
    try:
        result = subprocess.run(
            ["system_profiler", "SPHardwareDataType"], 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            serial_match = re.search(r"Serial Number[^:]*:\s*([^\n]+)", result.stdout)
            if serial_match:
                system_info["hw_serial"] = serial_match.group(1).strip()
            
            uuid_match = re.search(r"Hardware UUID[^:]*:\s*([^\n]+)", result.stdout)
            if uuid_match:
                system_info["hw_uuid"] = uuid_match.group(1).strip()
    except Exception:
        pass
    
    # Obtém o UUID do sistema
    try:
        result = subprocess.run(
            ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"], 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            uuid_match = re.search(r'"IOPlatformUUID"\s*=\s*"([^"]+)"', result.stdout)
            if uuid_match:
                system_info["platform_uuid"] = uuid_match.group(1)
    except Exception:
        pass
    
    # Obtém o endereço MAC da placa de rede
    try:
        result = subprocess.run(
            ["ifconfig", "en0"], 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            mac_match = re.search(r"ether\s+([0-9a-f:]{17})", result.stdout)
            if mac_match:
                system_info["mac_address"] = mac_match.group(1)
    except Exception:
        pass
    
    # Se não conseguiu obter informações suficientes, usa o ID da máquina do macOS
    if len(system_info) < 2:
        try:
            result = subprocess.run(
                ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"], 
                capture_output=True, 
                text=True
            )
            if result.returncode == 0:
                id_match = re.search(r'"IOPlatformSerialNumber"\s*=\s*"([^"]+)"', result.stdout)
                if id_match:
                    system_info["platform_serial"] = id_match.group(1)
        except Exception:
            pass
    
    # Se ainda não tiver informações suficientes, gera um fallback
    if not system_info:
        system_info["fallback"] = str(uuid.getnode())
    
    # Cria um hash a partir das informações coletadas
    identifier = hashlib.sha256(json.dumps(system_info, sort_keys=True).encode()).hexdigest()
    return identifier

def get_system_identifier() -> Dict[str, Any]:
    """
    Obtém um identificador único e imutável para o sistema operacional atual.
    
    Returns:
        Dict[str, Any]: Um dicionário contendo o identificador único e informações do sistema
    """
    system = platform.system().lower()
    
    if system == "windows":
        identifier = get_windows_identifier()
    elif system == "linux":
        identifier = get_linux_identifier()
    elif system == "darwin":  # macOS
        identifier = get_mac_identifier()
    else:
        # Fallback para sistemas não reconhecidos
        identifier = hashlib.sha256(str(uuid.getnode()).encode()).hexdigest()
    
    # Retorna um dicionário com o identificador e informações do sistema
    return {
        "identifier": identifier,
        "system": {
            "name": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "node": platform.node(),
            "platform": platform.platform()
        }
    }

def get_identifier() -> str:
    """
    Função simplificada que retorna apenas o identificador único em formato de string.
    
    Returns:
        str: Identificador único do sistema
    """
    return get_system_identifier()["identifier"]

# Teste direto se o arquivo for executado
if __name__ == "__main__":
    # Obtém o identificador completo com informações do sistema
    info = get_system_identifier()
    
    # Imprime as informações em formato JSON
    print(json.dumps(info, indent=4))
    
    # Imprime apenas o identificador
    print(f"\nIdentificador único do sistema: {info['identifier']}")
