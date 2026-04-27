from poe2scout.db.repositories import unique_item_repository
from poe2scout.db.repositories.unique_item_repository.get_all_unique_items import UniqueItem
from httpx import AsyncClient
import logging
from typing import List
from pydantic import BaseModel
from poe2scout.db.repositories.league_repository.get_leagues import League
from poe2scout.integrations.poe.client import ClientError
from .extract_unique_item_metadata import extract_unique_item_metadata
from ..exceptions import UniqueItemDelistedError

logger = logging.getLogger(__name__)

BASE_URL = "https://www.pathofexile.com/api/trade2"
REALM = "poe2"


class PriceFetchResult(BaseModel):
    price: float
    quantity: int
    currency: str


def create_query_string(unique_item: UniqueItem, currency_text: str):
    if unique_item.category_api_id == "jewel":
        return {
            "query": {
                "status": {"option": "securable"},
                "name": unique_item.name,
                "stats": [{"type": "and", "filters": []}],
                "filters": {
                    "trade_filters": {"filters": {"price": {"option": currency_text}}}
                },
            },
            "sort": {"price": "asc"}
        }
    
    return {
        "query": {
            "status": {"option": "securable"},
            "name": unique_item.name,
            "stats": [{"type": "and", "filters": []}],
            "filters": {
                "trade_filters": {"filters": {"price": {"option": currency_text}}},
                "misc_filters": {"filters": {"corrupted": {"option": "false"}}}
            },
        },
        "sort": {"price": "asc"},
    }

async def fetch_unique(
    unique_item: UniqueItem,
    league: League,
    client: AsyncClient,
    currency: str,
) -> PriceFetchResult:
    query_url = f"{BASE_URL}/search/{REALM}/{league.value}"
    query_data = create_query_string(unique_item, currency_text=currency)

    # Make first request to get the query id
    try:
        query_response = await client.post(query_url, json=query_data)
    except ClientError as exc:
        raise_for_delisted_unique(unique_item, exc)
        raise

    query_data = query_response.json()

    if len(query_data["result"]) == 0:
        logger.info(f"No results found for {unique_item.name} in {league}")
        return PriceFetchResult(price=-1, quantity=0, currency=currency)

    item_ids = query_data["result"][:10]

    # Second request - GET items
    items_url = f"{BASE_URL}/fetch/{','.join(item_ids)}"
    params = {"query": query_data["id"], "realm": REALM}
    try:
        fetch_response = await client.get(items_url, params=params)
    except ClientError as exc:
        raise_for_delisted_unique(unique_item, exc)
        raise

    fetch_data = fetch_response.json()

    if None not in fetch_data["result"]:
        await sync_metadata_and_icon(fetch_data["result"][0]["item"], unique_item)

    prices = parse_trade_response(fetch_data)

    if len(prices) == 0:
        logger.info(f"No prices found for {unique_item.name} in {league}")
        return PriceFetchResult(price=-1, quantity=0, currency=currency)

    return PriceFetchResult(
        price=prices[0], quantity=query_data["total"], currency=currency
    )


def raise_for_delisted_unique(unique_item: UniqueItem, error: ClientError) -> None:
    error_message = str(error)
    if "Status Code: 400" in error_message and "Unknown item name" in error_message:
        raise UniqueItemDelistedError(unique_item.unique_item_id, unique_item.name) from error


def parse_trade_response(response_data: dict) -> List[float]:
    """
    Parses the trade API response and returns a list of prices in exalts
    """
    if not response_data or "result" not in response_data:
        return []

    prices = []
    for result in response_data.get("result", []):
        try:
            listing_data = result.get("listing", {})
            price_data = listing_data.get("price", {})

            amount = price_data.get("amount")

            if amount is not None:
                prices.append(float(amount))
        except (KeyError, AttributeError, ValueError):
            continue

    if not prices:
        return []

    return prices


async def sync_metadata_and_icon(
    first_item: dict,
    unique_item: UniqueItem,
):
    item_metadata = extract_unique_item_metadata(first_item)

    if unique_item.item_metadata is None:
        await unique_item_repository.set_unique_item_metadata(
            item_metadata,
            unique_item.unique_item_id,
        )

    if unique_item.icon_url is None:
        await unique_item_repository.update_unique_icon_url(
            item_metadata["icon"],
            unique_item.unique_item_id,
        )
