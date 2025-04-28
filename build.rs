use std::env;
use std::path::{Path, PathBuf};
use std::fs;
use std::process::Command;

fn main() {
    // Copia arquivos de assets para o diretório de saída
    copy_assets_to_output().unwrap_or_else(|e| {
        println!("cargo:warning=Erro ao copiar assets: {}", e);
    });
    
    // Configura caminhos adicionais para bibliotecas apenas no Windows
    #[cfg(target_os = "windows")]
    {
        // Obtém as variáveis de ambiente para os diretórios de programa
        let program_files = env::var("ProgramFiles").unwrap_or_else(|_| "C:/Program Files".to_string());
        let program_files_x86 = env::var("ProgramFiles(x86)").unwrap_or_else(|_| "C:/Program Files (x86)".to_string());
        let system_root = env::var("SystemRoot").unwrap_or_else(|_| "C:/Windows".to_string());
        
        // Normaliza os caminhos para usar barras normais (/)
        let program_files = program_files.replace("\\", "/");
        let program_files_x86 = program_files_x86.replace("\\", "/");
        let system_root = system_root.replace("\\", "/");
        
        println!("cargo:warning=ProgramFiles: {}", program_files);
        println!("cargo:warning=ProgramFiles(x86): {}", program_files_x86);
        println!("cargo:warning=SystemRoot: {}", system_root);
        
        // Lista dos caminhos padrão onde o wpcap.lib pode estar instalado
        let npcap_paths = [
            format!("{}/System32/Npcap", system_root),
            format!("{}/Npcap/SDK/Lib/x64", program_files),
            format!("{}/Npcap/SDK/Lib", program_files),
            format!("{}/Npcap/SDK/Lib/x64", program_files_x86),
            format!("{}/Npcap/SDK/Lib", program_files_x86),
            format!("{}/WinPcap/Lib/x64", program_files),
            format!("{}/WinPcap/Lib", program_files),
            format!("{}/WinPcap/Lib", program_files_x86),
        ];

        // Verifica se a biblioteca já existe em algum local do sistema
        let mut lib_found = false;
        
        // Adiciona os caminhos de busca e verifica a presença da biblioteca
        for path in &npcap_paths {
            println!("cargo:rustc-link-search={}", path);
            
            if !lib_found {
                let lib_path = Path::new(path).join("wpcap.lib");
                if lib_path.exists() {
                    println!("cargo:warning=Biblioteca wpcap.lib encontrada em: {}", path);
                    lib_found = true;
                }
            }
        }
        
        // Diretório dentro do projeto para armazenar o SDK do Npcap
        let current_dir = env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
        let vendor_dir = current_dir.join("vendor").join("npcap-sdk");
        let vendor_lib_dir = vendor_dir.join("Lib").join("x64");
        
        // Adiciona o diretório vendor ao caminho de busca
        println!("cargo:rustc-link-search={}", vendor_lib_dir.display());
        
        // Verifica se a biblioteca já existe no diretório vendor
        if let Ok(entries) = fs::read_dir(&vendor_lib_dir) {
            for entry in entries.flatten() {
                if entry.path().file_name().map_or(false, |name| name == "wpcap.lib") {
                    println!("cargo:warning=Biblioteca wpcap.lib encontrada em: {}", vendor_lib_dir.display());
                    lib_found = true;
                    break;
                }
            }
        }
        
        // Se a biblioteca não foi encontrada, tenta baixar o SDK
        if !lib_found {
            println!("cargo:warning=ATENÇÃO: A biblioteca wpcap.lib não foi encontrada em nenhum dos caminhos padrão!");
            println!("cargo:warning=Tentando baixar e instalar o SDK do Npcap para o diretório vendor...");
            
            if let Err(e) = download_and_install_npcap_sdk(&vendor_dir) {
                println!("cargo:warning=Falha ao baixar o SDK do Npcap: {}", e);
                println!("cargo:warning=Por favor, instale o Npcap SDK (https://npcap.com/dist/npcap-sdk-1.15.zip)");
                println!("cargo:warning=Você pode baixar manualmente e extrair para {}", vendor_dir.display());
                println!("cargo:warning=Ou extrair para %ProgramFiles%/Npcap/SDK/");
                println!("cargo:warning=Alternativa: Instale o WinPcap Developer's Pack (https://www.winpcap.org/devel.htm)");
            } else {
                // Adiciona novamente o caminho do vendor que agora deve conter a biblioteca
                println!("cargo:rustc-link-search={}", vendor_lib_dir.display());
            }
        }
    }
}

// Copia arquivos de assets para o diretório de saída
fn copy_assets_to_output() -> Result<(), String> {
    let out_dir = env::var("OUT_DIR").map_err(|e| format!("Erro ao obter OUT_DIR: {}", e))?;
    let out_path = Path::new(&out_dir);
    
    // Recua 3 diretórios para chegar ao diretório target/debug ou target/release
    let target_dir = out_path
        .parent().ok_or("Não foi possível obter o diretório pai de OUT_DIR")?
        .parent().ok_or("Não foi possível obter o diretório pai")?
        .parent().ok_or("Não foi possível obter o diretório pai")?;
    
    println!("cargo:warning=Copiando assets para: {}", target_dir.display());
    
    // Cria o diretório assets no diretório de saída, se não existir
    let target_assets_dir = target_dir.join("assets");
    if !target_assets_dir.exists() {
        fs::create_dir_all(&target_assets_dir)
            .map_err(|e| format!("Erro ao criar diretório assets: {}", e))?;
    }
    
    // Obtém o diretório do projeto (onde está o Cargo.toml)
    let manifest_dir = env::var("CARGO_MANIFEST_DIR")
        .map_err(|e| format!("Erro ao obter CARGO_MANIFEST_DIR: {}", e))?;
    let source_assets_dir = Path::new(&manifest_dir).join("assets");
    
    println!("cargo:warning=Copiando assets de: {}", source_assets_dir.display());
    
    // Copia os arquivos do diretório assets do projeto
    if source_assets_dir.exists() {
        for entry in fs::read_dir(&source_assets_dir)
            .map_err(|e| format!("Erro ao ler diretório assets: {}", e))? {
            
            let entry = entry.map_err(|e| format!("Erro ao ler entrada do diretório: {}", e))?;
            let path = entry.path();
            
            if path.is_file() {
                let file_name = path.file_name().ok_or("Nome de arquivo inválido")?;
                let target_file = target_assets_dir.join(file_name);
                
                println!("cargo:warning=Copiando: {} para {}", path.display(), target_file.display());
                
                fs::copy(&path, &target_file)
                    .map_err(|e| format!("Erro ao copiar arquivo {}: {}", path.display(), e))?;
            }
        }
    } else {
        return Err(format!("Diretório de assets não encontrado: {}", source_assets_dir.display()));
    }
    
    Ok(())
}

#[cfg(target_os = "windows")]
fn download_and_install_npcap_sdk(vendor_dir: &Path) -> Result<(), String> {
    // URLs e caminhos
    let sdk_url = "https://npcap.com/dist/npcap-sdk-1.15.zip";
    let temp_dir = env::temp_dir();
    let zip_path = temp_dir.join("npcap-sdk.zip");
    let extract_dir = temp_dir.join("npcap-sdk");
    
    println!("cargo:warning=Baixando o SDK do Npcap de {}...", sdk_url);
    
    // Verifica se o diretório vendor existe, se não, cria-o
    if !vendor_dir.exists() {
        println!("cargo:warning=Criando diretório vendor...");
        fs::create_dir_all(vendor_dir).map_err(|e| format!("Erro ao criar diretório vendor: {}", e))?;
    }
    
    // Baixa o SDK usando curl ou powershell
    let download_result = if Command::new("where").arg("curl").status().is_ok() {
        println!("cargo:warning=Usando curl para download...");
        Command::new("curl")
            .args(["-L", sdk_url, "-o", zip_path.to_str().unwrap()])
            .status()
            .map_err(|e| format!("Falha ao executar curl: {}", e))
    } else {
        println!("cargo:warning=Usando PowerShell para download...");
        Command::new("powershell")
            .args([
                "-Command",
                &format!(
                    "Invoke-WebRequest -Uri '{}' -OutFile '{}'",
                    sdk_url,
                    zip_path.to_str().unwrap()
                ),
            ])
            .status()
            .map_err(|e| format!("Falha ao executar PowerShell: {}", e))
    };
    
    if let Err(e) = download_result {
        return Err(e);
    }
    
    let download_status = download_result.unwrap();
    if !download_status.success() {
        return Err(format!("Download falhou com código de saída: {}", download_status));
    }
    
    println!("cargo:warning=Download concluído. Extraindo...");
    
    // Cria diretório de extração se não existir
    if !extract_dir.exists() {
        fs::create_dir_all(&extract_dir).map_err(|e| format!("Erro ao criar diretório de extração: {}", e))?;
    }
    
    // Extrai o ZIP usando PowerShell
    let extract_status = Command::new("powershell")
        .args([
            "-Command",
            &format!(
                "Expand-Archive -Path '{}' -DestinationPath '{}' -Force",
                zip_path.to_str().unwrap(),
                extract_dir.to_str().unwrap()
            ),
        ])
        .status()
        .map_err(|e| format!("Falha ao extrair o ZIP: {}", e))?;
    
    if !extract_status.success() {
        return Err(format!("Extração falhou com código de saída: {}", extract_status));
    }
    
    println!("cargo:warning=Extração concluída. Copiando arquivos para {}...", vendor_dir.display());
    
    // Copia os arquivos para o diretório vendor usando PowerShell
    let copy_status = Command::new("powershell")
        .args([
            "-Command",
            &format!(
                "Copy-Item -Path '{}/*' -Destination '{}' -Recurse -Force",
                extract_dir.to_str().unwrap(),
                vendor_dir.to_str().unwrap()
            ),
        ])
        .status()
        .map_err(|e| format!("Falha ao copiar os arquivos: {}", e))?;
    
    if !copy_status.success() {
        return Err(format!("Cópia de arquivos falhou com código de saída: {}", copy_status));
    }
    
    println!("cargo:warning=SDK do Npcap instalado com sucesso em {}!", vendor_dir.display());
    
    // Limpeza dos arquivos temporários
    let _ = fs::remove_file(&zip_path);
    let _ = fs::remove_dir_all(&extract_dir);
    
    Ok(())
} 