from pydantic import BaseModel
from typing import List

class Region(BaseModel):
    name: str
    tag: str
    login: str

class RegionList(BaseModel):
    regions: List[Region]


