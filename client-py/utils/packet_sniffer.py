import socket
import threading
import json
import time
import logging
import importlib.util

class PacketSniffer:
    """
    Implementação do sniffer de pacotes UDP para o Tanakai.
    Monitora tráfego na porta 5056 e processa pacotes de interesse.
    """
    def __init__(self, port=5056, callback=None):
        """
        Inicializa o sniffer de pacotes.
        
        Args:
            port (int): Porta UDP para escutar (padrão: 5056)
            callback (callable): Função a ser chamada quando um pacote de interesse for identificado
        """
        self.port = port
        self.running = False
        self.socket = None
        self.thread = None
        self.callback = callback
        self.packet_processors = {}
        self.logger = self._setup_logger()
        self.use_scapy = self._check_scapy_available()
        
    def _check_scapy_available(self):
        """
        Verifica se o Scapy está disponível para uso
        
        Returns:
            bool: True se o Scapy estiver disponível, False caso contrário
        """
        try:
            return importlib.util.find_spec("scapy") is not None
        except ImportError:
            return False
    
    def _setup_logger(self):
        """Configura o logger para o sniffer"""
        logger = logging.getLogger("TanakaiSniffer")
        logger.setLevel(logging.INFO)
        
        # Cria handler para console
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', 
                                     datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def register_processor(self, name, processor_func):
        """
        Registra uma função de processamento para tipos específicos de pacotes
        
        Args:
            name (str): Nome identificador do processador
            processor_func (callable): Função que processa os pacotes
        """
        self.packet_processors[name] = processor_func
        self.logger.info(f"Processador de pacotes '{name}' registrado")
    
    def start(self):
        """Inicia o sniffer em uma thread separada"""
        if self.running:
            self.logger.warning("Sniffer já está em execução")
            return False
        
        try:
            # Se o Scapy estiver disponível, usa ele
            if self.use_scapy:
                return self._start_scapy_sniffer()
            else:
                # Caso contrário, usa o socket UDP padrão
                return self._start_socket_sniffer()
        except Exception as e:
            self.logger.error(f"Erro ao iniciar sniffer: {str(e)}")
            if self.socket:
                self.socket.close()
                self.socket = None
            self.running = False
            return False
    
    def _start_scapy_sniffer(self):
        """
        Inicia o sniffer usando a biblioteca Scapy
        
        Returns:
            bool: True se iniciado com sucesso, False caso contrário
        """
        try:
            # Importa Scapy aqui para não ter erro se não estiver instalado
            from scapy.all import sniff
            
            self.running = True
            self.thread = threading.Thread(target=self._run_scapy_sniffer)
            self.thread.daemon = True
            self.thread.start()
            
            self.logger.info(f"Sniffer Scapy iniciado na porta UDP {self.port}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao iniciar sniffer Scapy: {str(e)}")
            self.running = False
            return False
    
    def _start_socket_sniffer(self):
        """
        Inicia o sniffer usando sockets UDP padrão
        
        Returns:
            bool: True se iniciado com sucesso, False caso contrário
        """
        try:
            # Cria um socket UDP
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind(('0.0.0.0', self.port))
            self.socket.settimeout(1.0)  # Timeout de 1 segundo para permitir encerramento suave
            
            self.running = True
            self.thread = threading.Thread(target=self._run_socket_sniffer)
            self.thread.daemon = True
            self.thread.start()
            
            self.logger.info(f"Sniffer Socket iniciado na porta UDP {self.port}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao iniciar sniffer Socket: {str(e)}")
            if self.socket:
                self.socket.close()
                self.socket = None
            self.running = False
            return False
    
    def stop(self):
        """Para o sniffer e libera recursos"""
        if not self.running:
            return
        
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None
        
        if self.socket:
            self.socket.close()
            self.socket = None
        
        self.logger.info("Sniffer encerrado")
    
    def _run_scapy_sniffer(self):
        """
        Loop principal do sniffer usando Scapy 
        (executado em thread separada)
        """
        try:
            from scapy.all import sniff, UDP
            
            self.logger.info("Loop de captura Scapy iniciado")
            
            # Função de callback para o Scapy
            def packet_callback(packet):
                if not self.running:
                    return
                
                # Verifica se é um pacote UDP na porta alvo
                if UDP in packet and (packet[UDP].dport == self.port or packet[UDP].sport == self.port):
                    try:
                        # Extrai os dados do pacote
                        data = bytes(packet[UDP].payload)
                        addr = (packet.src, packet[UDP].sport)
                        
                        # Processa o pacote
                        self._process_packet(data, addr)
                    except Exception as e:
                        self.logger.error(f"Erro ao processar pacote Scapy: {str(e)}")
            
            # Inicia a captura 
            # Nota: o parâmetro 'stop_filter' permite parar a captura quando self.running for False
            sniff(
                filter=f"udp port {self.port}",
                prn=packet_callback,
                store=0,
                stop_filter=lambda _: not self.running
            )
            
        except Exception as e:
            if self.running:  # Só loga erro se ainda estiver rodando
                self.logger.error(f"Erro no sniffer Scapy: {str(e)}")
                self.running = False
    
    def _run_socket_sniffer(self):
        """
        Loop principal do sniffer usando socket padrão 
        (executado em thread separada)
        """
        self.logger.info("Loop de captura Socket iniciado")
        
        while self.running and self.socket is not None:
            try:
                # Recebe dados do socket com timeout
                data, addr = self.socket.recvfrom(65535)
                
                # Tenta processar o pacote
                self._process_packet(data, addr)
                
            except socket.timeout:
                # Timeout é esperado e usado para verificar periodicamente self.running
                pass
            except Exception as e:
                if self.running:  # Só loga erro se ainda estiver rodando
                    self.logger.error(f"Erro ao capturar pacote Socket: {str(e)}")
                    time.sleep(0.1)  # Pequena pausa para evitar consumo excessivo de CPU
    
    def _process_packet(self, data, addr):
        """
        Processa um pacote recebido, chamando os processadores registrados
        
        Args:
            data (bytes): Dados do pacote recebido
            addr (tuple): Endereço da origem (IP, porta)
        """
        try:
            # Registra o recebimento do pacote (versão de depuração)
            # self.logger.debug(f"Pacote recebido de {addr[0]}:{addr[1]} ({len(data)} bytes)")
            
            # Executa todos os processadores de pacotes registrados
            for name, processor in self.packet_processors.items():
                try:
                    result = processor(data, addr)
                    
                    # Se um processador retornar um resultado, notifica via callback
                    if result and self.callback:
                        self.callback(name, result, data, addr)
                except Exception as e:
                    self.logger.error(f"Erro no processador '{name}': {str(e)}")
        
        except Exception as e:
            self.logger.error(f"Erro ao processar pacote: {str(e)}") 