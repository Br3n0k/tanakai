mod collector;
mod crypto;
mod validator;

pub use collector::{HardwareInfo, collect_hardware_info};
pub use crypto::encrypt_id;
pub use validator::{verify_hardware, HwIdStatus};

/// Representa um Token HWID completo
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct HwId {
    /// Identificador da placa-mãe
    pub motherboard: String,
    
    /// Identificador da placa de rede
    pub network: String,
    
    /// Identificador do disco rígido
    pub disk: String,
    
    /// Identificador da placa de vídeo
    pub gpu: String,
}

impl HwId {
    /// Cria um novo HWID a partir das informações de hardware
    pub fn new(hardware_info: &HardwareInfo) -> Self {
        HwId {
            motherboard: encrypt_id(&hardware_info.motherboard_id),
            network: encrypt_id(&hardware_info.network_id),
            disk: encrypt_id(&hardware_info.disk_id),
            gpu: encrypt_id(&hardware_info.gpu_id),
        }
    }
    
    /// Converte o HWID para formato de string
    pub fn to_string(&self) -> String {
        format!(
            "{}-{}-{}-{}", 
            self.motherboard, 
            self.network, 
            self.disk, 
            self.gpu
        )
    }
    
    /// Tenta converter uma string em HWID
    #[allow(dead_code)]
    pub fn from_string(s: &str) -> Option<Self> {
        let parts: Vec<&str> = s.split('-').collect();
        if parts.len() != 4 {
            return None;
        }
        
        Some(HwId {
            motherboard: parts[0].to_string(),
            network: parts[1].to_string(),
            disk: parts[2].to_string(),
            gpu: parts[3].to_string(),
        })
    }
} 