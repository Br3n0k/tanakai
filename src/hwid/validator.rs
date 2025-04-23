use anyhow::Result;
use log::{debug, error, info, warn};
use reqwest::Client;
use serde::{Serialize, Deserialize};
use tokio::time::{timeout, Duration};

use crate::config;
use crate::hwid::{HwId, HardwareInfo};

/// Status de verificação do HWID
#[derive(Debug, Clone, PartialEq)]
pub enum HwIdStatus {
    /// Hardware válido e não banido
    Valid,
    
    /// Um ou mais componentes estão banidos
    Banned(Vec<BannedComponent>),
    
    /// Hardware registrado com sucesso
    Registered,
    
    /// Erro na verificação
    Error(String),
}

/// Componente banido
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct BannedComponent {
    /// Tipo de componente (motherboard, network, disk, gpu)
    pub component_type: String,
    
    /// Razão do banimento
    pub reason: String,
    
    /// Data do banimento
    pub banned_at: String,
}

/// Resposta da API de verificação
#[derive(Debug, Clone, Serialize, Deserialize)]
struct VerifyResponse {
    /// Status da verificação
    pub status: String,
    
    /// Mensagem detalhada
    pub message: String,
    
    /// Lista de componentes banidos (se houver)
    pub banned_components: Option<Vec<BannedComponent>>,
}

/// Requisição para registro de hardware
#[derive(Debug, Clone, Serialize, Deserialize)]
struct RegisterRequest {
    /// HWID completo
    pub hwid: HwId,
}

/// Verifica o estado do hardware na API
pub async fn verify_hardware(hardware_info: &HardwareInfo) -> Result<HwIdStatus> {
    let hwid = HwId::new(hardware_info);
    let client = Client::new();
    
    debug!("Verificando HWID: {}", hwid.to_string());
    
    // Verificação de saúde da API
    if !check_api_health(&client).await {
        let error_msg = "API indisponível, não foi possível verificar o hardware".to_string();
        error!("{}", error_msg);
        return Ok(HwIdStatus::Error(error_msg));
    }
    
    // Monta o endpoint de verificação
    let verify_url = config::get_api_url("/hwid/verify");
    
    // Prepara a requisição com um timeout
    let request_timeout = Duration::from_millis(config::CONFIG.read().unwrap().api_timeout_ms);
    
    // Envia a requisição
    let response = match timeout(request_timeout, client.post(&verify_url)
        .json(&hwid)
        .send()).await {
        Ok(result) => match result {
            Ok(response) => response,
            Err(e) => {
                let error_msg = format!("Erro ao enviar requisição: {}", e);
                error!("{}", error_msg);
                return Ok(HwIdStatus::Error(error_msg));
            }
        },
        Err(_) => {
            let error_msg = "Timeout ao verificar hardware".to_string();
            error!("{}", error_msg);
            return Ok(HwIdStatus::Error(error_msg));
        }
    };
    
    // Processa a resposta
    if response.status().is_success() {
        match response.json::<VerifyResponse>().await {
            Ok(verify_response) => {
                match verify_response.status.as_str() {
                    "valid" => {
                        info!("Hardware verificado com sucesso");
                        Ok(HwIdStatus::Valid)
                    },
                    "banned" => {
                        if let Some(banned_components) = verify_response.banned_components {
                            warn!("Hardware banido: {}", verify_response.message);
                            for component in &banned_components {
                                warn!("Componente banido: {} - Razão: {}", 
                                     component.component_type, component.reason);
                            }
                            Ok(HwIdStatus::Banned(banned_components))
                        } else {
                            error!("Resposta de banimento sem componentes especificados");
                            Ok(HwIdStatus::Error("Resposta de banimento inválida".to_string()))
                        }
                    },
                    "unknown" => {
                        info!("Hardware não registrado, tentando registrar...");
                        register_hardware(&hwid).await
                    },
                    _ => {
                        let error_msg = format!("Status desconhecido: {}", verify_response.status);
                        error!("{}", error_msg);
                        Ok(HwIdStatus::Error(error_msg))
                    }
                }
            },
            Err(e) => {
                let error_msg = format!("Erro ao processar resposta: {}", e);
                error!("{}", error_msg);
                Ok(HwIdStatus::Error(error_msg))
            }
        }
    } else {
        let error_msg = format!("Erro na requisição: {}", response.status());
        error!("{}", error_msg);
        Ok(HwIdStatus::Error(error_msg))
    }
}

/// Registra o hardware na API
pub async fn register_hardware(hwid: &HwId) -> Result<HwIdStatus> {
    let client = Client::new();
    
    // Monta o endpoint de registro
    let register_url = config::get_api_url("/hwid/register");
    
    // Prepara a requisição
    let request = RegisterRequest {
        hwid: hwid.clone(),
    };
    
    // Prepara a requisição com um timeout
    let request_timeout = Duration::from_millis(config::CONFIG.read().unwrap().api_timeout_ms);
    
    // Envia a requisição
    let response = match timeout(request_timeout, client.post(&register_url)
        .json(&request)
        .send()).await {
        Ok(result) => match result {
            Ok(response) => response,
            Err(e) => {
                let error_msg = format!("Erro ao enviar requisição de registro: {}", e);
                error!("{}", error_msg);
                return Ok(HwIdStatus::Error(error_msg));
            }
        },
        Err(_) => {
            let error_msg = "Timeout ao registrar hardware".to_string();
            error!("{}", error_msg);
            return Ok(HwIdStatus::Error(error_msg));
        }
    };
    
    // Processa a resposta
    if response.status().is_success() {
        info!("Hardware registrado com sucesso");
        Ok(HwIdStatus::Registered)
    } else {
        let error_msg = format!("Erro ao registrar hardware: {}", response.status());
        error!("{}", error_msg);
        Ok(HwIdStatus::Error(error_msg))
    }
}

/// Verifica a saúde da API
async fn check_api_health(client: &Client) -> bool {
    let health_url = config::get_api_url("/health");
    
    match client.get(&health_url).send().await {
        Ok(response) => response.status().is_success(),
        Err(_) => false,
    }
} 