from fastapi import APIRouter

router = uniques_router = APIRouter(
    prefix="/{Realm}/Leagues/{LeagueName}/Uniques", 
    tags=["Uniques"]
)


def _register_routes() -> None:
    from . import get_by_category as _uniques_get_by_category  # noqa: F401


_register_routes()
