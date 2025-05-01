use once_cell::sync::Lazy;
use std::sync::RwLock;
use std::path::PathBuf;
use serde::{Deserialize, Serialize};
use semver::Version;

/// Configurações da aplicação
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    /// URL base da API
    pub api_url: String,
    
    /// URL do repositório GitHub
    pub github_repo: String,
    
    /// Versão atual da aplicação
    pub version: String,
    
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
    
    /// Caminho para os ícones
    pub icons_path: PathBuf,
    
    /// Tema da aplicação
    pub theme: ThemeConfig,
}

/// Configuração do tema
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ThemeConfig {
    /// Nome do tema
    pub name: String,
    
    /// Cores do tema
    pub colors: ThemeColors,
    
    /// Estilos do tema
    pub styles: ThemeStyles,
}

/// Cores do tema
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ThemeColors {
    pub primary: String,
    pub secondary: String,
    pub background: String,
    pub surface: String,
    pub text: String,
    pub accent: String,
    pub error: String,
    pub warning: String,
    pub success: String,
}

/// Estilos do tema
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ThemeStyles {
    pub font_family: String,
    pub font_size: f32,
    pub border_radius: f32,
    pub padding: f32,
    pub margin: f32,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            api_url: "http://api.noktech.com.br/tanakai".to_string(),
            github_repo: "https://github.com/Br3n0k/tanakai".to_string(),
            version: env!("CARGO_PKG_VERSION").to_string(),
            photon_port: 5056,
            api_timeout_ms: 5000,
            health_check_interval_ms: 60000,
            quiet_mode: false,
            icons_path: PathBuf::from("assets/icons"),
            theme: ThemeConfig::default(),
        }
    }
}

impl Default for ThemeConfig {
    fn default() -> Self {
        Self {
            name: "cyberpunk".to_string(),
            colors: ThemeColors::default(),
            styles: ThemeStyles::default(),
        }
    }
}

impl Default for ThemeColors {
    fn default() -> Self {
        Self {
            primary: "#00ff00".to_string(),
            secondary: "#ff00ff".to_string(),
            background: "#000000".to_string(),
            surface: "#1a1a1a".to_string(),
            text: "#ffffff".to_string(),
            accent: "#00ffff".to_string(),
            error: "#ff0000".to_string(),
            warning: "#ffff00".to_string(),
            success: "#00ff00".to_string(),
        }
    }
}

impl Default for ThemeStyles {
    fn default() -> Self {
        Self {
            font_family: "Consolas".to_string(),
            font_size: 14.0,
            border_radius: 4.0,
            padding: 8.0,
            margin: 8.0,
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
    
    // Carrega o tema
    if let Err(e) = load_theme() {
        log::error!("Erro ao carregar tema: {}", e);
    }
}

/// Carrega o tema da aplicação
fn load_theme() -> anyhow::Result<()> {
    let mut config = CONFIG.write().unwrap();
    let theme_path = config.icons_path.join("theme");
    
    // Carrega as cores
    let colors_path = theme_path.join("colors.json");
    if colors_path.exists() {
        let colors: ThemeColors = serde_json::from_str(&std::fs::read_to_string(colors_path)?)?;
        config.theme.colors = colors;
    }
    
    // Carrega os estilos
    let styles_path = theme_path.join("styles.json");
    if styles_path.exists() {
        let styles: ThemeStyles = serde_json::from_str(&std::fs::read_to_string(styles_path)?)?;
        config.theme.styles = styles;
    }
    
    Ok(())
}

/// Verifica se há uma nova versão disponível
pub async fn check_for_updates() -> anyhow::Result<bool> {
    let config = CONFIG.read().unwrap();
    let current_version = Version::parse(&config.version)?;
    
    // Obtém a última versão do GitHub
    let client = reqwest::Client::new();
    let response = client
        .get(&format!("{}/releases/latest", config.github_repo))
        .header("User-Agent", "Tanakai")
        .send()
        .await?;
    
    if response.status().is_success() {
        let response_text = response.text().await?;
        let latest_version = response_text
            .split("tag_name")
            .nth(1)
            .and_then(|s| s.split('"').nth(2))
            .ok_or_else(|| anyhow::anyhow!("Não foi possível obter a versão mais recente"))?;
        
        let latest_version = Version::parse(latest_version)?;
        
        Ok(latest_version > current_version)
    } else {
        Err(anyhow::anyhow!("Erro ao verificar atualizações"))
    }
}

/// Obtém a URL completa da API
pub fn get_api_url(endpoint: &str) -> String {
    let config = CONFIG.read().unwrap();
    format!("{}/{}", config.api_url, endpoint)
}

/// Obtém a porta UDP do Photon
pub fn get_photon_port() -> u16 {
    let config = CONFIG.read().unwrap();
    config.photon_port
}

/// Verifica se o modo silencioso está ativo
pub fn is_quiet_mode() -> bool {
    let config = CONFIG.read().unwrap();
    config.quiet_mode
}

/// Obtém o caminho completo para um ícone
pub fn get_icon_path(name: &str) -> PathBuf {
    let config = CONFIG.read().unwrap();
    config.icons_path.join(name)
} 