use serde::{Serialize, Deserialize};
use std::collections::HashMap;

/// Tipo de evento Photon
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum PhotonEventType {
    PlayerAppear,
    PlayerDisappear,
    MarketUpdate,
    GuildUpdate,
    CombatEvent,
    Unknown,
}

/// Estrutura para representar um evento Photon
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PhotonEvent {
    /// Tipo de evento
    pub event_type: PhotonEventType,
    
    /// Timestamp do evento (em milissegundos)
    pub timestamp: u64,
    
    /// Dados do evento
    pub data: HashMap<String, serde_json::Value>,
    
    /// ID da operação Photon
    pub operation_code: u8,
    
    /// ID do canal 
    pub channel_id: Option<u8>,
}

impl PhotonEvent {
    pub fn new(event_type: PhotonEventType, operation_code: u8, channel_id: Option<u8>) -> Self {
        PhotonEvent {
            event_type,
            timestamp: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap_or_default()
                .as_millis() as u64,
            data: HashMap::new(),
            operation_code,
            channel_id,
        }
    }
    
    pub fn add_data<T: Serialize>(&mut self, key: &str, value: T) -> Result<(), serde_json::Error> {
        let json_value = serde_json::to_value(value)?;
        self.data.insert(key.to_string(), json_value);
        Ok(())
    }
} 