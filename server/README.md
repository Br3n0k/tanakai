# Tanakai Server - API REST para Albion Online

![FastAPI](https://img.shields.io/badge/FastAPI-0.95.0-009485?style=flat-square&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-336791?style=flat-square&logo=postgresql)

> API REST completa para processamento, armazenamento e análise de dados do Albion Online

## 📋 Visão Geral

O servidor Tanakai é o componente responsável por processar, armazenar e disponibilizar dados capturados do jogo Albion Online. Desenvolvido com FastAPI para alto desempenho e baixa latência, oferece uma API REST completa para consumo de informações do jogo.

## 🚀 Funcionalidades

- **Processamento de Dados**: Recebimento e processamento de eventos do jogo
- **Persistência**: Armazenamento de longo prazo para análise histórica
- **API Completa**: Endpoints RESTful para todos os dados coletados
- **Documentação Automática**: Swagger UI e ReDoc integrados
- **Autenticação**: Sistema seguro de autenticação e autorização
- **Rate Limiting**: Controle de taxa de requisições para prevenção de abusos
- **Gerenciamento de Clientes**: Controle de licenças e tokens via HWID

## 📦 Módulos Principais

- **API (v1)**: Endpoints de acesso aos dados
  - **Clientes**: Gerenciamento de clientes Tanakai
  - **Itens**: Informações sobre itens do jogo
  - **Mercado**: Preços, histórico e volume de negociação
  - **Mobs**: Dados sobre criaturas, atributos e drops
  - **Jogadores**: Informações sobre jogadores e estatísticas
  - **Eventos**: Registro de eventos do mundo (PvP, GvG, ZvZ)

- **Core**: Configuração e segurança do sistema
- **DB**: Acesso e modelos de banco de dados
- **Services**: Lógica de negócio e processamento
- **Schemas**: Validação e serialização de dados
- **Utils**: Ferramentas utilitárias e auxiliares

## 🔧 Requisitos

- Python 3.9+
- PostgreSQL 12+
- 4GB RAM (recomendado)
- 20GB espaço em disco (mínimo)
- Conexão à Internet

## ⚙️ Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/tanakai/tanakai.git
cd tanakai/server
```

### 2. Ambiente Virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 3. Dependências

```bash
pip install -r requirements.txt
```

### 4. Configuração

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite as variáveis de ambiente
nano .env  # ou use seu editor preferido
```

#### Variáveis de Ambiente Necessárias

```
# Configuração do Banco de Dados
DATABASE_URL=postgresql://user:password@localhost/tanakai

# Segurança
SECRET_KEY=sua_chave_secreta_super_segura
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

# API
API_V1_STR=/api/v1
PROJECT_NAME=Tanakai
VERSION=1.0.0
BACKEND_CORS_ORIGINS=["http://localhost", "http://localhost:8080"]

# Logs
LOG_LEVEL=INFO
```

### 5. Banco de Dados

```bash
# Crie o banco de dados PostgreSQL
createdb tanakai

# Execute as migrações
alembic upgrade head
```

### 6. Execute a API

```bash
# Desenvolvimento
uvicorn server.main:app --reload --host 0.0.0.0 --port 8000

# Produção
uvicorn server.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🌐 Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | /api/v1/clients/ | Lista todos os clientes |
| POST | /api/v1/clients/ | Registra novo cliente |
| GET | /api/v1/clients/{id} | Obtém detalhes de um cliente |
| PUT | /api/v1/clients/{id} | Atualiza cliente existente |
| DELETE | /api/v1/clients/{id} | Remove um cliente |
| GET | /api/v1/items/ | Lista todos os itens |
| GET | /api/v1/items/{id} | Obtém detalhes de um item |
| GET | /api/v1/market/prices | Preços atuais do mercado |
| GET | /api/v1/market/history/{item_id} | Histórico de preços |
| GET | /api/v1/mobs/ | Lista mobs com filtros |
| GET | /api/v1/mobs/{id} | Detalhes de um mob específico |
| GET | /api/v1/mobs/stats | Estatísticas de mobs |
| GET | /api/v1/mobs/search/{term} | Busca mobs por termo |

## 📁 Estrutura do Projeto

```
server/
├── alembic/                  # Migrações de banco de dados
├── server/                   # Código principal
│   ├── api/                  # API e endpoints
│   │   ├── deps.py           # Dependências para injeção
│   │   └── v1/               # Versão 1 da API
│   │       ├── api.py        # Definição de rotas
│   │       └── endpoints/    # Endpoints por recurso
│   │           ├── clients.py
│   │           ├── items.py
│   │           ├── market.py
│   │           └── mobs.py
│   ├── core/                 # Núcleo da aplicação
│   │   ├── config.py         # Configurações
│   │   └── security.py       # Autenticação e segurança
│   ├── db/                   # Acesso ao banco de dados
│   │   └── base.py           # Configuração do SQLAlchemy
│   ├── models/               # Modelos SQLAlchemy
│   │   ├── client.py
│   │   ├── item.py
│   │   └── market.py
│   ├── schemas/              # Modelos Pydantic
│   │   ├── client.py
│   │   ├── item.py
│   │   ├── mobs.py
│   │   └── market.py
│   ├── services/             # Lógica de negócio
│   │   ├── client.py
│   │   └── item.py
│   ├── utils/                # Utilidades
│   │   ├── check_xml.py
│   │   ├── get_dumps.py
│   │   └── read_mobs.py
│   └── main.py               # Ponto de entrada
├── tests/                    # Testes
├── .env                      # Variáveis de ambiente
├── .env.example              # Exemplo de variáveis
├── requirements.txt          # Dependências
└── README.md
```

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Executar com relatório de cobertura
pytest --cov=server tests/
```

## 📋 Logs e Monitoramento

Os logs são armazenados em `logs/tanakai.log` e incluem:

- Requisições e respostas da API
- Erros e exceções
- Eventos do sistema
- Estatísticas de performance

## 🔄 Atualização de Dados do Jogo

O servidor possui rotinas automáticas para atualizar dados do jogo:

```bash
# Atualização manual dos arquivos XML do jogo
python -m server.utils.get_dumps

# Processar dados de mobs
python -m server.utils.read_mobs
```

## 📚 Documentação

A documentação da API está disponível em:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🛡️ Segurança

O servidor utiliza:

- Autenticação JWT
- CORS configurável
- Rate limiting por IP e por cliente
- Validação de HWID
- Sanitização de inputs

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/sua-feature`)
3. Faça commit das alterações (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/sua-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a [Licença MIT](../LICENSE).
