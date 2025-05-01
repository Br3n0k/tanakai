use egui::{Button as EguiButton, Color32, RichText, Ui};
use crate::ui::Theme;

pub struct ButtonStyle {
    pub text: String,
    pub icon: Option<&'static str>,
    pub color: Color32,
    pub hover_color: Color32,
    pub active_color: Color32,
    pub font_size: f32,
}

impl Default for ButtonStyle {
    fn default() -> Self {
        Self {
            text: String::new(),
            icon: None,
            color: Color32::from_rgb(0, 255, 0),
            hover_color: Color32::from_rgb(0, 200, 0),
            active_color: Color32::from_rgb(0, 150, 0),
            font_size: 14.0,
        }
    }
}

pub struct Button {
    style: ButtonStyle,
    theme: Theme,
}

impl Button {
    pub fn new(theme: Theme) -> Self {
        Self {
            style: ButtonStyle::default(),
            theme,
        }
    }
    
    pub fn text(mut self, text: impl Into<String>) -> Self {
        self.style.text = text.into();
        self
    }
    
    pub fn icon(mut self, icon: &'static str) -> Self {
        self.style.icon = Some(icon);
        self
    }
    
    pub fn color(mut self, color: Color32) -> Self {
        self.style.color = color;
        self
    }
    
    pub fn hover_color(mut self, color: Color32) -> Self {
        self.style.hover_color = color;
        self
    }
    
    pub fn active_color(mut self, color: Color32) -> Self {
        self.style.active_color = color;
        self
    }
    
    pub fn font_size(mut self, size: f32) -> Self {
        self.style.font_size = size;
        self
    }
    
    pub fn show(&self, ui: &mut Ui) -> bool {
        let button = EguiButton::new(
            RichText::new(&self.style.text)
                .font(self.theme.get_font(self.style.font_size))
                .color(self.style.color),
        )
        .min_size(egui::vec2(120.0, 32.0));
        
        let response = ui.add(button);
        
        if response.hovered() {
            ui.painter().rect_filled(
                response.rect,
                0.0,
                self.style.hover_color
            );
        }
        
        if response.clicked() {
            ui.painter().rect_filled(
                response.rect,
                0.0,
                self.style.active_color
            );
            true
        } else {
            false
        }
    }
} 