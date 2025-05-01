use std::sync::mpsc::{self, Receiver};
use tray_icon::{
    menu::{Menu, MenuEvent, MenuItem},
    TrayIconBuilder,
};
use tray_icon::icon::Icon;
use log::{error, info};
use open;
use anyhow::Result;
use std::thread::JoinHandle;
use std::path::{Path, PathBuf};
use std::env;

use crate::config;
use crate::hwid;

/// Ações que podem ser enviadas da bandeja para a aplicação principal
#[derive(Debug, Clone)]
pub enum TrayAction {
    /// Mostrar informações sobre o app
    ShowInfo,
    /// Restaurar a janela principal
    Restore,
    /// Sair do aplicativo
    Exit,
}

/// Inicia o ícone na bandeja do sistema.
/// 
/// Retorna um receiver para ações da bandeja.
pub fn start_tray_icon() -> Result<Receiver<TrayAction>> {
    // Canal para enviar ações da bandeja para a aplicação principal
    let (tx, rx) = mpsc::channel();
    
    // Configura o menu da bandeja
    let menu = Menu::new();
    let info_item = MenuItem::new("Informações", true, None);
    let restore_item = MenuItem::new("Restaurar", true, None);
    let exit_item = MenuItem::new("Sair", true, None);
    
    // Armazena os IDs dos itens para uso posterior
    let info_id = info_item.id();
    let restore_id = restore_item.id();
    let exit_id = exit_item.id();
    
    menu.append(&info_item);
    menu.append(&restore_item);
    menu.append(&exit_item);
    
    // Tenta encontrar o caminho absoluto para o ícone
    let icon_path = find_icon_path("assets/icon_16x16.ico")?;
    info!("Usando ícone da bandeja: {}", icon_path.display());
    
    // Carrega o ícone da aplicação
    let icon = Icon::from_path(&icon_path, None)
        .map_err(|e| anyhow::anyhow!("Erro ao carregar ícone da bandeja: {}", e))?;
    
    // Cria o ícone da bandeja
    let _tray_icon = TrayIconBuilder::new()
        .with_tooltip("Tanakai")
        .with_icon(icon)
        .with_menu(Box::new(menu))
        .build()?;
    
    // Configura o receptor de eventos do menu
    let event_receiver = MenuEvent::receiver();
    
    // Inicia uma thread que apenas encaminha eventos do menu
    // usando os IDs armazenados e não os objetos MenuItem diretamente
    let _handle: JoinHandle<()> = std::thread::spawn(move || {
        for event in event_receiver {
            let action = if event.id == info_id {
                Some(TrayAction::ShowInfo)
            } else if event.id == restore_id {
                Some(TrayAction::Restore)
            } else if event.id == exit_id {
                Some(TrayAction::Exit)
            } else {
                None
            };
            
            if let Some(action) = action {
                if let Err(e) = tx.send(action) {
                    error!("Erro ao enviar ação: {}", e);
                }
            }
        }
    });
    
    Ok(rx)
}

/// Tenta encontrar o caminho absoluto para o arquivo de ícone
fn find_icon_path(relative_path: &str) -> Result<PathBuf> {
    // Primeiro tenta encontrar o ícone relativo ao executável
    if let Ok(exe_path) = env::current_exe() {
        let exe_dir = exe_path.parent().unwrap_or_else(|| Path::new(""));
        let icon_path = exe_dir.join(relative_path);
        if icon_path.exists() {
            return Ok(icon_path);
        }
        
        // Tenta encontrar no diretório "assets" ao lado do executável
        let assets_icon_path = exe_dir.join("assets").join(Path::new(relative_path).file_name().unwrap_or_default());
        if assets_icon_path.exists() {
            return Ok(assets_icon_path);
        }
    }
    
    // Tenta encontrar o ícone relativo ao diretório de trabalho atual
    let current_dir = env::current_dir()?;
    let icon_path = current_dir.join(relative_path);
    if icon_path.exists() {
        return Ok(icon_path);
    }
    
    // Procura em um nível acima (útil para teste)
    let parent_dir = current_dir.parent().unwrap_or_else(|| Path::new(""));
    let parent_icon_path = parent_dir.join(relative_path);
    if parent_icon_path.exists() {
        return Ok(parent_icon_path);
    }
    
    // Se não encontrou em nenhum lugar, retorna o caminho relativo original
    // e deixa o erro ser tratado pela função chamadora
    Err(anyhow::anyhow!("Não foi possível encontrar o arquivo de ícone: {}", relative_path))
}

/// Mostra a página de informações sobre o aplicativo
pub fn show_info_page() -> Result<()> {
    let hardware_info = match hwid::collect_hardware_info() {
        Ok(info) => {
            let hwid = hwid::HwId::new(&info);
            hwid.to_string()
        },
        Err(_) => "Não foi possível coletar informações de hardware".to_string(),
    };
    
    // URL da API com o token de hardware
    let api_url = config::get_api_url("/status");
    let info_url = format!("{}?hwid={}", api_url, hardware_info);
    
    match open::that(info_url) {
        Ok(_) => {
            info!("Página de informações aberta com sucesso");
            Ok(())
        },
        Err(e) => {
            error!("Erro ao abrir página de informações: {}", e);
            Err(anyhow::anyhow!("Erro ao abrir página de informações: {}", e))
        }
    }
} 