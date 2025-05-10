from fastapi import APIRouter
from server.schemas.regions import RegionList, Region

router = APIRouter()

@router.get("/", response_model=RegionList)
def get_regions():
    return RegionList(
        regions=[
            Region(name="America", tag="am", login="loginserver.live.albion.zone"),
            Region(name="Asia", tag="as", login="live02-loginserver.ams.albion.zone"),
            Region(name="Europe", tag="eu", login="live03-loginserver.ams.albion.zone")
        ]
    )