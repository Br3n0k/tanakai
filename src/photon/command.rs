use anyhow::{Result, anyhow};
use bytes::Bytes;
use byteorder::{ByteOrder, LittleEndian};
use std::collections::HashMap;
use log::debug;

/// Representa um comando Photon
#[derive(Debug, Clone)]
pub struct PhotonCommand {
    /// Código da operação
    pub operation_code: u8,
    
    /// Dados do comando
    pub parameters: HashMap<u8, Bytes>,
    
    /// ID do canal (opcional)
    pub channel_id: Option<u8>,
}

impl PhotonCommand {
    pub fn new(operation_code: u8, channel_id: Option<u8>) -> Self {
        PhotonCommand {
            operation_code,
            parameters: HashMap::new(),
            channel_id,
        }
    }

    /// Adiciona um parâmetro ao comando
    pub fn add_parameter(&mut self, key: u8, value: Bytes) {
        self.parameters.insert(key, value);
    }

    /// Obtém um parâmetro como um número inteiro
    pub fn get_int(&self, key: u8) -> Option<i32> {
        self.parameters.get(&key).map(|bytes| {
            if bytes.len() >= 4 {
                LittleEndian::read_i32(&bytes[..4])
            } else {
                0
            }
        })
    }

    /// Obtém um parâmetro como uma string
    pub fn get_string(&self, key: u8) -> Option<String> {
        self.parameters.get(&key).and_then(|bytes| {
            String::from_utf8(bytes.to_vec()).ok()
        })
    }

    /// Obtém um parâmetro como bytes
    #[allow(dead_code)]
    pub fn get_bytes(&self, key: u8) -> Option<&Bytes> {
        self.parameters.get(&key)
    }

    /// Parseia um comando Photon a partir de bytes
    pub fn parse(data: &[u8]) -> Result<Self> {
        if data.len() < 2 {
            return Err(anyhow!("Dados de comando insuficientes"));
        }

        let operation_code = data[0];
        let channel_id = if (data[1] & 0x80) != 0 {
            Some(data[1] & 0x7F)
        } else {
            None
        };

        let mut command = Self::new(operation_code, channel_id);
        
        // Parseia os parâmetros
        if data.len() > 2 {
            let parameters_data = &data[2..];
            // Lógica de parsing dos parâmetros
            // Aqui precisaríamos implementar mais detalhes baseados na documentação do protocolo Photon
            
            debug!("Parseando parâmetros de comando Photon: {} bytes", parameters_data.len());
            // Implementação simplificada para exemplo - na prática precisaríamos analisar cada tipo de parâmetro
            
            // Exemplo: dividir os dados em pares de chave-valor
            let mut index = 0;
            while index + 1 < parameters_data.len() {
                let param_key = parameters_data[index];
                let param_len = parameters_data[index + 1] as usize;
                
                if index + 2 + param_len <= parameters_data.len() {
                    let param_value = Bytes::copy_from_slice(&parameters_data[index + 2..index + 2 + param_len]);
                    command.add_parameter(param_key, param_value);
                }
                
                index += 2 + param_len;
            }
        }

        Ok(command)
    }
} 