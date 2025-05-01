use egui::{Color32, Frame, RichText, Ui, Vec2};
use crate::ui::Theme;

#[derive(Clone)]
pub enum StatusType {
    Success,
    Warning,
    Error,
    Info,
}

pub struct StatusStyle {
    pub text: String,
    pub status_type: StatusType,
    pub color: Color32,
    pub border_color: Color32,
    pub border_width: f32,
    pub corner_radius: f32,
    pub padding: Vec2,
    pub font_size: f32,
}

impl Default for StatusStyle {
    fn default() -> Self {
        Self {
            text: String::new(),
            status_type: StatusType::Info,
            color: Color32::from_rgb(26, 26, 26),
            border_color: Color32::from_rgb(0, 255, 0),
            border_width: 1.0,
            corner_radius: 4.0,
            padding: Vec2::splat(8.0),
            font_size: 14.0,
        }
    }
}

pub struct Status {
    style: StatusStyle,
    theme: Theme,
}

impl Status {
    pub fn new(theme: Theme) -> Self {
        Self {
            style: StatusStyle::default(),
            theme,
        }
    }
    
    pub fn text(mut self, text: impl Into<String>) -> Self {
        self.style.text = text.into();
        self
    }
    
    pub fn status_type(mut self, status_type: StatusType) -> Self {
        self.style.status_type = status_type;
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
    
    pub fn corner_radius(mut self, radius: f32) -> Self {
        self.style.corner_radius = radius;
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
        let status_color = match self.style.status_type {
            StatusType::Success => self.theme.get_color("success"),
            StatusType::Warning => self.theme.get_color("warning"),
            StatusType::Error => self.theme.get_color("error"),
            StatusType::Info => self.theme.get_color("primary"),
        };
        
        Frame::none()
            .fill(self.style.color)
            .stroke(egui::Stroke::new(self.style.border_width, status_color))
            .rounding(self.style.corner_radius)
            .inner_margin(self.style.padding)
            .show(ui, |ui| {
                ui.label(
                    RichText::new(&self.style.text)
                        .font(self.theme.get_font(self.style.font_size))
                        .color(status_color),
                );
            });
    }
} 