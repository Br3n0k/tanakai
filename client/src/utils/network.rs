use anyhow::Result;
use pcap::{Device, Capture};
use log::{info, error};

/// Obtém a lista de interfaces de rede disponíveis
pub fn get_available_interfaces() -> Result<Vec<Device>> {
    match Device::list() {
        Ok(devices) => Ok(devices),
        Err(e) => {
            error!("Erro ao listar interfaces de rede: {}", e);
            Err(anyhow::anyhow!("Erro ao listar interfaces de rede: {}", e))
        }
    }
}

/// Encontra a interface padrão adequada para captura
pub fn find_default_interface() -> Result<Device> {
    let devices = get_available_interfaces()?;
    
    // Tenta encontrar uma interface não loopback que esteja ativa
    for device in &devices {
        // Verifica se a interface não é loopback usando nome ou descrição
        if !device.name.contains("loop") && !device.desc.as_deref().unwrap_or("").to_lowercase().contains("loopback") {
            info!("Selecionada interface padrão: {}", device.name);
            return Ok(device.clone());
        }
    }
    
    // Se não encontrar, usa a primeira disponível
    if let Some(device) = devices.first() {
        info!("Usando primeira interface disponível: {}", device.name);
        return Ok(device.clone());
    }
    
    error!("Nenhuma interface de rede encontrada");
    Err(anyhow::anyhow!("Nenhuma interface de rede encontrada"))
}

/// Cria um capturador na interface especificada
pub fn create_capture(interface_name: &str) -> Result<Capture<pcap::Active>> {
    // Cria o capturador
    let mut capture = Capture::from_device(interface_name)?
        .promisc(true)
        .snaplen(65535)
        .timeout(1000)
        .open()?;
    
    // Configura o filtro para pacotes UDP
    // Nota: precisamos ajustar esse filtro para pegar apenas pacotes Photon
    // Exemplo: porta 5056 é uma porta comum usada pelo Photon
    capture.filter("udp port 5056", true)?;
    
    Ok(capture)
}

/// Verifica se um pacote é um pacote Photon válido
pub fn is_photon_packet(data: &[u8]) -> bool {
    // Verifica o tamanho mínimo para um cabeçalho Photon
    if data.len() < 12 {
        return false;
    }
    
    // Verifica a assinatura do Photon (este é um exemplo simplificado, precisa ser ajustado)
    // Na verdade, precisamos conhecer melhor o formato específico do Photon usado pelo Albion
    let flags = data[2];
    let command_count = data[3];
    
    // Valores razoáveis para flags e contagem de comandos
    flags < 10 && command_count > 0 && command_count < 20
} 