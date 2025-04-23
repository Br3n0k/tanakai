mod api;
mod capture;
mod models;
mod photon;
mod utils;
mod config;
mod hwid;

use clap::Parser;
use log::{error, info};
use std::process;

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

#[tokio::main]
async fn main() -> anyhow::Result<()> {
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

    // Inicia o capturador de pacotes
    if !args.quiet {
        info!("Iniciando captura de pacotes...");
    }
    
    let result = capture::start_capture(args.interface, args.api_url, args.quiet).await;
    
    if let Err(err) = result {
        error!("Erro ao iniciar captura: {}", err);
        return Err(err);
    }

    Ok(())
}
