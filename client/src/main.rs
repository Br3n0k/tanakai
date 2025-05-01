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
use eframe::egui;
use crate::ui::{Theme, Dashboard};

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
}

struct TanakaiApp {
    dashboard: Dashboard,
    capture_handle: Option<tokio::task::JoinHandle<()>>,
}

impl TanakaiApp {
    fn new(_cc: &eframe::CreationContext<'_>) -> Self {
        // Inicializa o logger
        utils::logger::setup_logger(false);
        
        // Inicializa a configuração
        config::init_config(None, false);
        
        // Cria o tema
        let theme = Theme::new(config::CONFIG.read().unwrap().theme.clone());
        
        // Cria o dashboard
        let dashboard = Dashboard::new(theme);
        
        Self {
            dashboard,
            capture_handle: None,
        }
    }
}

impl eframe::App for TanakaiApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        // Verifica atualizações
        let rt = tokio::runtime::Runtime::new().unwrap();
        if let Ok(has_update) = rt.block_on(config::check_for_updates()) {
            if has_update {
                self.dashboard.set_status(
                    "Uma nova versão está disponível!".to_string(),
                    crate::ui::components::status::StatusType::Warning,
                );
            }
        }
        
        // Mostra o dashboard
        self.dashboard.show(ctx);
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
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
    
    // Inicia a aplicação
    let options = eframe::NativeOptions {
        initial_window_size: Some(egui::vec2(1024.0, 768.0)),
        ..Default::default()
    };
    
    eframe::run_native(
        "Tanakai",
        options,
        Box::new(|cc| Box::new(TanakaiApp::new(cc))),
    )?;
    
    Ok(())
}
