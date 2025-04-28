mod api;
mod capture;
mod models;
mod photon;
mod utils;
mod config;
mod hwid;
mod ui;

use clap::Parser;
use log::{error, info};
use std::process;
use tokio::select;
use tokio::sync::mpsc;

#[derive(Parser, Debug)]
#[clap(author, version, about, long_about = None)]
struct Args {
    /// Endereço da API para enviar os dados
    #[clap(short, long, default_value = "http://api.tanakai.io/v1")]
    api_url: String,

    /// Interface de rede a ser monitorada
    #[clap(short, long)]
    interface: Option<String>,

    /// Modo de execução silencioso
    #[clap(short, long)]
    quiet: bool,
    
    /// Desabilitar ícone na bandeja do sistema
    #[clap(short, long)]
    no_tray: bool,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Verifica caminhos de assets
    if let Ok(exe_path) = std::env::current_exe() {
        log::info!("Executável em: {}", exe_path.display());
        
        let exe_dir = exe_path.parent().unwrap_or_else(|| std::path::Path::new(""));
        log::info!("Diretório do executável: {}", exe_dir.display());
        
        let icon_path = exe_dir.join("assets").join("icon_16x16.ico");
        log::info!("Verificando ícone em: {} (existe: {})", 
            icon_path.display(), icon_path.exists());
        
        let current_dir = std::env::current_dir().unwrap_or_else(|_| std::path::PathBuf::from("."));
        log::info!("Diretório atual: {}", current_dir.display());
        
        let current_icon_path = current_dir.join("assets").join("icon_16x16.ico");
        log::info!("Verificando ícone em diretório atual: {} (existe: {})", 
            current_icon_path.display(), current_icon_path.exists());
    }

    // Processa argumentos da linha de comando
    let args = Args::parse();

    // Inicializa o logger
    utils::logger::setup_logger(args.quiet);

    if !args.quiet {
        info!("Tanakai - Sniffer de pacotes Photon para Albion Online");
    }

    // Inicializa o módulo de configuração
    config::init_config(Some(args.api_url.clone()), args.quiet);

    // Verifica o hardware
    match hwid::collect_hardware_info() {
        Ok(hardware_info) => {
            if !args.quiet {
                info!("Informações de hardware coletadas com sucesso");
            }
            
            // Verifica o hardware na API
            match hwid::verify_hardware(&hardware_info).await {
                Ok(status) => match status {
                    hwid::HwIdStatus::Banned(components) => {
                        error!("Este hardware está banido e não pode executar o Tanakai");
                        for component in components {
                            error!("Componente banido: {} - Razão: {}", 
                                component.component_type, component.reason);
                        }
                        process::exit(1);
                    },
                    _ => {
                        if !args.quiet {
                            info!("Verificação de hardware concluída");
                        }
                    }
                },
                Err(e) => {
                    error!("Erro ao verificar hardware: {}", e);
                    // Não bloqueamos a execução, apenas logamos o erro
                }
            }
        },
        Err(e) => {
            error!("Erro ao coletar informações de hardware: {}", e);
            // Não bloqueamos a execução, apenas logamos o erro
        }
    }
    
    // Cria um canal para comandos do sistema
    let (_tx, mut rx) = mpsc::channel::<String>(10);
    
    // Inicia o capturador em background
    let capture_handle = tokio::spawn(async move {
        match capture::start_capture(args.interface, args.api_url, args.quiet).await {
            Ok(_) => {
                if !args.quiet {
                    info!("Captura finalizada com sucesso");
                }
            },
            Err(e) => {
                error!("Erro na captura: {}", e);
            }
        }
    });
    
    // Inicia o ícone da bandeja do sistema, se não estiver desativado
    if !args.no_tray {
        // Inicializa o gerenciador de janela para minimizar para a bandeja
        let window_tx = match ui::init_window_manager() {
            Ok(tx) => Some(tx),
            Err(e) => {
                error!("Erro ao inicializar gerenciador de janela: {}", e);
                None
            }
        };
        
        match ui::start_tray_icon() {
            Ok(tray_rx) => {
                tokio::spawn(async move {
                    loop {
                        // Processar ações da bandeja
                        if let Ok(action) = tray_rx.recv() {
                            match action {
                                ui::tray::TrayAction::ShowInfo => {
                                    if let Err(e) = ui::tray::show_info_page() {
                                        error!("Erro ao mostrar página de informações: {}", e);
                                    }
                                }
                                ui::tray::TrayAction::Restore => {
                                    // Restaura a janela da bandeja
                                    if let Some(tx) = &window_tx {
                                        if let Err(e) = tx.send(ui::WindowMessage::RestoreFromTray) {
                                            error!("Erro ao restaurar janela: {}", e);
                                        }
                                    }
                                }
                                ui::tray::TrayAction::Exit => {
                                    info!("Saindo do aplicativo através da bandeja do sistema");
                                    std::process::exit(0);
                                }
                            }
                        }
                    }
                });
            }
            Err(e) => {
                error!("Erro ao iniciar ícone da bandeja: {}", e);
            }
        }
    }
    
    // Aguarda por um sinal de saída
    select! {
        _ = rx.recv() => {
            info!("Recebido sinal para encerrar o aplicativo");
        }
        _ = tokio::signal::ctrl_c() => {
            info!("Recebido sinal Ctrl+C");
        }
    }
    
    // Tenta abortar a captura
    capture_handle.abort();
    
    if !args.quiet {
        info!("Tanakai finalizado");
    }
    
    Ok(())
}
