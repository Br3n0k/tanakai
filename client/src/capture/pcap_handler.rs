use anyhow::{Result, anyhow};
use log::{debug, error, info, warn};
use tokio::sync::mpsc::Sender;
use tokio::task;

use crate::config;
use crate::models::PhotonEvent;
use crate::photon::{PhotonLayer, PhotonParser};
use crate::utils;

/// Inicia a captura de pacotes em uma interface
pub async fn start_packet_capture(
    interface_name: &str,
    event_sender: Sender<PhotonEvent>,
) -> Result<()> {
    // Cria o capturador
    let mut capture = match utils::create_capture(interface_name) {
        Ok(cap) => cap,
        Err(e) => {
            error!("Falha ao criar capturador: {}", e);
            return Err(anyhow!("Falha ao criar capturador: {}", e));
        }
    };
    
    info!("Captura iniciada na interface: {}", interface_name);
    
    // Configura o Photon Layer para processamento de pacotes
    let mut photon_layer = PhotonLayer::new();
    
    // Configura o parser de eventos
    let photon_parser = PhotonParser::new(config::is_quiet_mode());
    
    // Executa a captura em uma thread de bloqueio separada
    let handle = task::spawn_blocking(move || -> Result<()> {
        loop {
            // Captura o próximo pacote
            match capture.next_packet() {
                Ok(packet) => {
                    // Verifica se é um pacote Photon válido
                    if utils::is_photon_packet(packet.data) {
                        debug!("Pacote Photon capturado: {} bytes", packet.data.len());
                        
                        // Processa o pacote Photon
                        match photon_layer.process_packet(packet.data) {
                            Ok(commands) => {
                                for command in commands {
                                    // Parseia comandos em eventos
                                    let events = photon_parser.parse_command(&command);
                                    
                                    // Envia eventos para processamento
                                    for event in events {
                                        if let Err(e) = event_sender.blocking_send(event) {
                                            warn!("Erro ao enviar evento: {}", e);
                                        }
                                    }
                                }
                            },
                            Err(e) => {
                                debug!("Erro ao processar pacote Photon: {}", e);
                            }
                        }
                    }
                },
                Err(pcap::Error::TimeoutExpired) => {
                    // Timeout normal, continua capturando
                    continue;
                },
                Err(e) => {
                    error!("Erro ao capturar pacote: {}", e);
                    break;
                }
            }
        }
        
        Ok(())
    });
    
    // Aguarda o resultado da captura
    match handle.await {
        Ok(result) => result,
        Err(e) => {
            error!("Erro na thread de captura: {}", e);
            Err(anyhow!("Erro na thread de captura: {}", e))
        }
    }
} 