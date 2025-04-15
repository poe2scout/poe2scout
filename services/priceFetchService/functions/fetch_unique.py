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
    should_fetch_divines: bool
    quantity: int

class DivinePriceFetchResult(BaseModel):
    price: float
    quantity: int

def create_query_string(uniqueItem: UniqueItem, currencyText: str):
    query = {
        "query": {
            "status": {"option": "online"},
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

def filter_outliers(prices: List[float]) -> List[float]:
    if len(prices) < 5:
        return prices

    # Remove 1-value outliers
    non_one_prices = [p for p in prices if p != 1]

    if len(non_one_prices) >= 2:
        avg_non_one = sum(non_one_prices) / len(non_one_prices)
        threshold = avg_non_one * 0.5
        prices = [p for p in prices if p !=
                    1 or abs(p - avg_non_one) <= threshold]

    # Remove extreme outliers
    avg = sum(prices) / len(prices)
    filtered = [p for p in prices if avg/3 <= p <= avg*3]

    final_result = filtered if len(filtered) >= 3 else prices
    return final_result


async def fetch_unique(uniqueItem: UniqueItem, league: League, repo: ItemRepository, client: AsyncClient) -> PriceFetchResult:
    query_url = f"{BASE_URL}/search/{REALM}/{league.value}"
    # create query string
    query_data = create_query_string(uniqueItem, currencyText="exalted")

    divine_item = await repo.GetCurrencyItem("divine")
    divine_price = await repo.GetItemPrice(divine_item.itemId, league.id)

    if divine_price is None:
        logger.info("No price found for divine, using 100")
        divine_price = 100

    exalt_price_cutoff = divine_price * 0.7

    # Make first request to get the query id

    query_response = await client.post(query_url, json=query_data)
    if query_response.status_code != 200:
        raise Exception(f"Search request failed for {uniqueItem.name} with status code {query_response.status_code}")

    query_data = query_response.json()

    if len(query_data["result"]) == 0:
        logger.info(f"No results found for {uniqueItem.name} in {league}")
        return PriceFetchResult(price=-1, should_fetch_divines=True, quantity=0)

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

    if prices:
        prices = filter_outliers(prices)

    if len(prices) == 0:
        logger.info(f"No prices found for {uniqueItem.name} in {league}")
        return PriceFetchResult(price=-1, should_fetch_divines=True, quantity=0)
    
    should_fetch_divines =  (prices[0] >= exalt_price_cutoff) or len(prices) < 3

    return PriceFetchResult(price=prices[0], should_fetch_divines=should_fetch_divines, quantity=query_data['total'])

async def fetch_unique_divine(uniqueItem: UniqueItem, league: League, client: PoeTradeClient, repo: ItemRepository) -> DivinePriceFetchResult:
    query_url = f"{BASE_URL}/search/{REALM}/{league.value}"
    # create query string
    query_data = create_query_string(uniqueItem, currencyText="divine")

    # Make first request to get the query id

    query_response = await client.post(query_url, json=query_data)
    if query_response.status_code != 200:
        raise Exception(f"Search request failed for {uniqueItem.name} with status code {query_response.status_code}")

    query_data = query_response.json()

    if len(query_data["result"]) == 0:
        logger.info(f"No results found for {uniqueItem.name} in {league.value}")
        return DivinePriceFetchResult(price=-1, quantity=0)

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

    if prices:
        prices = filter_outliers(prices)

    if len(prices) == 0:
        logger.info(f"No prices found for {uniqueItem.name} in {league.value}")
        return DivinePriceFetchResult(price=-1, quantity=0)
    
    return DivinePriceFetchResult(price=prices[0], quantity=query_data['total'])


def remove_outliers(prices: List[float]) -> List[float]:
    """
    Removes outliers from price data using standard deviation method
    """
    if len(prices) < 4:  # Need at least 4 data points for meaningful outlier detection
        return prices

    avg = mean(prices)
    std = stdev(prices)

    # Keep prices within 2 standard deviations
    filtered_prices = [x for x in prices if (
        avg - 2 * std) <= x <= (avg + 2 * std)]

    # Return original if all filtered out
    return filtered_prices if filtered_prices else prices


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

            if amount is not None and (currency == 'exalted' or currency == 'regal' or currency == 'divine'):
                prices.append(float(amount))
        except (KeyError, AttributeError, ValueError):
            continue

    if not prices:
        return []

    # Remove outliers and get the lowest remaining price
    filtered_prices = remove_outliers(prices)
    return filtered_prices if filtered_prices else []



async def sync_metadata_and_icon(first_item: dict, uniqueItem: UniqueItem, repo: ItemRepository):
    itemMetadata = extract_unique_item_metadata(first_item)

    if uniqueItem.itemMetadata is None:
        await repo.SetUniqueItemMetadata(itemMetadata, uniqueItem.id)


    if uniqueItem.iconUrl is None:
        await repo.UpdateUniqueIconUrl(itemMetadata['icon'], uniqueItem.id)
