use log::{error, info};
use anyhow::Result;
use std::thread;
use std::sync::mpsc::{self, Receiver, Sender};
use std::time::Duration;

#[cfg(target_os = "windows")]
use windows_sys::Win32::Foundation::{HWND, WPARAM};
#[cfg(target_os = "windows")]
use windows_sys::Win32::UI::WindowsAndMessaging::{
    GetWindowLongPtrA, SetWindowLongPtrA, SendMessageA, 
    GWL_STYLE, WM_SYSCOMMAND, SC_MINIMIZE, WS_VISIBLE, WS_MINIMIZE,
    GetWindowThreadProcessId, WM_SIZE, EnumWindows,
};
#[cfg(target_os = "windows")]
use windows_sys::Win32::System::Threading::GetCurrentProcessId;

/// Mensagens que podem ser enviadas para o gerenciador de janela
#[allow(dead_code)]
pub enum WindowMessage {
    /// Minimizar a janela para a bandeja
    MinimizeToTray,
    /// Restaurar a janela da bandeja
    RestoreFromTray,
    /// Sair do aplicativo
    Exit,
}

/// Inicializa o gerenciador de janela
/// 
/// Retorna um canal para enviar mensagens ao gerenciador
pub fn init_window_manager() -> Result<Sender<WindowMessage>> {
    let (tx, rx) = mpsc::channel();
    
    // Inicia a thread do gerenciador de janela
    thread::spawn(move || {
        if let Err(e) = window_manager_thread(rx) {
            error!("Erro no gerenciador de janela: {}", e);
        }
    });
    
    // Aguarda um pouco para a thread inicializar
    thread::sleep(Duration::from_millis(500));
    
    // Nota: Não tentamos mais minimizar automaticamente a janela na inicialização
    // para evitar erros quando não conseguimos encontrar a janela do console
    
    Ok(tx)
}

/// Thread principal do gerenciador de janela
fn window_manager_thread(rx: Receiver<WindowMessage>) -> Result<()> {
    info!("Gerenciador de janela iniciado");
    
    loop {
        // Processa mensagens recebidas
        match rx.recv() {
            Ok(message) => {
                match message {
                    WindowMessage::MinimizeToTray => {
                        if let Err(e) = minimize_to_tray() {
                            error!("Erro ao minimizar para a bandeja: {}", e);
                        }
                    },
                    WindowMessage::RestoreFromTray => {
                        if let Err(e) = restore_from_tray() {
                            error!("Erro ao restaurar da bandeja: {}", e);
                        }
                    },
                    WindowMessage::Exit => {
                        info!("Recebida mensagem para encerrar o gerenciador de janela");
                        break;
                    }
                }
            },
            Err(e) => {
                error!("Erro ao receber mensagem no gerenciador de janela: {}", e);
                break;
            }
        }
    }
    
    info!("Gerenciador de janela finalizado");
    Ok(())
}

/// Minimiza a janela do console para a bandeja do sistema
#[cfg(target_os = "windows")]
fn minimize_to_tray() -> Result<()> {
    unsafe {
        // Encontra a janela do console para o processo atual
        match find_console_window() {
            Ok(hwnd) => {
                // Altera o estilo da janela para não ser visível quando minimizada
                let style = GetWindowLongPtrA(hwnd, GWL_STYLE);
                SetWindowLongPtrA(hwnd, GWL_STYLE, style & (!WS_VISIBLE as isize) | WS_MINIMIZE as isize);
                
                // Envia mensagem para minimizar a janela
                SendMessageA(hwnd, WM_SYSCOMMAND, SC_MINIMIZE as WPARAM, 0);
                SendMessageA(hwnd, WM_SIZE, 1, 0);
                
                info!("Janela minimizada para a bandeja");
                Ok(())
            },
            Err(e) => {
                // Se não conseguimos encontrar a janela, apenas logamos o erro
                // mas não considera isso um erro fatal
                info!("Não foi possível minimizar para a bandeja: {}", e);
                // Retornamos Ok para não propagar o erro
                Ok(())
            }
        }
    }
}

/// Restaura a janela do console da bandeja do sistema
#[cfg(target_os = "windows")]
fn restore_from_tray() -> Result<()> {
    unsafe {
        // Encontra a janela do console para o processo atual
        match find_console_window() {
            Ok(hwnd) => {
                // Altera o estilo da janela para ser visível
                let style = GetWindowLongPtrA(hwnd, GWL_STYLE);
                SetWindowLongPtrA(hwnd, GWL_STYLE, style | WS_VISIBLE as isize);
                
                // Mostra a janela
                ShowWindow(hwnd, 9); // SW_RESTORE = 9
                
                info!("Janela restaurada da bandeja");
                Ok(())
            },
            Err(e) => {
                // Se não conseguimos encontrar a janela, apenas logamos o erro
                // mas não considera isso um erro fatal
                info!("Não foi possível restaurar da bandeja: {}", e);
                // Retornamos Ok para não propagar o erro
                Ok(())
            }
        }
    }
}

// Função auxiliar para obter o nome da classe de uma janela e manipular janelas
#[cfg(target_os = "windows")]
#[link(name = "user32")]
extern "system" {
    fn GetClassNameA(hwnd: HWND, lpClassName: *mut u8, nMaxCount: i32) -> i32;
    fn ShowWindow(hwnd: HWND, nCmdShow: i32) -> i32;
}

/// Encontra o handle da janela do console do processo atual
#[cfg(target_os = "windows")]
unsafe fn find_console_window() -> Result<HWND> {
    // Estrutura para passar dados entre EnumWindows e o callback
    struct EnumData {
        process_id: u32,
        hwnd: HWND,
    }
    
    // Callback para EnumWindows
    unsafe extern "system" fn enum_windows_callback(hwnd: HWND, lparam: isize) -> i32 {
        let enum_data = &mut *(lparam as *mut EnumData);
        let mut window_process_id: u32 = 0;
        
        GetWindowThreadProcessId(hwnd, &mut window_process_id);
        
        if window_process_id == enum_data.process_id {
            // Verifica se esta é uma janela de console
            let mut class_name = [0u8; 256];
            let len = GetClassNameA(hwnd, class_name.as_mut_ptr(), class_name.len() as i32);
            
            if len > 0 {
                let class_name = String::from_utf8_lossy(&class_name[..len as usize]);
                // Verifica vários nomes de classe que podem representar uma janela de console
                // ConsoleWindowClass: Windows cmd tradicional
                // Mintty: Git Bash e outros terminais baseados no mintty
                // VirtualConsoleClass: Windows Terminal e outros
                if class_name == "ConsoleWindowClass" || 
                   class_name.contains("Mintty") || 
                   class_name.contains("Console") || 
                   class_name.contains("Terminal") {
                    info!("Encontrada janela de console com classe: {}", class_name);
                    enum_data.hwnd = hwnd;
                    return 0; // Interrompe a enumeração
                }
            }
        }
        
        1 // Continua a enumeração
    }
    
    // Obter o ID do processo atual
    let process_id = GetCurrentProcessId();
    
    // Dados para o callback
    let mut enum_data = EnumData {
        process_id,
        hwnd: 0,
    };
    
    // Enumera todas as janelas
    EnumWindows(Some(enum_windows_callback), &mut enum_data as *mut _ as isize);
    
    if enum_data.hwnd == 0 {
        return Err(anyhow::anyhow!("Não foi possível encontrar a janela do console"));
    }
    
    Ok(enum_data.hwnd)
}

/// Implementações vazias para outros sistemas operacionais
#[cfg(not(target_os = "windows"))]
fn minimize_to_tray() -> Result<()> {
    info!("Minimização para bandeja não implementada para este sistema operacional");
    Ok(())
}

#[cfg(not(target_os = "windows"))]
fn restore_from_tray() -> Result<()> {
    info!("Restauração da bandeja não implementada para este sistema operacional");
    Ok(())
} 