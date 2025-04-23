mod network;
pub mod logger;

pub use network::{find_default_interface, create_capture, is_photon_packet}; 