from pydantic import BaseModel


class PaginationParams(BaseModel):
    page: int
    perPage: int
    league: str
