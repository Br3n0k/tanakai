use anyhow::Result;
use log::{error, info};
use reqwest::Client;
use serde::Serialize;

/// Cliente para comunicação com a API REST
pub struct ApiClient {
    client: Client,
    api_url: String,
    quiet: bool,
}

impl ApiClient {
    pub fn new(api_url: String, quiet: bool) -> Self {
        ApiClient {
            client: Client::new(),
            api_url,
            quiet,
        }
    }

    /// Envia dados para a API
    pub async fn send_event<T: Serialize>(&self, event_type: &str, data: &T) -> Result<()> {
        let url = format!("{}/events/{}", self.api_url, event_type);
        
        let response = self.client.post(&url)
            .json(data)
            .send()
            .await?;

        if !response.status().is_success() {
            let error_msg = format!("Falha ao enviar evento: {}", response.status());
            if !self.quiet {
                error!("{}", error_msg);
            }
            return Err(anyhow::anyhow!(error_msg));
        }
        
        if !self.quiet {
            info!("Evento {} enviado com sucesso", event_type);
        }
        
        Ok(())
    }
} 