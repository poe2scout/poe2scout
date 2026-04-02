from fastapi import APIRouter

router = currency_exchange_router = APIRouter(
    prefix="/CurrencyExchange",
    tags=["CurrencyExchange"],
)


def _register_routes() -> None:
    from . import get_current_snapshot  # noqa: F401
    from . import get_pair_history  # noqa: F401
    from . import get_snapshot_history  # noqa: F401
    from . import get_snapshot_pairs  # noqa: F401


_register_routes()

__all__ = ["currency_exchange_router"]
