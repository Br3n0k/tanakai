use egui::{Color32, Frame, RichText, Ui, Vec2};
use crate::ui::Theme;

pub struct SidebarItem {
    pub text: String,
    pub icon: Option<&'static str>,
    pub selected: bool,
}

pub struct SidebarStyle {
    pub items: Vec<SidebarItem>,
    pub color: Color32,
    pub border_color: Color32,
    pub border_width: f32,
    pub padding: Vec2,
    pub item_height: f32,
    pub font_size: f32,
    pub min_size: Vec2,
}

impl Default for SidebarStyle {
    fn default() -> Self {
        Self {
            items: Vec::new(),
            color: Color32::from_rgb(26, 26, 26),
            border_color: Color32::from_rgb(0, 255, 0),
            border_width: 1.0,
            padding: Vec2::splat(8.0),
            item_height: 32.0,
            font_size: 14.0,
            min_size: Vec2::new(200.0, 0.0),
        }
    }
}

pub struct Sidebar {
    style: SidebarStyle,
    theme: Theme,
}

impl Sidebar {
    pub fn new(theme: Theme) -> Self {
        Self {
            style: SidebarStyle::default(),
            theme,
        }
    }
    
    pub fn items(mut self, items: Vec<SidebarItem>) -> Self {
        self.style.items = items;
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
    
    pub fn item_height(mut self, height: f32) -> Self {
        self.style.item_height = height;
        self
    }
    
    pub fn font_size(mut self, size: f32) -> Self {
        self.style.font_size = size;
        self
    }
    
    pub fn min_size(mut self, size: Vec2) -> Self {
        self.style.min_size = size;
        self
    }
    
    pub fn show(&self, ui: &mut Ui) -> Option<usize> {
        let mut selected_index = None;
        
        Frame::none()
            .fill(self.style.color)
            .stroke(egui::Stroke::new(self.style.border_width, self.style.border_color))
            .inner_margin(self.style.padding)
            .show(ui, |ui| {
                ui.set_min_size(self.style.min_size);
                for (index, item) in self.style.items.iter().enumerate() {
                    let button = egui::Button::new(
                        RichText::new(&item.text)
                            .font(self.theme.get_font(self.style.font_size))
                            .color(if item.selected {
                                self.theme.get_color("primary")
                            } else {
                                self.theme.get_color("text")
                            }),
                    )
                    .min_size(egui::vec2(ui.available_width(), self.style.item_height));
                    
                    let response = ui.add(button);
                    
                    if response.clicked() {
                        selected_index = Some(index);
                    }
                }
            });
        
        selected_index
    }
} 