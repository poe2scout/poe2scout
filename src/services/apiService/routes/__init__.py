from fastapi import APIRouter

# Create routers
# Import route handlers
from .item_route import router as item_router
from .league_route import router as league_router
from .currency_exchange_route import router as currency_exchange_router
