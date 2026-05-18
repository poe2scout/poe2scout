from fastapi import APIRouter

router = leagues_router = APIRouter(prefix="/{Realm}/Leagues", tags=["Leagues"])


def _register_routes() -> None:
    from . import get as _get  # noqa: F401
    from . import get_exchange_snapshot as _get_exchange_snapshot  # noqa: F401
    from . import get_reference_currencies as _get_reference_currencies  # noqa: F401
    from . import get_snapshot_history as _get_snapshot_history  # noqa: F401
    from . import get_snapshot_pairs as _get_snapshot_pairs  # noqa: F401


_register_routes()
