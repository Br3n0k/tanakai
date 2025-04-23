use log::{debug, info};

use crate::models::PhotonEvent;
use crate::models::PhotonEventType;
use super::command::PhotonCommand;

/// Parser para eventos Photon
pub struct PhotonParser {
    quiet: bool,
}

impl PhotonParser {
    pub fn new(quiet: bool) -> Self {
        PhotonParser {
            quiet,
        }
    }

    /// Processa um comando Photon e gera eventos
    pub fn parse_command(&self, command: &PhotonCommand) -> Vec<PhotonEvent> {
        let mut events = Vec::new();
        
        // Implementação dos diferentes tipos de eventos com base no operation_code
        match command.operation_code {
            // Códigos de operação para movimentação de jogadores
            1 | 2 => {
                if let Some(event) = self.parse_player_movement(command) {
                    events.push(event);
                }
            },
            
            // Códigos de operação para ações de mercado
            10 | 11 | 12 => {
                if let Some(event) = self.parse_market_action(command) {
                    events.push(event);
                }
            },
            
            // Códigos de operação para ações de guilda
            20 | 21 => {
                if let Some(event) = self.parse_guild_action(command) {
                    events.push(event);
                }
            },
            
            // Outros códigos de operação
            _ => {
                if !self.quiet {
                    debug!("Código de operação não processado: {}", command.operation_code);
                }
            }
        }
        
        events
    }

    /// Processa eventos de movimentação de jogadores
    fn parse_player_movement(&self, command: &PhotonCommand) -> Option<PhotonEvent> {
        // Esta é uma implementação simplificada - precisaríamos detalhar com base na documentação
        let mut event = PhotonEvent::new(
            PhotonEventType::PlayerAppear, 
            command.operation_code, 
            command.channel_id
        );
        
        // Adicionamos alguns dados básicos
        if let Some(player_id) = command.get_string(1) {
            // Clonamos o valor antes de adicioná-lo ao evento para evitar o erro de movimento
            let id_clone = player_id.clone();
            let _ = event.add_data("player_id", id_clone);
            
            if !self.quiet {
                info!("Detectado movimento do jogador: {}", player_id);
            }
            
            return Some(event);
        }
        
        None
    }

    /// Processa ações de mercado
    fn parse_market_action(&self, command: &PhotonCommand) -> Option<PhotonEvent> {
        // Esta é uma implementação simplificada - precisaríamos detalhar com base na documentação
        let mut event = PhotonEvent::new(
            PhotonEventType::MarketUpdate, 
            command.operation_code, 
            command.channel_id
        );
        
        // Adicionamos alguns dados básicos
        if let Some(item_id) = command.get_int(1) {
            let _ = event.add_data("item_id", item_id);
            
            if let Some(price) = command.get_int(2) {
                let _ = event.add_data("price", price);
            }
            
            if !self.quiet {
                info!("Detectada atualização de mercado para item: {}", item_id);
            }
            
            return Some(event);
        }
        
        None
    }

    /// Processa ações de guilda
    fn parse_guild_action(&self, command: &PhotonCommand) -> Option<PhotonEvent> {
        // Esta é uma implementação simplificada - precisaríamos detalhar com base na documentação
        let mut event = PhotonEvent::new(
            PhotonEventType::GuildUpdate, 
            command.operation_code, 
            command.channel_id
        );
        
        // Adicionamos alguns dados básicos
        if let Some(guild_id) = command.get_string(1) {
            // Clonamos o valor antes de adicioná-lo ao evento para evitar o erro de movimento
            let id_clone = guild_id.clone();
            let _ = event.add_data("guild_id", id_clone);
            
            if !self.quiet {
                info!("Detectada ação da guilda: {}", guild_id);
            }
            
            return Some(event);
        }
        
        None
    }
} 