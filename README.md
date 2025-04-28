# Tanakai - Photon Packet Sniffer

## Descrição

- Tanakai é um sniffer de pacotes especializado para o protocolo Photon utilizado pelo jogo Albion Online. Escrito em Rust para alta performance, o Tanakai captura, decodifica e analisa pacotes do jogo, enviando eventos relevantes dentro do jogo sua API REST FULL.

## Eventos capturados

- Login
- Logout
- Mercado:
-- Valores de itens
-- Disponibilidade de itens
-- Taxas de mercado
-- Compras e vendas de itens
- Combate
-- Morte
-- Dano
-- Estatisticas de Batalha

## Características

- **Alto Desempenho**: Desenvolvido em Rust para máxima eficiência e uso mínimo de recursos
- **Sistema HWID**: Identificação de hardware para controle e segurança
- **Análise Discreta**: Execução em segundo plano sem impacto na experiência do jogo
- **API REST**: Integração com backend para processamento e armazenamento de dados
- **Multiplataforma**: Suporte para Windows, macOS e Linux

## Instalação

### Pré-requisitos

- Rust 1.56.0 ou superior
- Biblioteca libpcap (Windows: Npcap, Linux: libpcap-dev, macOS: libpcap)

### Compilação

```bash
# Clone o repositório
git clone https://github.com/tanakai/tanakai.git
cd tanakai

# Compilação em modo release
cargo build --release
```

O executável estará disponível em `target/release/tanakai`.

### Instalação de Dependências

#### Windows

**IMPORTANTE**: Para compilar o Tanakai, é necessário instalar a versão para desenvolvedor do Npcap que inclui as bibliotecas de desenvolvimento.

> **Nota**: O Tanakai tentará baixar e instalar automaticamente o SDK do Npcap durante a compilação caso ele não seja encontrado em seu sistema. O SDK será baixado para o diretório `vendor/npcap-sdk` dentro do projeto.

1. Baixe e instale o [Npcap](https://npcap.com/#download) em modo WinPcap compatível.
2. Para desenvolvimento, você precisa do SDK do Npcap, disponível em [Npcap SDK](https://npcap.com/dist/npcap-sdk-1.15.zip)
3. Caso o download automático falhe, você pode extrair manualmente o conteúdo do SDK para:
   - `vendor/npcap-sdk` dentro do projeto, ou
   - `%ProgramFiles%\Npcap\SDK` (geralmente C:\Program Files\Npcap\SDK)

**Alternativa**: Instale o [WinPcap Developer's Pack](https://www.winpcap.org/devel.htm) e certifique-se de que os arquivos estão em `%ProgramFiles%\WinPcap\`

#### Linux

```bash
sudo apt install libpcap-dev
```

#### macOS

```bash
brew install libpcap
```

## Uso

```bash
# Execução básica (detecta interface automaticamente)
./tanakai

# Especificar interface de rede
./tanakai -i eth0

# Especificar URL da API
./tanakai -a http://api.exemplo.com

# Modo silencioso
./tanakai -q
```

### Argumentos

- `-i, --interface`: Interface de rede a ser monitorada
- `-a, --api_url`: URL da API para envio de dados (padrão: "<http://api.tanakai.io/v1>")
- `-q, --quiet`: Execução em modo silencioso (sem logs informativos)

## Arquitetura

O Tanakai é organizado nos seguintes módulos:

- **api**: Cliente para comunicação com a API REST
- **capture**: Captura e processamento de pacotes de rede
- **config**: Configurações centralizadas
- **hwid**: Sistema de identificação de hardware
- **models**: Modelos de dados
- **photon**: Processamento do protocolo Photon
- **utils**: Utilitários diversos

## Segurança

O Tanakai inclui um sistema de HWID (Hardware ID) para segurança e prevenção de abusos. O sistema gera um identificador único baseado em:

- Identificador da placa-mãe
- Identificador da placa de rede
- Identificador do disco rígido
- Identificador da placa de vídeo

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

## Contribuição

Contribuições são bem-vindas! Por favor, sinta-se à vontade para enviar pull requests, relatar problemas ou sugerir melhorias.
