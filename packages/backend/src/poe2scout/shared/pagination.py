from pydantic import BaseModel


class PaginationParams(BaseModel):
    page: int
    per_page: int
