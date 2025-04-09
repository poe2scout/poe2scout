from fastapi import Query, Depends
from typing import Optional
from dataclasses import dataclass
from pydantic import BaseModel

from services.repositories import ItemRepository


class PaginationParams(BaseModel):
    page: int
    perPage: int
    league: str

def get_pagination_params(
    page: int = Query(default=1, ge=1, description="Page number"),
    perPage: int = Query(default=25, ge=1, le=10000, description="Items per page"),
    league: str = Query(default="Standard", description="League name")
) -> PaginationParams:
    return PaginationParams(
        page=page,
        perPage=perPage,
        league=league
    )

def get_item_repository() -> ItemRepository:
    return _item_repository

_item_repository = ItemRepository()


class PaginatedResponse(BaseModel):
    currentPage: int
    pages: int
    total: int