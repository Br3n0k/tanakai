use eframe::egui;
use crate::ui::Theme;

pub struct WindowManager {
    theme: Theme,
    windows: Vec<Box<dyn Window>>,
}

pub trait Window {
    fn title(&self) -> &str;
    fn show(&mut self, ctx: &egui::Context);
}

impl WindowManager {
    pub fn new(theme: Theme) -> Self {
        Self {
            theme,
            windows: Vec::new(),
        }
    }
    
    pub fn add_window(&mut self, window: Box<dyn Window>) {
        self.windows.push(window);
    }
    
    pub fn show(&mut self, ctx: &egui::Context) {
        for window in &mut self.windows {
            egui::Window::new(window.title())
                .default_pos(egui::pos2(100.0, 100.0))
                .default_size(egui::vec2(400.0, 300.0))
                .show(ctx, |_ui| {
                    window.show(ctx);
                });
        }
    }
} 