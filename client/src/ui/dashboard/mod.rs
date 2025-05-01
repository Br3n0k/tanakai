use eframe::egui;
use crate::ui::Theme;
use crate::ui::components::button::Button;
use crate::ui::components::card::Card;
use crate::ui::components::header::Header;
use crate::ui::components::sidebar::{Sidebar, SidebarItem};
use crate::ui::components::status::{Status, StatusType};

pub struct Dashboard {
    theme: Theme,
    selected_tab: usize,
    status: Option<String>,
    status_type: StatusType,
}

impl Dashboard {
    pub fn new(theme: Theme) -> Self {
        Self {
            theme,
            selected_tab: 0,
            status: None,
            status_type: StatusType::Info,
        }
    }
    
    pub fn show(&mut self, ctx: &egui::Context) {
        // Aplica o tema
        self.theme.apply(ctx);
        
        // Layout principal
        egui::CentralPanel::default().show(ctx, |ui| {
            // Cabeçalho
            Header::new(self.theme.clone())
                .title("Tanakai")
                .subtitle("Photon Packet Sniffer")
                .show(ui);
            
            ui.horizontal(|ui| {
                // Barra lateral
                let sidebar_width = 200.0;
                let sidebar = Sidebar::new(self.theme.clone())
                    .items(vec![
                        SidebarItem {
                            text: "Dashboard".to_string(),
                            icon: Some("📊"),
                            selected: self.selected_tab == 0,
                        },
                        SidebarItem {
                            text: "Captura".to_string(),
                            icon: Some("🎯"),
                            selected: self.selected_tab == 1,
                        },
                        SidebarItem {
                            text: "Configurações".to_string(),
                            icon: Some("⚙️"),
                            selected: self.selected_tab == 2,
                        },
                        SidebarItem {
                            text: "Sobre".to_string(),
                            icon: Some("ℹ️"),
                            selected: self.selected_tab == 3,
                        },
                    ])
                    .min_size(egui::vec2(sidebar_width, ui.available_height()));
                
                if let Some(index) = sidebar.show(ui) {
                    self.selected_tab = index;
                }
                
                // Conteúdo principal
                ui.vertical(|ui| {
                    match self.selected_tab {
                        0 => self.show_dashboard(ui),
                        1 => self.show_capture(ui),
                        2 => self.show_settings(ui),
                        3 => self.show_about(ui),
                        _ => unreachable!(),
                    }
                });
            });
            
            // Barra de status
            if let Some(status) = &self.status {
                Status::new(self.theme.clone())
                    .text(status)
                    .status_type(self.status_type.clone())
                    .show(ui);
            }
        });
    }
    
    fn show_dashboard(&mut self, ui: &mut egui::Ui) {
        ui.heading("Dashboard");
        
        // Cards de status
        ui.horizontal(|ui| {
            Card::new(self.theme.clone())
                .title("Status da Captura")
                .subtitle("Monitoramento em tempo real")
                .show(ui, |ui| {
                    ui.label("Captura ativa");
                });
            
            Card::new(self.theme.clone())
                .title("Pacotes Capturados")
                .subtitle("Total de pacotes")
                .show(ui, |ui| {
                    ui.label("0 pacotes");
                });
        });
    }
    
    fn show_capture(&mut self, ui: &mut egui::Ui) {
        ui.heading("Captura de Pacotes");
        
        // Configurações de captura
        Card::new(self.theme.clone())
            .title("Configurações de Captura")
            .show(ui, |ui| {
                ui.label("Interface de rede:");
                ui.text_edit_singleline(&mut "Interface padrão");
                
                ui.add_space(8.0);
                
                Button::new(self.theme.clone())
                    .text("Iniciar Captura")
                    .show(ui);
            });
    }
    
    fn show_settings(&mut self, ui: &mut egui::Ui) {
        ui.heading("Configurações");
        
        // Configurações gerais
        Card::new(self.theme.clone())
            .title("Configurações Gerais")
            .show(ui, |ui| {
                ui.label("URL da API:");
                ui.text_edit_singleline(&mut "http://api.tanakai.io/v1");
                
                ui.add_space(8.0);
                
                ui.checkbox(&mut false, "Modo silencioso");
            });
    }
    
    fn show_about(&mut self, ui: &mut egui::Ui) {
        ui.heading("Sobre");
        
        // Informações do aplicativo
        Card::new(self.theme.clone())
            .title("Tanakai")
            .subtitle("Photon Packet Sniffer")
            .show(ui, |ui| {
                ui.label("Versão: 0.1.0");
                ui.label("Desenvolvido por: Tanakai Team");
                ui.label("Licença: MIT");
            });
    }
    
    pub fn set_status(&mut self, text: String, status_type: StatusType) {
        self.status = Some(text);
        self.status_type = status_type;
    }
} 