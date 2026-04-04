from fastapi import APIRouter

router = items_router = APIRouter(prefix="/Items", tags=["Items"])


def _register_routes() -> None:
    from . import get_categories  # noqa: F401

_register_routes()

__all__ = ["items_router"]
