use serde::{Serialize, Deserialize};

/// Estrutura para representar um jogador
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Player {
    /// ID único do jogador
    pub id: String,
    
    /// Nome do jogador
    pub name: String,
    
    /// Guilda do jogador (se houver)
    pub guild: Option<String>,
    
    /// Aliança do jogador (se houver)
    pub alliance: Option<String>,
    
    /// Pontuação ou nível do jogador
    pub fame: Option<u64>,
    
    /// Última localização conhecida
    pub location: Option<Location>,
    
    /// Equipamento visível
    pub equipment: Option<Equipment>,
}

/// Localização de um jogador
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Location {
    pub x: f32,
    pub y: f32,
    pub zone_id: Option<String>,
    pub zone_name: Option<String>,
}

/// Equipamento de um jogador
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Equipment {
    pub main_hand: Option<Item>,
    pub off_hand: Option<Item>,
    pub head: Option<Item>,
    pub chest: Option<Item>,
    pub shoes: Option<Item>,
    pub bag: Option<Item>,
    pub cape: Option<Item>,
    pub mount: Option<Item>,
}

/// Item de equipamento
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Item {
    pub item_id: String,
    pub quality: u8,
    pub enchantment: u8,
} 