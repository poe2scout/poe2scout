from services.repositories.item_repository import ItemRepository
from services.repositories.item_repository.GetAllUniqueItems import UniqueItem
from services.repositories.item_repository.GetAllCurrencyItems import CurrencyItem
from httpx import AsyncClient
import logging
from typing import Tuple, List
from statistics import mean, stdev
from pydantic import BaseModel
from typing import Awaitable
from services.repositories.item_repository.GetLeagues import League
from .extract_unique_item_metadata import extract_unique_item_metadata
from services.libs.poe_trade_client import PoeTradeClient
logger = logging.getLogger(__name__)

BASE_URL = "https://www.pathofexile.com/api/trade2"
REALM = "poe2"

class PriceFetchResult(BaseModel):
    price: float
    quantity: int
    currency: str

def create_query_string(uniqueItem: UniqueItem, currencyText: str):
    query = {
        "query": {
            "status": {"option": "securable"},
            "name": uniqueItem.name,
            "stats": [{"type": "and", "filters": []}],
            "filters": {
                "trade_filters": {
                    "filters": {
                        "price": {
                            "option": currencyText
                        }
                    }
                }
            }
        },
        "sort": {"price": "asc"},
    }

    return query

async def fetch_unique(uniqueItem: UniqueItem, league: League, repo: ItemRepository, client: AsyncClient, currency: str) -> PriceFetchResult:
    query_url = f"{BASE_URL}/search/{REALM}/{league.value}"
    # create query string
    query_data = create_query_string(uniqueItem, currencyText=currency)

    # Make first request to get the query id
    query_response = await client.post(query_url, json=query_data)
    if query_response.status_code != 200:
        raise Exception(f"Search request failed for {uniqueItem.name} with status code {query_response.status_code}")

    query_data = query_response.json()

    if len(query_data["result"]) == 0:
        logger.info(f"No results found for {uniqueItem.name} in {league}")
        return PriceFetchResult(price=-1, quantity=0, currency=currency)

    item_ids = query_data['result'][:10]

    # Second request - GET items
    items_url = f"{BASE_URL}/fetch/{','.join(item_ids)}"
    params = {
        "query": query_data['id'],
        "realm": REALM
    }
    fetch_response = await client.get(
        items_url, params=params)

    if fetch_response.status_code != 200:
        raise Exception(f"Fetch request failed for {uniqueItem.name} with status code {fetch_response.status_code}")

    fetch_data = fetch_response.json()

    await sync_metadata_and_icon(fetch_data['result'][0]['item'], uniqueItem, repo)

    prices = parse_trade_response(fetch_data)

    if len(prices) == 0:
        logger.info(f"No prices found for {uniqueItem.name} in {league}")
        return PriceFetchResult(price=-1, quantity=0, currency=currency)
    
    return PriceFetchResult(price=prices[0], quantity=query_data['total'], currency=currency)


def parse_trade_response(response_data: dict) -> List[float]:
    """
    Parses the trade API response and returns a list of prices in exalts
    """
    if not response_data or 'result' not in response_data:
        return []

    prices = []
    for result in response_data.get('result', []):
        try:
            listing_data = result.get('listing', {})
            price_data = listing_data.get('price', {})

            amount = price_data.get('amount')
            currency = price_data.get('currency')

            if amount is not None:
                prices.append(float(amount))
        except (KeyError, AttributeError, ValueError):
            continue

    if not prices:
        return []

    return prices



async def sync_metadata_and_icon(first_item: dict, uniqueItem: UniqueItem, repo: ItemRepository):
    itemMetadata = extract_unique_item_metadata(first_item)

    if uniqueItem.itemMetadata is None:
        await repo.SetUniqueItemMetadata(itemMetadata, uniqueItem.id)


    if uniqueItem.iconUrl is None:
        await repo.UpdateUniqueIconUrl(itemMetadata['icon'], uniqueItem.id)
