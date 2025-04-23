use env_logger::{Builder, Env};
use log::LevelFilter;

/// Configura o logger da aplicação
pub fn setup_logger(quiet: bool) {
    let mut builder = Builder::from_env(Env::default());
    
    if quiet {
        builder.filter_level(LevelFilter::Error);
    } else {
        builder.filter_level(LevelFilter::Info);
    }
    
    builder.init();
} 