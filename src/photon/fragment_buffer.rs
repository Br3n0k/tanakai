use std::collections::HashMap;
use log::{debug, warn};

/// Estrutura para armazenamento e reconstrução de fragmentos de pacotes Photon
pub struct FragmentBuffer {
    /// Fragmentos armazenados por ID
    fragments: HashMap<u32, FragmentCollection>,
}

/// Coleção de fragmentos de um pacote
struct FragmentCollection {
    /// Total de fragmentos esperados
    fragment_count: u32,
    
    /// Tamanho total do pacote completo
    total_size: u32,
    
    /// Fragmentos recebidos, indexados pelo número do fragmento
    received_fragments: HashMap<u32, Vec<u8>>,
}

impl FragmentBuffer {
    pub fn new() -> Self {
        FragmentBuffer {
            fragments: HashMap::new(),
        }
    }

    /// Adiciona um fragmento ao buffer
    pub fn add_fragment(
        &mut self, 
        fragment_id: u32, 
        fragment_count: u32, 
        fragment_number: u32, 
        total_size: u32, 
        data: Vec<u8>
    ) {
        // Obtém ou cria a coleção de fragmentos
        let fragment_collection = self.fragments
            .entry(fragment_id)
            .or_insert_with(|| FragmentCollection {
                fragment_count,
                total_size,
                received_fragments: HashMap::new(),
            });

        // Atualiza os valores da coleção
        if fragment_collection.fragment_count != fragment_count {
            warn!("Contagem de fragmentos inconsistente para ID {}: esperado {}, recebido {}", 
                fragment_id, fragment_collection.fragment_count, fragment_count);
        }

        if fragment_collection.total_size != total_size {
            warn!("Tamanho total inconsistente para ID {}: esperado {}, recebido {}", 
                fragment_id, fragment_collection.total_size, total_size);
        }

        // Adiciona o fragmento à coleção
        fragment_collection.received_fragments.insert(fragment_number, data);

        debug!("Adicionado fragmento {} de {} para ID {}", 
            fragment_number, fragment_count, fragment_id);
    }

    /// Verifica se todos os fragmentos foram recebidos e retorna os dados completos
    pub fn get_complete_data(&mut self, fragment_id: u32) -> Option<Vec<u8>> {
        // Verifica se temos a coleção de fragmentos
        let collection = self.fragments.get(&fragment_id)?;
        
        // Verifica se todos os fragmentos foram recebidos
        if collection.received_fragments.len() != collection.fragment_count as usize {
            debug!("Aguardando por mais fragmentos: {}/{} para ID {}", 
                collection.received_fragments.len(), collection.fragment_count, fragment_id);
            return None;
        }

        // Monta os dados completos
        let mut complete_data = Vec::with_capacity(collection.total_size as usize);
        for i in 0..collection.fragment_count {
            if let Some(fragment_data) = collection.received_fragments.get(&i) {
                complete_data.extend_from_slice(fragment_data);
            } else {
                warn!("Fragmento {} não encontrado para ID {}", i, fragment_id);
                return None;
            }
        }

        // Remove a coleção de fragmentos do buffer
        self.fragments.remove(&fragment_id);
        
        debug!("Reconstruído pacote completo de {} bytes para ID {}", 
            complete_data.len(), fragment_id);
        
        Some(complete_data)
    }

    /// Limpa entradas antigas do buffer
    #[allow(dead_code)]
    pub fn clean_old_entries(&mut self) {
        // Aqui poderíamos implementar uma lógica para remover coleções de fragmentos
        // que estão incompletas por um período muito longo
    }
} 