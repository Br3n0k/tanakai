# Tanakai Client - Capturador de Pacotes para Albion Online

![Rust](https://img.shields.io/badge/Rust-1.56+-000000?style=flat-square&logo=rust)
![EGUI](https://img.shields.io/badge/EGUI-0.21+-4169E1?style=flat-square)
![Status](https://img.shields.io/badge/Status-Beta-orange?style=flat-square)

> Cliente desktop cyberpunk para captura e análise de pacotes do Albion Online

## 🔍 Visão Geral

O cliente Tanakai é um aplicativo desktop de alta performance desenvolvido em Rust que captura, decodifica e analisa pacotes do protocolo Photon utilizado pelo jogo Albion Online. Apresenta uma interface gráfica moderna com tema cyberpunk e se comunica com a API REST do servidor Tanakai para fornecer análises em tempo real.

## ✨ Características

- **Captura de Alta Performance**: Interceptação de pacotes com mínimo impacto no desempenho do jogo
- **Interface Gráfica Moderna**: UI cyberpunk desenvolvida com a biblioteca EGUI
- **Configuração Intuitiva**: Toda configuração feita através da interface gráfica
- **Análise em Tempo Real**: Processamento e visualização instantânea de dados do jogo
- **Identificação Segura**: Sistema HWID para conexão segura com a API
- **Multiplataforma**: Compatível com Windows, Linux e macOS
- **Atualizações Automáticas**: Verificação e instalação de atualizações via API

## 🖥️ Interface do Usuário

O cliente Tanakai possui uma interface gráfica completa dividida em várias seções:

### 📊 Dashboard Principal

![Dashboard](https://placeholder.com/dashboard.png)

- **Indicadores de Status**: Estado da captura, conexão com a API e desempenho
- **Estatísticas Gerais**: Pacotes capturados, eventos processados e taxas de transferência
- **Gráficos em Tempo Real**: Visualização de atividade e eventos importantes
- **Logs de Eventos**: Registro de atividades e notificações

### ⚙️ Configurações

- **Conexão**: URL da API, tokens de autenticação
- **Captura**: Seleção de interface de rede, filtros de pacotes
- **Aparência**: Personalização de tema e interface
- **Avançado**: Configurações de desempenho e debug

### 🔄 Captura de Dados

- **Lista de Interfaces**: Seleção da interface de rede para captura
- **Filtros**: Configuração de filtros para otimizar a captura
- **Visualização de Pacotes**: Inspeção detalhada de pacotes capturados
- **Estatísticas de Tráfego**: Análise do volume e tipos de pacotes

### 📈 Análise

- **Dados de Mercado**: Preços, tendências e histórico de itens
- **Eventos de Combate**: Estatísticas de batalhas e combates
- **Mapa de Atividade**: Visualização de atividades por região
- **Alertas Personalizados**: Configuração de notificações para eventos específicos

## 🔧 Requisitos do Sistema

### Windows
- Windows 10 64-bit ou superior
- 2GB RAM mínimo
- Drivers Npcap instalados
- Acesso de administrador (necessário para captura de pacotes)

### Linux
- Kernel 4.0 ou superior
- libpcap 1.9.0 ou superior
- 2GB RAM mínimo
- Permissões para captura de pacotes (geralmente requer sudo ou capabilities)

### macOS
- macOS 10.15 (Catalina) ou superior
- libpcap (incluído no sistema)
- 2GB RAM mínimo

## ⚙️ Instalação

### Instalação do Binário (Recomendado)

1. Baixe o instalador mais recente da [página de releases](https://github.com/tanakai/tanakai/releases)
2. Execute o instalador e siga as instruções na tela
3. Inicie o Tanakai a partir do menu de aplicativos ou atalho criado

### Compilação a partir do Código Fonte

#### Pré-requisitos

- Rust 1.56.0 ou superior
- Cargo (geralmente incluído com Rust)
- Dependências de sistema:
  - **Windows**: SDK do Npcap ou WinPcap
  - **Linux**: libpcap-dev
  - **macOS**: libpcap e ferramentas de desenvolvimento

#### Windows

```bash
# Instale o Npcap (https://npcap.com/#download)
# Clone o repositório
git clone https://github.com/tanakai/tanakai.git
cd tanakai/client

# Compilação
cargo build --release
```

##### Instalação do SDK do Npcap (Desenvolvimento)

O Tanakai tentará baixar e instalar automaticamente o SDK durante a compilação, mas você também pode:

1. Baixe o [SDK do Npcap](https://npcap.com/dist/npcap-sdk-1.15.zip)
2. Extraia para `vendor/npcap-sdk` dentro do projeto ou para `%ProgramFiles%\Npcap\SDK`

#### Linux

```bash
# Instale as dependências
sudo apt install libpcap-dev

# Clone o repositório
git clone https://github.com/tanakai/tanakai.git
cd tanakai/client

# Compilação
cargo build --release
```

#### macOS

```bash
# Instale as dependências
brew install libpcap

# Clone o repositório
git clone https://github.com/tanakai/tanakai.git
cd tanakai/client

# Compilação
cargo build --release
```

O executável compilado estará disponível em `target/release/tanakai`.

## 🚀 Uso

### Primeira Execução

1. Inicie o aplicativo Tanakai
2. Na primeira execução, o assistente de configuração será exibido automaticamente
3. Configure a URL da API e as credenciais (se necessário)
4. Selecione a interface de rede que o Albion Online utiliza
5. Clique em "Conectar" para iniciar a captura

### Configuração

A partir desta versão, **todas as configurações são feitas exclusivamente pela interface gráfica**. Não é mais necessário (ou possível) passar argumentos pela linha de comando como antes.

#### Local de Armazenamento da Configuração

- **Windows:** `%PROGRAMDATA%\Tanakai\config.json`
- **Linux/macOS:** `/etc/tanakai/config.json`

### Fluxo de Trabalho

1. O cliente verifica a existência de um arquivo de configuração válido
2. Se não encontrar, ou se houver problemas de conexão, exibe o assistente de configuração
3. Após configurado, inicia automaticamente a captura de pacotes
4. A interface exibe em tempo real as informações capturadas e processadas
5. Todas as alterações nas configurações são salvas instantaneamente

## 📁 Estrutura do Código

```
client/
├── src/
│   ├── api/                 # Comunicação com API REST
│   │   ├── client.rs        # Cliente HTTP
│   │   ├── endpoints.rs     # Definição de endpoints
│   │   └── mod.rs           # Módulo da API
│   ├── capture/             # Captura de pacotes
│   │   ├── device.rs        # Gerenciamento de dispositivos
│   │   ├── packet.rs        # Estruturas de pacotes
│   │   ├── sniffer.rs       # Captura e processamento
│   │   └── mod.rs           # Módulo de captura
│   ├── config/              # Configurações
│   │   ├── app_config.rs    # Estrutura de configuração
│   │   ├── serialization.rs # Serialização/deserialização
│   │   └── mod.rs           # Módulo de configuração
│   ├── hwid/                # Identificação de hardware
│   │   ├── generator.rs     # Geração de HWID
│   │   └── mod.rs           # Módulo de HWID
│   ├── models/              # Modelos de dados
│   │   ├── market.rs        # Dados do mercado
│   │   ├── player.rs        # Dados de jogadores
│   │   └── mod.rs           # Módulo de modelos
│   ├── photon/              # Processamento Photon
│   │   ├── decoder.rs       # Decodificação de pacotes
│   │   ├── parser.rs        # Análise de eventos
│   │   └── mod.rs           # Módulo Photon
│   ├── ui/                  # Interface de usuário
│   │   ├── components/      # Componentes reutilizáveis
│   │   │   ├── button.rs    # Botões personalizados
│   │   │   ├── card.rs      # Cards informativos
│   │   │   ├── header.rs    # Cabeçalho da aplicação
│   │   │   ├── sidebar.rs   # Barra lateral de navegação
│   │   │   ├── status.rs    # Indicadores de status
│   │   │   └── mod.rs       # Módulo de componentes
│   │   ├── dashboard/       # Interface principal
│   │   │   ├── charts.rs    # Gráficos e visualizações
│   │   │   ├── stats.rs     # Estatísticas e métricas
│   │   │   └── mod.rs       # Módulo de dashboard
│   │   ├── theme/           # Sistema de temas
│   │   │   ├── colors.rs    # Paleta de cores
│   │   │   ├── fonts.rs     # Configurações de fontes
│   │   │   └── mod.rs       # Módulo de tema
│   │   ├── windows/         # Gerenciamento de janelas
│   │   │   ├── config.rs    # Janela de configuração
│   │   │   ├── main.rs      # Janela principal
│   │   │   └── mod.rs       # Módulo de janelas
│   │   └── mod.rs           # Módulo de UI
│   ├── utils/               # Utilitários diversos
│   │   ├── logger.rs        # Sistema de logs
│   │   ├── updater.rs       # Atualizações automáticas
│   │   └── mod.rs           # Módulo de utilitários
│   └── main.rs              # Ponto de entrada
├── Cargo.toml               # Configuração do projeto
├── build.rs                 # Script de compilação
└── README.md                # Documentação
```

## 🔐 Segurança

O Tanakai Client implementa diversas medidas de segurança:

- **HWID**: Geração de identificador único de hardware para autenticação segura
- **Comunicação Segura**: Conexão HTTPS/TLS com a API
- **Token de Acesso**: Autenticação via token JWT
- **Acesso Limitado**: Captura apenas pacotes relevantes ao Albion Online
- **Sandboxing**: Isolamento do processo de captura para maior segurança

### Componentes do HWID

O identificador de hardware é gerado a partir de uma combinação de:
- Identificador da placa-mãe
- Endereço MAC da placa de rede principal
- Identificador do disco principal
- Identificador da GPU

## 🔄 Ciclo de Atualização

O cliente verifica automaticamente por atualizações ao iniciar e periodicamente durante a execução:

1. Consulta a API para verificar a versão mais recente
2. Caso uma nova versão esteja disponível, notifica o usuário
3. Se autorizado, baixa e instala a atualização
4. Reinicia automaticamente após a atualização

## 🛠️ Solução de Problemas

### Permissões de Captura

- **Windows**: Execute como administrador
- **Linux**: Use `sudo` ou configure as capabilities: `sudo setcap cap_net_raw,cap_net_admin=eip /caminho/para/tanakai`
- **macOS**: Autorize o acesso em Preferências do Sistema > Segurança e Privacidade

### Problemas Comuns

- **"Interface não encontrada"**: Verifique se o driver Npcap está instalado corretamente
- **"Erro ao conectar à API"**: Verifique a URL da API e sua conexão de internet
- **"Acesso negado"**: Execute como administrador ou verifique permissões
- **"HWID inválido"**: Contate o suporte se seu sistema estiver bloqueado

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, leia nossas [diretrizes de contribuição](../CONTRIBUTING.md) antes de enviar uma pull request.

## 📄 Licença

Este projeto está licenciado sob a [Licença MIT](../LICENSE).
