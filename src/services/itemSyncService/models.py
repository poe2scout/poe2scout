from pydantic import BaseModel
from typing import Optional


class item(BaseModel):
    type: str
    name: Optional[str] = None
    text: Optional[str] = None
    flags: Optional[dict] = None


class currencyItem(BaseModel):
    id: str
    image: Optional[str] = None
    text: str


class itemCategory(BaseModel):
    id: str
    label: str
    entries: list[item]


class currencyCategory(BaseModel):
    id: str
    label: Optional[str] = None
    entries: list[currencyItem]


class itemResponse(BaseModel):
    result: list[itemCategory]


class currencyResponse(BaseModel):
    result: list[currencyCategory]
