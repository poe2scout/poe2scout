from typing import Self

from fastapi import APIRouter, HTTPException

from poe2scout.api.dependancies import ItemRepoDep
from poe2scout.api.api_model import ApiModel

router = static_router = APIRouter(prefix="/Static", tags=["Static"])


def _register_routes() -> None:
    from . import get_landing_splash_info  # noqa: F401
    from . import get_filters  # noqa: F401

_register_routes()