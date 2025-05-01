use egui::{Color32, FontId, Margin, Rounding, Stroke, Vec2};
use crate::config::ThemeConfig;

#[derive(Clone)]
pub struct Theme {
    config: ThemeConfig,
}

impl Theme {
    pub fn new(config: ThemeConfig) -> Self {
        Self { config }
    }
    
    pub fn apply(&self, ctx: &egui::Context) {
        let mut style = ctx.style().clone();
        
        // Aplica as cores
        style.visuals.override_text_color = Some(Color32::from_rgb(
            u8::from_str_radix(&self.config.colors.text[1..3], 16).unwrap(),
            u8::from_str_radix(&self.config.colors.text[3..5], 16).unwrap(),
            u8::from_str_radix(&self.config.colors.text[5..7], 16).unwrap(),
        ));
        style.visuals.window_fill = Color32::from_rgb(
            u8::from_str_radix(&self.config.colors.background[1..3], 16).unwrap(),
            u8::from_str_radix(&self.config.colors.background[3..5], 16).unwrap(),
            u8::from_str_radix(&self.config.colors.background[5..7], 16).unwrap(),
        );
        style.visuals.faint_bg_color = Color32::from_rgb(
            u8::from_str_radix(&self.config.colors.surface[1..3], 16).unwrap(),
            u8::from_str_radix(&self.config.colors.surface[3..5], 16).unwrap(),
            u8::from_str_radix(&self.config.colors.surface[5..7], 16).unwrap(),
        );
        style.visuals.hyperlink_color = Color32::from_rgb(
            u8::from_str_radix(&self.config.colors.accent[1..3], 16).unwrap(),
            u8::from_str_radix(&self.config.colors.accent[3..5], 16).unwrap(),
            u8::from_str_radix(&self.config.colors.accent[5..7], 16).unwrap(),
        );
        style.visuals.window_stroke = Stroke::new(1.0, Color32::from_rgb(
            u8::from_str_radix(&self.config.colors.primary[1..3], 16).unwrap(),
            u8::from_str_radix(&self.config.colors.primary[3..5], 16).unwrap(),
            u8::from_str_radix(&self.config.colors.primary[5..7], 16).unwrap(),
        ));
        
        // Aplica os estilos
        style.spacing.item_spacing = Vec2::splat(self.config.styles.margin);
        style.spacing.window_margin = Margin::same(self.config.styles.padding);
        style.visuals.window_rounding = Rounding::same(self.config.styles.border_radius);
        style.visuals.widgets.noninteractive.rounding = Rounding::same(self.config.styles.border_radius);
        style.visuals.widgets.inactive.rounding = Rounding::same(self.config.styles.border_radius);
        style.visuals.widgets.hovered.rounding = Rounding::same(self.config.styles.border_radius);
        style.visuals.widgets.active.rounding = Rounding::same(self.config.styles.border_radius);
        
        // Aplica a fonte
        let mut fonts = egui::FontDefinitions::default();
        
        ctx.set_fonts(fonts);
        ctx.set_style(style);
    }
    
    pub fn get_color(&self, name: &str) -> Color32 {
        match name {
            "primary" => Color32::from_rgb(
                u8::from_str_radix(&self.config.colors.primary[1..3], 16).unwrap(),
                u8::from_str_radix(&self.config.colors.primary[3..5], 16).unwrap(),
                u8::from_str_radix(&self.config.colors.primary[5..7], 16).unwrap(),
            ),
            "secondary" => Color32::from_rgb(
                u8::from_str_radix(&self.config.colors.secondary[1..3], 16).unwrap(),
                u8::from_str_radix(&self.config.colors.secondary[3..5], 16).unwrap(),
                u8::from_str_radix(&self.config.colors.secondary[5..7], 16).unwrap(),
            ),
            "background" => Color32::from_rgb(
                u8::from_str_radix(&self.config.colors.background[1..3], 16).unwrap(),
                u8::from_str_radix(&self.config.colors.background[3..5], 16).unwrap(),
                u8::from_str_radix(&self.config.colors.background[5..7], 16).unwrap(),
            ),
            "surface" => Color32::from_rgb(
                u8::from_str_radix(&self.config.colors.surface[1..3], 16).unwrap(),
                u8::from_str_radix(&self.config.colors.surface[3..5], 16).unwrap(),
                u8::from_str_radix(&self.config.colors.surface[5..7], 16).unwrap(),
            ),
            "text" => Color32::from_rgb(
                u8::from_str_radix(&self.config.colors.text[1..3], 16).unwrap(),
                u8::from_str_radix(&self.config.colors.text[3..5], 16).unwrap(),
                u8::from_str_radix(&self.config.colors.text[5..7], 16).unwrap(),
            ),
            "accent" => Color32::from_rgb(
                u8::from_str_radix(&self.config.colors.accent[1..3], 16).unwrap(),
                u8::from_str_radix(&self.config.colors.accent[3..5], 16).unwrap(),
                u8::from_str_radix(&self.config.colors.accent[5..7], 16).unwrap(),
            ),
            "error" => Color32::from_rgb(
                u8::from_str_radix(&self.config.colors.error[1..3], 16).unwrap(),
                u8::from_str_radix(&self.config.colors.error[3..5], 16).unwrap(),
                u8::from_str_radix(&self.config.colors.error[5..7], 16).unwrap(),
            ),
            "warning" => Color32::from_rgb(
                u8::from_str_radix(&self.config.colors.warning[1..3], 16).unwrap(),
                u8::from_str_radix(&self.config.colors.warning[3..5], 16).unwrap(),
                u8::from_str_radix(&self.config.colors.warning[5..7], 16).unwrap(),
            ),
            "success" => Color32::from_rgb(
                u8::from_str_radix(&self.config.colors.success[1..3], 16).unwrap(),
                u8::from_str_radix(&self.config.colors.success[3..5], 16).unwrap(),
                u8::from_str_radix(&self.config.colors.success[5..7], 16).unwrap(),
            ),
            _ => Color32::WHITE,
        }
    }
    
    pub fn get_font(&self, size: f32) -> FontId {
        FontId::new(size, egui::FontFamily::Proportional)
    }
} 