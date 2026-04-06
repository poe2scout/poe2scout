from fastapi import APIRouter

router = leagues_router = APIRouter(prefix="/{Realm}/Leagues", tags=["Leagues"])


def _register_routes() -> None:
    from . import get as _get  # noqa: F401
    from . import get_exchange_snapshot as _get_exchange_snapshot  # noqa: F401
    from . import get_snapshot_history as _get_snapshot_history  # noqa: F401
    from . import get_snapshot_pairs as _get_snapshot_pairs  # noqa: F401
    from .currencies import get_by_category as _currencies_get_by_category  # noqa: F401
    from .currencies import get as _currencies_get  # noqa: F401
    from .currencies import get_pair_history as _currencies_get_pair_history  # noqa: F401
    from .items import get as _items_get  # noqa: F401
    from .items import get_price_histories as _items_get_price_histories  # noqa: F401
    from .items import get_price_history as _items_get_price_history  # noqa: F401
    from .uniques import get_by_category as _uniques_get_by_category  # noqa: F401


_register_routes()
