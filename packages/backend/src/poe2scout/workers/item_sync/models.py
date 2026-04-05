from pydantic import BaseModel
from typing import Optional


class Item(BaseModel):
    type: str
    name: Optional[str] = None
    text: Optional[str] = None
    flags: Optional[dict] = None


class CurrencyItem(BaseModel):
    id: str
    image: Optional[str] = None
    text: str


class ItemCategory(BaseModel):
    id: str
    label: str
    entries: list[Item]


class CurrencyCategory(BaseModel):
    id: str
    label: Optional[str] = None
    entries: list[CurrencyItem]


class ItemResponse(BaseModel):
    result: list[ItemCategory]


class CurrencyResponse(BaseModel):
    result: list[CurrencyCategory]
