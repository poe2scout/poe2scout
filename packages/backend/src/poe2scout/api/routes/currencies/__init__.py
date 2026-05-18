from fastapi import APIRouter

router = currencies_router = APIRouter(
    prefix="/{Realm}/Leagues/{LeagueName}/Currencies", 
    tags=["Currencies"]
)

def _register_routes() -> None:
    from . import get_by_category as _currencies_get_by_category  # noqa: F401
    from . import get as _currencies_get  # noqa: F401
    from . import get_pair_history as _currencies_get_pair_history  # noqa: F401

_register_routes()
