from fastapi import APIRouter

router = items_router = APIRouter(prefix="/Items", tags=["Items"])


def _register_routes() -> None:
    from . import get_currency_category_items  # noqa: F401
    from . import get_currency_item  # noqa: F401
    from . import get_filters  # noqa: F401
    from . import get_item_categories  # noqa: F401
    from . import get_item_histories  # noqa: F401
    from . import get_item_history  # noqa: F401
    from . import get_items  # noqa: F401
    from . import get_landing_splash_info  # noqa: F401
    from . import get_unique_category_items  # noqa: F401


_register_routes()

__all__ = ["items_router"]
