"""League-scoped item routes."""

from fastapi import APIRouter


router = items_router = APIRouter(prefix="/{Realm}/Leagues/{LeagueName}/Items", tags=["Items"])


def _register_routes() -> None:
    from . import get as _items_get  # noqa: F401
    from . import get_categories as _items_get_categories # noqa: F401
    from . import get_daily_stats_history as _items_get_daily_stats_history  # noqa: F401
    from . import get_price_histories as _items_get_price_histories  # noqa: F401
    from . import get_by_id as _items_get_by_id  # noqa: F401
    from . import get_price_history as _items_get_price_history  # noqa: F401

_register_routes()
