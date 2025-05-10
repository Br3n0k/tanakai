from fastapi import APIRouter
from server.api.v1.info import clients, mobs, items, harvestables, regions
from server.api.v1.client import hardware_id

api_router = APIRouter()

# Rotas de informação do cliente do albion online
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(harvestables.router, prefix="/harvestables", tags=["harvestables"]) 
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(mobs.router, prefix="/mobs", tags=["mobs"])
api_router.include_router(regions.router, prefix="/regions", tags=["regions"])

# Rotas de informação dos clientes tanakai
api_router.include_router(hardware_id.router, prefix="/client", tags=["client"])