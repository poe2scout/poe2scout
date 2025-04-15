from typing import List, Tuple, Awaitable
from statistics import median
from itertools import chain
from httpx import AsyncClient
from pydantic import BaseModel
from services.repositories.item_repository import ItemRepository
from services.repositories.item_repository.GetLeagues import League
from services.repositories.item_repository.GetAllUniqueBaseItems import UniqueBaseItem
from .extract_base_item_metadata import extract_base_item_metadata
import logging
from services.libs.poe_trade_client import PoeTradeClient
from .fetch_unique import parse_trade_response, filter_outliers
logger = logging.getLogger(__name__)

BASE_URL = "https://www.pathofexile.com/api/trade2"
REALM = "poe2"

class PriceFetchResult(BaseModel):
    price: float
    quantity: int


def create_query_string(baseItem: UniqueBaseItem, currencyText: str):
    query = {
        "query": {
            "status": {"option": "online"},
            "type": baseItem.name,
            "stats": [{"type": "and", "filters": []}],
            "filters": {
                "type_filters": {
                    "disabled": False,
                    "filters": {
                        "rarity": {
                            "option": "normal"
                        }
                    }
                },
                "misc_filters": {
                    "disabled": False,
                    "filters": {
                        "alternate_art": {
                            "option": "false"
                        },
                        "corrupted": {
                            "option": "false"
                        },
                        "identified": {
                            "option": "true"
                        }
                    }
                },
                "trade_filters": {
                    "disabled": False,
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



async def fetch_base(baseItem: UniqueBaseItem, league: League, repo: ItemRepository, client: PoeTradeClient) -> PriceFetchResult:
    query_url = f"{BASE_URL}/search/{REALM}/{league.value}"
    # create query string
    query_data = create_query_string(baseItem, currencyText="exalted")
    logger.info(f"Query data: {query_data}")
    logger.info(f"Query url: {query_url}")

    # Make first request to get the query id

    query_response = await client.post(query_url, json=query_data)
    if query_response.status_code != 200:
        raise Exception(f"Search request failed for {baseItem.name} with status code {query_response.status_code}")

    query_data = query_response.json()

    if len(query_data["result"]) == 0:
        logger.info(f"No results found for {baseItem.name} in {league}")
        return PriceFetchResult(price=-1, quantity=0)

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
        raise Exception(f"Fetch request failed for {baseItem.name} with status code {fetch_response.status_code}")

    fetch_data = fetch_response.json()

    await sync_metadata_and_icon(fetch_data['result'][0]['item'], baseItem, repo)

    prices = parse_trade_response(fetch_data)

    if prices:
        prices = filter_outliers(prices)

    if len(prices) == 0:
        logger.info(f"No prices found for {baseItem.name} in {league}")
        return PriceFetchResult(price=-1, quantity=0)
    
    return PriceFetchResult(price=prices[0], quantity=query_data['total'])

async def sync_metadata_and_icon(first_item: dict, baseItem: UniqueBaseItem, repo: ItemRepository):
    itemMetadata = extract_base_item_metadata(first_item)

    if baseItem.itemMetadata is None:
        await repo.SetBaseItemMetadata(itemMetadata, baseItem.id)

    if baseItem.iconUrl is None:
        await repo.UpdateBaseItemIconUrl(itemMetadata['icon'], baseItem.id)
