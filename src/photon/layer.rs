use anyhow::{Result, anyhow};
use byteorder::{ByteOrder, LittleEndian};
use log::{debug, warn};

use super::command::PhotonCommand;
use super::fragment_buffer::FragmentBuffer;

/// Tipos de comandos Photon
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum PhotonCommandType {
    Unreliable = 0,
    Reliable = 1,
    ReliableFragment = 2,
    Unknown = 255,
}

impl From<u8> for PhotonCommandType {
    fn from(value: u8) -> Self {
        match value {
            0 => PhotonCommandType::Unreliable,
            1 => PhotonCommandType::Reliable,
            2 => PhotonCommandType::ReliableFragment,
            _ => PhotonCommandType::Unknown,
        }
    }
}

/// Processa a camada Photon dos pacotes
pub struct PhotonLayer {
    fragment_buffer: FragmentBuffer,
}

impl PhotonLayer {
    pub fn new() -> Self {
        PhotonLayer {
            fragment_buffer: FragmentBuffer::new(),
        }
    }

    /// Processa um pacote Photon e extrai os comandos
    pub fn process_packet(&mut self, data: &[u8]) -> Result<Vec<PhotonCommand>> {
        if data.len() < 12 {
            return Err(anyhow!("Pacote Photon muito pequeno"));
        }

        // Verifica o cabeçalho do pacote Photon
        let peer_id = LittleEndian::read_u16(&data[0..2]);
        let flags = data[2];
        let command_count = data[3];
        
        // Pula o cabeçalho e processa os comandos
        let mut offset = 12;
        let mut commands = Vec::new();
        
        debug!("Processando pacote Photon: peer_id={}, flags={:x}, command_count={}", 
              peer_id, flags, command_count);
        
        for _ in 0..command_count {
            if offset >= data.len() {
                warn!("Offset maior que o tamanho dos dados ao processar comandos");
                break;
            }
            
            // Lê o tipo e tamanho do comando
            let command_type: PhotonCommandType = data[offset].into();
            let command_length = data[offset + 1] as usize;
            
            // Verifica se temos dados suficientes
            if offset + 2 + command_length > data.len() {
                warn!("Comando incompleto no pacote Photon");
                break;
            }
            
            let command_data = &data[offset + 2..offset + 2 + command_length];
            
            // Processa o comando com base no tipo
            match command_type {
                PhotonCommandType::Unreliable => {
                    if let Ok(command) = PhotonCommand::parse(command_data) {
                        commands.push(command);
                    }
                },
                PhotonCommandType::Reliable => {
                    if let Ok(command) = PhotonCommand::parse(command_data) {
                        commands.push(command);
                    }
                },
                PhotonCommandType::ReliableFragment => {
                    if command_data.len() < 16 {
                        warn!("Fragmento confiável muito pequeno");
                    } else {
                        // Processa o fragmento
                        let fragment_id = LittleEndian::read_u32(&command_data[0..4]);
                        let fragment_count = LittleEndian::read_u32(&command_data[4..8]);
                        let fragment_number = LittleEndian::read_u32(&command_data[8..12]);
                        let fragment_total_size = LittleEndian::read_u32(&command_data[12..16]);
                        
                        // Extrai os dados do fragmento
                        let fragment_data = &command_data[16..];
                        
                        // Adiciona o fragmento ao buffer
                        self.fragment_buffer.add_fragment(
                            fragment_id, 
                            fragment_count, 
                            fragment_number, 
                            fragment_total_size, 
                            fragment_data.to_vec()
                        );
                        
                        // Verifica se temos um comando completo
                        if let Some(complete_data) = self.fragment_buffer.get_complete_data(fragment_id) {
                            if let Ok(command) = PhotonCommand::parse(&complete_data) {
                                commands.push(command);
                            }
                        }
                    }
                },
                PhotonCommandType::Unknown => {
                    warn!("Tipo de comando Photon desconhecido: {}", data[offset]);
                }
            }
            
            // Avança para o próximo comando
            offset += 2 + command_length;
        }
        
        Ok(commands)
    }
} 