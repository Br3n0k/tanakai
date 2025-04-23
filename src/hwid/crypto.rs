use aes_gcm::{
    aead::{Aead, AeadCore, KeyInit, OsRng},
    Aes256Gcm, Key, Nonce
};
use base64::{Engine as _, engine::general_purpose};
use sha2::{Sha256, Digest};
use log::{debug, error};
use once_cell::sync::Lazy;

// Chave mestra usada para encriptar IDs (em produção, deveria ser obtida de uma fonte segura)
static MASTER_KEY: Lazy<Key<Aes256Gcm>> = Lazy::new(|| {
    // Em produção, essa chave poderia ser carregada de uma variável de ambiente ou arquivo seguro
    let key_string = "tanakai-security-key-never-share-this-key-12345";
    let mut hasher = Sha256::new();
    hasher.update(key_string.as_bytes());
    let result = hasher.finalize();
    
    *Key::<Aes256Gcm>::from_slice(&result)
});

// Cipher AES-GCM para criptografia
static CIPHER: Lazy<Aes256Gcm> = Lazy::new(|| {
    Aes256Gcm::new(&MASTER_KEY)
});

/// Encripta um identificador
pub fn encrypt_id(id: &str) -> String {
    // Gera um nonce aleatório
    let nonce = Aes256Gcm::generate_nonce(&mut OsRng);
    
    // Encripta o ID
    match CIPHER.encrypt(&nonce, id.as_bytes().as_ref()) {
        Ok(ciphertext) => {
            // Concatena o nonce com o texto cifrado
            let mut result = nonce.to_vec();
            result.extend_from_slice(&ciphertext);
            
            // Converte para Base64 para facilitar armazenamento
            general_purpose::URL_SAFE_NO_PAD.encode(result)
        },
        Err(e) => {
            // Em caso de erro, usamos um hash do ID original
            error!("Erro ao encriptar ID: {}", e);
            let mut hasher = Sha256::new();
            hasher.update(id.as_bytes());
            let result = hasher.finalize();
            
            // Usa apenas os primeiros 16 bytes para manter um tamanho razoável
            general_purpose::URL_SAFE_NO_PAD.encode(&result[..16])
        }
    }
}

/// Decripta um identificador
#[allow(dead_code)]
pub fn decrypt_id(encrypted_id: &str) -> Option<String> {
    // Decodifica o Base64
    let encrypted_data = match general_purpose::URL_SAFE_NO_PAD.decode(encrypted_id) {
        Ok(data) => data,
        Err(e) => {
            debug!("Erro ao decodificar ID Base64: {}", e);
            return None;
        }
    };
    
    // Verifica se temos dados suficientes (nonce + ciphertext)
    if encrypted_data.len() <= 12 {
        debug!("Dados encriptados muito curtos");
        return None;
    }
    
    // Extrai o nonce (primeiros 12 bytes)
    let nonce = Nonce::from_slice(&encrypted_data[..12]);
    
    // Extrai o texto cifrado (resto dos bytes)
    let ciphertext = &encrypted_data[12..];
    
    // Tenta decriptar
    match CIPHER.decrypt(nonce, ciphertext.as_ref()) {
        Ok(plaintext) => {
            // Converte de volta para string
            match String::from_utf8(plaintext) {
                Ok(id) => Some(id),
                Err(e) => {
                    debug!("Erro ao converter plaintext para UTF-8: {}", e);
                    None
                }
            }
        },
        Err(e) => {
            debug!("Erro ao decriptar ID: {}", e);
            None
        }
    }
} 