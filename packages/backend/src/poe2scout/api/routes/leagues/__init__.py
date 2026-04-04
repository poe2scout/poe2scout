from typing import Self

from fastapi import APIRouter, HTTPException

from poe2scout.api.dependancies import ItemRepoDep
from poe2scout.api.api_model import ApiModel

router = leagues_router = APIRouter(prefix="/Leagues", tags=["Leagues"])


def _register_routes() -> None:
    from . import get  # noqa: F401
    from . import get_exchange_snapshot  # noqa: F401
    from . import get_snapshot_history  # noqa: F401
    from . import get_snapshot_pairs  # noqa: F401
    from .currencies import get_by_category  # noqa: F401
    from .currencies import get_pair_history  # noqa: F401
    from .currencies import get  # noqa: F401
    from .items import get  # noqa: F401
    from .items import get_price_history  # noqa: F401
    from .items import get_price_histories  # noqa: F401
    from .uniques import get_by_category  # noqa: F401


_register_routes()
