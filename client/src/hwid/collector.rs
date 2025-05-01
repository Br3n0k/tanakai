use anyhow::Result;
use log::{debug, error, info};
use sysinfo::{System, SystemExt, DiskExt, ComponentExt, NetworkExt, CpuExt};
use std::fmt;

/// Informações de hardware coletadas
#[derive(Debug, Clone)]
pub struct HardwareInfo {
    /// Identificador da placa-mãe
    pub motherboard_id: String,
    
    /// Identificador da placa de rede
    pub network_id: String,
    
    /// Identificador do disco rígido
    pub disk_id: String,
    
    /// Identificador da placa de vídeo
    pub gpu_id: String,
}

impl fmt::Display for HardwareInfo {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "Hardware Info:\n")?;
        write!(f, "  Placa-mãe: {}\n", self.motherboard_id)?;
        write!(f, "  Placa de rede: {}\n", self.network_id)?;
        write!(f, "  Disco: {}\n", self.disk_id)?;
        write!(f, "  GPU: {}", self.gpu_id)
    }
}

/// Coleta informações de hardware do sistema
pub fn collect_hardware_info() -> Result<HardwareInfo> {
    // Inicializa o sistema para coleta de informações
    let mut sys = System::new_all();
    sys.refresh_all();
    
    debug!("Coletando informações de hardware...");
    
    // Obtém informações da placa-mãe
    let motherboard_id = get_motherboard_info(&sys)?;
    
    // Obtém informações da placa de rede
    let network_id = get_network_info(&sys)?;
    
    // Obtém informações do disco
    let disk_id = get_disk_info(&sys)?;
    
    // Obtém informações da GPU
    let gpu_id = get_gpu_info(&sys)?;
    
    let info = HardwareInfo {
        motherboard_id,
        network_id,
        disk_id,
        gpu_id,
    };
    
    info!("Informações de hardware coletadas com sucesso");
    debug!("{}", info);
    
    Ok(info)
}

/// Obtém informações da placa-mãe
fn get_motherboard_info(sys: &System) -> Result<String> {
    // Sysinfo não fornece diretamente informações da placa-mãe
    // Usamos uma combinação de informações disponíveis
    
    let hostname = sys.host_name().unwrap_or_else(|| "unknown".to_string());
    let os_version = sys.os_version().unwrap_or_else(|| "unknown".to_string());
    let kernel_version = sys.kernel_version().unwrap_or_else(|| "unknown".to_string());
    
    // Usamos CPU como parte da identificação da placa-mãe
    let cpu_info = sys.global_cpu_info().brand().to_string();
    
    let motherboard_id = format!("{}:{}:{}:{}", hostname, os_version, kernel_version, cpu_info);
    
    Ok(motherboard_id)
}

/// Obtém informações da placa de rede
fn get_network_info(sys: &System) -> Result<String> {
    let mut network_info = String::new();
    
    for (interface_name, data) in sys.networks() {
        let mac = data.mac_address().to_string();
        if !mac.is_empty() && mac != "00:00:00:00:00:00" {
            network_info = format!("{}:{}", interface_name, mac);
            break;
        }
    }
    
    if network_info.is_empty() {
        network_info = "unknown_network".to_string();
        error!("Não foi possível encontrar interfaces de rede com MAC válido");
    }
    
    Ok(network_info)
}

/// Obtém informações do disco
fn get_disk_info(sys: &System) -> Result<String> {
    let mut disk_info = String::new();
    
    // Tenta encontrar o disco de boot
    for disk in sys.disks() {
        if disk.is_removable() {
            continue;
        }
        
        let mount_point = disk.mount_point().to_string_lossy();
        let name = disk.name().to_string_lossy();
        let total_space = disk.total_space();
        
        // Prioriza o disco do sistema (C: no Windows, / no Linux/Mac)
        if mount_point == "/" || mount_point.contains("C:") {
            disk_info = format!("{}:{}:{}", name, mount_point, total_space);
            break;
        }
        
        // Se não encontramos ainda, guardamos essa informação
        if disk_info.is_empty() {
            disk_info = format!("{}:{}:{}", name, mount_point, total_space);
        }
    }
    
    if disk_info.is_empty() {
        disk_info = "unknown_disk".to_string();
        error!("Não foi possível encontrar informações de disco");
    }
    
    Ok(disk_info)
}

/// Obtém informações da GPU
fn get_gpu_info(sys: &System) -> Result<String> {
    // Sysinfo não fornece diretamente informações da GPU
    // Podemos usar os componentes para ter algumas informações
    
    let mut gpu_info = String::new();
    
    for component in sys.components() {
        let name = component.label();
        if name.contains("GPU") || name.contains("Graphics") {
            gpu_info = format!("{}:{}", name, component.temperature());
            break;
        }
    }
    
    // Caso não encontremos via componentes, podemos usar uma abordagem diferente
    // No caso real, usaríamos uma biblioteca mais específica para obter essas informações
    
    if gpu_info.is_empty() {
        #[cfg(target_os = "windows")]
        {
            // No Windows, podemos tentar outras abordagens
            // Aqui seria uma implementação mais complexa usando WMI, por exemplo
            gpu_info = "windows_gpu".to_string();
        }
        
        #[cfg(not(target_os = "windows"))]
        {
            gpu_info = "unknown_gpu".to_string();
        }
    }
    
    Ok(gpu_info)
} 