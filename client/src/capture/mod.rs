mod pcap_handler;

use anyhow::Result;
use log::{error, info, warn};
use tokio::sync::mpsc;

use crate::api::ApiClient;
use crate::config;
use crate::hwid::{self, HwIdStatus};
use crate::models::PhotonEvent;
use crate::utils;

/// Inicia a captura de pacotes
pub async fn start_capture(
    interface_name: Option<String>,
    api_url: String,
    quiet: bool,
) -> Result<()> {
    // Inicializa a configuração
    config::init_config(Some(api_url.clone()), quiet);
    
    // Verifica hardware e API
    let hardware_info = hwid::collect_hardware_info()?;
    let hwid_status = hwid::verify_hardware(&hardware_info).await?;
    
    match hwid_status {
        HwIdStatus::Valid | HwIdStatus::Registered => {
            if !quiet {
                info!("Hardware verificado com sucesso");
            }
        },
        HwIdStatus::Banned(components) => {
            error!("Este hardware está banido e não pode executar o Tanakai");
            for component in components {
                error!("Componente banido: {} - Razão: {}", 
                    component.component_type, component.reason);
            }
            return Err(anyhow::anyhow!("Hardware banido"));
        },
        HwIdStatus::Error(msg) => {
            warn!("Erro na verificação de hardware: {}", msg);
            warn!("Continuando em modo offline...");
        }
    }
    
    // Determina a interface de rede a ser usada
    let interface = match interface_name {
        Some(name) => name,
        None => {
            // Tenta encontrar a interface adequada
            let default_interface = utils::find_default_interface()?;
            default_interface.name
        }
    };
    
    if !quiet {
        info!("Iniciando captura na interface: {}", interface);
    }
    
    // Cria canais para comunicação entre threads
    let (tx, mut rx) = mpsc::channel::<PhotonEvent>(100);
    
    // Inicia o capturador em uma thread separada
    let capture_handle = tokio::spawn(async move {
        match pcap_handler::start_packet_capture(&interface, tx).await {
            Ok(_) => {
                if !quiet {
                    info!("Captura finalizada");
                }
            },
            Err(e) => {
                error!("Erro ao capturar pacotes: {}", e);
            }
        }
    });
    
    // Cria cliente da API
    let api_client = ApiClient::new(api_url, quiet);
    
    // Processa eventos recebidos
    while let Some(event) = rx.recv().await {
        // Tenta enviar para a API
        match api_client.send_event("photon", &event).await {
            Ok(_) => {
                if !quiet {
                    info!("Evento enviado com sucesso: {:?}", event.event_type);
                }
            },
            Err(e) => {
                if !quiet {
                    warn!("Erro ao enviar evento: {}", e);
                }
            }
        }
    }
    
    // Aguarda o término da captura
    if let Err(e) = capture_handle.await {
        error!("Erro ao aguardar thread de captura: {}", e);
    }
    
    Ok(())
} 