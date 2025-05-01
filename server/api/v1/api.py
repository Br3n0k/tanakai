from fastapi import APIRouter
from server.api.v1.endpoints import clients, mobs, items, harvestables

api_router = APIRouter()

api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(mobs.router, prefix="/mobs", tags=["mobs"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(harvestables.router, prefix="/harvestables", tags=["harvestables"]) 