use serde::{Serialize, Deserialize};

/// Estrutura para representar um item do mercado
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MarketItem {
    /// ID único do item
    pub item_id: String,
    
    /// Nome do item
    pub name: Option<String>,
    
    /// Qualidade do item (0-5)
    pub quality: u8,
    
    /// Nível de encantamento (0-4)
    pub enchantment: u8,
    
    /// Preço de venda
    pub sell_price: Option<u64>,
    
    /// Preço de compra
    pub buy_price: Option<u64>,
    
    /// Localização do mercado
    pub location: String,
    
    /// Timestamp da atualização
    pub timestamp: u64,
}

impl MarketItem {
    #[allow(dead_code)]
    pub fn new(item_id: String, quality: u8, enchantment: u8, location: String) -> Self {
        MarketItem {
            item_id,
            name: None,
            quality,
            enchantment,
            sell_price: None,
            buy_price: None,
            location,
            timestamp: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap_or_default()
                .as_millis() as u64,
        }
    }
} 