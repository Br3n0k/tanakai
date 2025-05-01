use egui::{Color32, Frame, RichText, Ui, Vec2};
use crate::ui::Theme;

pub struct HeaderStyle {
    pub title: String,
    pub subtitle: Option<String>,
    pub color: Color32,
    pub border_color: Color32,
    pub border_width: f32,
    pub padding: Vec2,
    pub font_size: f32,
}

impl Default for HeaderStyle {
    fn default() -> Self {
        Self {
            title: String::new(),
            subtitle: None,
            color: Color32::from_rgb(0, 0, 0),
            border_color: Color32::from_rgb(0, 255, 0),
            border_width: 1.0,
            padding: Vec2::new(16.0, 8.0),
            font_size: 24.0,
        }
    }
}

pub struct Header {
    style: HeaderStyle,
    theme: Theme,
}

impl Header {
    pub fn new(theme: Theme) -> Self {
        Self {
            style: HeaderStyle::default(),
            theme,
        }
    }
    
    pub fn title(mut self, title: impl Into<String>) -> Self {
        self.style.title = title.into();
        self
    }
    
    pub fn subtitle(mut self, subtitle: impl Into<String>) -> Self {
        self.style.subtitle = Some(subtitle.into());
        self
    }
    
    pub fn color(mut self, color: Color32) -> Self {
        self.style.color = color;
        self
    }
    
    pub fn border_color(mut self, color: Color32) -> Self {
        self.style.border_color = color;
        self
    }
    
    pub fn border_width(mut self, width: f32) -> Self {
        self.style.border_width = width;
        self
    }
    
    pub fn padding(mut self, padding: Vec2) -> Self {
        self.style.padding = padding;
        self
    }
    
    pub fn font_size(mut self, size: f32) -> Self {
        self.style.font_size = size;
        self
    }
    
    pub fn show(&self, ui: &mut Ui) {
        Frame::none()
            .fill(self.style.color)
            .stroke(egui::Stroke::new(self.style.border_width, self.style.border_color))
            .inner_margin(self.style.padding)
            .show(ui, |ui| {
                ui.horizontal(|ui| {
                    // Título
                    ui.heading(
                        RichText::new(&self.style.title)
                            .font(self.theme.get_font(self.style.font_size))
                            .color(self.theme.get_color("text")),
                    );
                    
                    // Subtítulo
                    if let Some(subtitle) = &self.style.subtitle {
                        ui.label(
                            RichText::new(subtitle)
                                .font(self.theme.get_font(self.style.font_size - 8.0))
                                .color(self.theme.get_color("text")),
                        );
                    }
                    
                    ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |_ui| {
                        // Adicione aqui os controles do cabeçalho (botões, etc.)
                    });
                });
            });
    }
} 