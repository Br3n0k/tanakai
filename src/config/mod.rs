use once_cell::sync::Lazy;
use std::sync::RwLock;

/// Configurações da aplicação
#[derive(Debug, Clone)]
pub struct Config {
    /// URL base da API
    pub api_url: String,
    
    /// Porta UDP utilizada pelo Photon
    #[allow(dead_code)]
    pub photon_port: u16,
    
    /// Tempo de timeout para requisições (ms)
    pub api_timeout_ms: u64,
    
    /// Intervalo para verificação de saúde da API (ms)
    #[allow(dead_code)]
    pub health_check_interval_ms: u64,
    
    /// Habilitar modo discreto
    pub quiet_mode: bool,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            api_url: "http://api.noktech.com.br/tanakai".to_string(),
            photon_port: 5056,
            api_timeout_ms: 5000,
            health_check_interval_ms: 60000,
            quiet_mode: false,
        }
    }
}

/// Configuração global da aplicação
pub static CONFIG: Lazy<RwLock<Config>> = Lazy::new(|| {
    RwLock::new(Config::default())
});

/// Inicializa a configuração da aplicação
pub fn init_config(api_url: Option<String>, quiet_mode: bool) {
    let mut config = CONFIG.write().unwrap();
    
    if let Some(url) = api_url {
        config.api_url = url;
    }
    
    config.quiet_mode = quiet_mode;
}

/// Obtém a URL completa para um endpoint específico
pub fn get_api_url(endpoint: &str) -> String {
    let config = CONFIG.read().unwrap();
    format!("{}/{}", config.api_url, endpoint.trim_start_matches('/'))
}

/// Obtém a porta Photon configurada
#[allow(dead_code)]
pub fn get_photon_port() -> u16 {
    CONFIG.read().unwrap().photon_port
}

/// Obtém a configuração de modo silencioso
pub fn is_quiet_mode() -> bool {
    CONFIG.read().unwrap().quiet_mode
} 