# Tanakai - Analisador de Pacotes para Albion Online

![Logo Tanakai](https://placeholder.com/logo.png)

> Uma solução completa para captura, análise e exibição de dados do jogo Albion Online.

## Visão Geral

Tanakai é um sistema completo de captura e análise de pacotes do protocolo Photon utilizado pelo jogo Albion Online. O projeto adota uma arquitetura cliente-servidor:

- **Cliente**: Aplicação desktop em Rust com interface gráfica cyberpunk que captura pacotes de rede.
- **Servidor**: API REST em Python com FastAPI que processa, armazena e disponibiliza dados úteis do jogo.

## Principais Funcionalidades

- 🕵️ **Captura de Pacotes**: Interceptação e decodificação de pacotes do protocolo Photon
- 📊 **Análise de Dados**: Processamento de eventos e dados do jogo
- 🔍 **Informações de Mercado**: Valores, disponibilidade e histórico de itens
- ⚔️ **Estatísticas de Combate**: Análise detalhada de combates e eventos PvP
- 🗺️ **Dados do Mundo**: Mobs, recursos, conteúdo PvE e mais
- 🔧 **Configuração Flexível**: Interface gráfica para configuração completa

## Estrutura do Projeto

O Tanakai é dividido em dois componentes principais:

### [📱 Cliente](/client/)

- Captura pacotes de rede em tempo real com alta performance
- Interface gráfica moderna com tema cyberpunk
- Sistema de HWID para gerenciamento de licenças
- Conexão segura com o servidor
- [Leia mais sobre o cliente](/client/README.md)

### [🖥️ Servidor](/server/)

- API REST completa para processamento e armazenamento de dados
- Banco de dados para histórico de preços e eventos
- Busca avançada de itens, mobs e recursos
- Autenticação e gerenciamento de clientes
- [Leia mais sobre o servidor](/server/README.md)

## Informações Capturadas

O sistema Tanakai captura e processa diversos tipos de informações do jogo:

| Categoria | Dados Capturados |
|-----------|------------------|
| Mercado | Preços de itens, histórico, volume de transações |
| Combate | Estatísticas de batalha, mortes, assistências |
| Jogadores | Atividades, equipamentos, alianças, guildas |
| Recursos | Localizações, níveis, tempos de respawn |
| Mobs | Atributos, drops, localizações |

## Instalação Rápida

```bash
# Clone o repositório
git clone https://github.com/tanakai/tanakai.git
cd tanakai

# Configure o servidor (API)
cd server
python -m venv venv
source venv/bin/activate  # ou "venv\Scripts\activate" no Windows
pip install -r requirements.txt
uvicorn server.main:app --reload

# Em outro terminal, compile o cliente
cd client
cargo build --release
```

Para instruções detalhadas, consulte os READMEs de cada componente.

## Requisitos do Sistema

### Cliente

- Sistema Operacional: Windows 10/11, Ubuntu 20.04+, macOS 12+
- Memória: 2GB RAM mínimo
- Drivers: Npcap (Windows) ou libpcap (Linux/macOS)

### Servidor

- Python 3.9+
- PostgreSQL 12+
- 4GB RAM recomendado
- 20GB espaço em disco

## Contribuindo

Contribuições são bem-vindas! Por favor, leia nossas [diretrizes de contribuição](CONTRIBUTING.md) antes de enviar uma pull request.

## Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE) - veja o arquivo LICENSE para detalhes.

## Contato e Suporte

- Discord: n0k0606
- GitHub: [Reportar Problemas](https://github.com/tanakai/tanakai/issues)
- Email: <br3n0k@gmail.com>
