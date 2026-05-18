from fastapi import APIRouter

router = realms_router = APIRouter(prefix="/Realms", tags=["Realms"])


def _register_routes() -> None:
    from . import get_filters as _get_filters  # noqa: F401
    from . import get_landing_splash_info as _get_landing_splash_info  # noqa: F401
    from . import get_realms as _get_realms  # noqa: F401

_register_routes()
