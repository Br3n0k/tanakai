import os
import sys

# Impede criação dos arquivos de cache
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["PYTHONUNBUFFERED"] = "1"
sys.dont_write_bytecode = True

# Define o diretório base do projeto
os.environ["TANAKAI"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Adiciona o diretório base ao sys.path
sys.path.append(os.environ["TANAKAI"])

# Define algumas variaveis de ambiente para o projeto
os.environ["TANAKAI_SERVER"] = os.path.join(os.environ["TANAKAI"], "server")
os.environ["TANAKAI_DUMPS"] = os.path.join(os.environ["TANAKAI"], "dumps")
os.environ["TANAKAI_ASSETS"] = os.path.join(os.environ["TANAKAI"], "assets")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from server.core.config import settings
from server.api.v1.api import api_router

from server.utils import get_dumps

# Faz o download dos dumps do albion online
get_dumps()

# Procedimentos do banco de dados
# Importa e usa a função de inicialização do banco de dados
import logging
from server.db.initialize import check_and_initialize_database

# Configura o logging básico se ainda não estiver configurado
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("server")

# Verifica e inicializa o banco de dados
logger.info(f"Diretório base do projeto: {os.environ['TANAKAI']}")
logger.info(f"URI do banco de dados: {settings.SQLALCHEMY_DATABASE_URI}")
if not check_and_initialize_database():
    logger.error("Erro ao inicializar o banco de dados. Aplicação não pode continuar.")
    sys.exit(1)
else:
    logger.info("Banco de dados inicializado com sucesso!")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Monta os arquivos estáticos
app.mount("/static", StaticFiles(directory=os.environ["TANAKAI_ASSETS"]), name="static")

# Configuração CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join(os.environ["TANAKAI_ASSETS"], "icon.ico"))

@app.get("/")
def root():
    return {"message": "Bem-vindo à API do Tanakai"}

@app.get("/health")
def health():
    return {
        # Status - live | down | maintenance
        "status": "live",
        # Versão do projeto
        "version": settings.VERSION,
        # Nome do projeto
        "project": settings.PROJECT_NAME
    }