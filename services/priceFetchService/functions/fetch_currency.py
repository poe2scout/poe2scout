from typing import List, Tuple, Awaitable
from statistics import median
from itertools import chain
from httpx import AsyncClient
from pydantic import BaseModel
from services.repositories.item_repository import ItemRepository
from services.repositories.item_repository.GetLeagues import League
from services.repositories.item_repository.GetAllCurrencyItems import CurrencyItem
from .extract_currency_item_metadata import extract_currency_item_metadata
import logging
from services.libs.poe_trade_client import PoeTradeClient
logger = logging.getLogger(__name__)

BASE_URL = "https://www.pathofexile.com/api/trade2"
REALM = "poe2"

class CurrencyPriceFetchResult(BaseModel):
    price: float
    quantity: int

def create_currency_exchange_query(want_currency_api_id: str, have_currency_api_ids: List[str]) -> dict:
    logger.debug(f"Creating currency exchange query for want: {want_currency_api_id}, have: {have_currency_api_ids}")
    return {
        "query": {
            "status": {
                "option": "online"
            },
            "have": have_currency_api_ids,
            "want": [want_currency_api_id]
        },
        "sort": {
            "have": "asc"
        },
        "engine": "new"
    }


def weighted_median(values: List[Tuple[float, int]]) -> float:
    logger.debug(f"Calculating weighted median for {len(values)} values")
    # Expand values based on weights
    expanded = list(chain.from_iterable(
        [value] * weight for value, weight in values))
    if not expanded:
        logger.warning("No values to calculate weighted median")
        return 0
    result = median(expanded)
    logger.debug(f"Weighted median calculated: {result}")
    return result


def weighted_stdev(values: List[Tuple[float, int]], weighted_med: float) -> float:
    logger.debug(f"Calculating weighted standard deviation for {len(values)} values")
    if not values:
        logger.warning("No values to calculate weighted standard deviation")
        return 0

    total_weight = sum(weight for _, weight in values)
    if total_weight == 0:
        logger.warning("Total weight is 0, cannot calculate weighted standard deviation")
        return 0

    variance = sum(((x - weighted_med) ** 2) * w for x, w in values) / total_weight
    result = variance ** 0.5
    logger.debug(f"Weighted standard deviation calculated: {result}")
    return result

def calculate_listing_values(listings: dict| list, divine_price: float) -> List[Tuple[float, float, int]]:
    logger.debug(f"Calculating listing values with divine price: {divine_price}")
    values = []
    if isinstance(listings, list):
        logger.warning("Listings is a list instead of expected dict")
        return []
    
    for listing_data in listings.values():
        if not listing_data.get('listing') or not listing_data['listing'].get('offers'):
            logger.debug("Skipping invalid listing without required fields")
            continue

        for offer in listing_data['listing']['offers']:
            try:
                currency = offer['exchange']['currency']
                if currency == "divine":
                    exalt_amount = offer['exchange']['amount'] * divine_price
                else:
                    exalt_amount = offer['exchange']['amount']
                currency_amount = offer['item']['amount']
                stock = offer['item']['stock']

                exchange_rate = exalt_amount / currency_amount
                total_value = stock * exchange_rate  # Calculate total value for this listing

                logger.debug(f"Processed offer - rate: {exchange_rate}, value: {total_value}, stock: {stock}")
                values.append((exchange_rate, total_value, stock))
            except (KeyError, ZeroDivisionError) as e:
                logger.warning(f"Error processing offer: {e}")
                continue

    logger.info(f"Calculated {len(values)} valid listing values")
    return values


def filter_outliers(values: List[Tuple[float, float, int]], z_threshold: float = 1.7) -> List[Tuple[float, float, int]]:
    logger.debug(f"Filtering outliers from {len(values)} values with z_threshold: {z_threshold}")
    if not values:
        logger.warning("No values to filter outliers")
        return []

    listing_values = [(v[1], v[2]) for v in values]
    med = weighted_median(listing_values)
    std = weighted_stdev(listing_values, med)

    if std == 0:
        logger.debug("Standard deviation is 0, returning original values")
        return values

    filtered = [v for v in values if (
        abs((v[1] - med) / std) < z_threshold and
        0.5 * med <= v[1] <= 2.0 * med
    )]
    
    logger.info(f"Filtered {len(values) - len(filtered)} outliers, {len(filtered)} values remaining")
    return filtered

async def fetch_currency(want_currency: CurrencyItem, league: League, have_currency_api_ids: List[str], client: PoeTradeClient, divine_price: float) -> CurrencyPriceFetchResult:
    logger.info(f"Fetching currency prices for {want_currency.apiId} in {league.value} league")
    query = create_currency_exchange_query(want_currency.apiId, have_currency_api_ids)
    query_url = f"{BASE_URL}/exchange/{REALM}/{league.value}"
    
    try:
        response = await client.post(query_url, json=query)
        response_data = response.json()
    except Exception as e:
        logger.error(f"Error fetching currency data: {e}")
        return CurrencyPriceFetchResult(price=-1, quantity=0)

    if response_data.get('result') is None:
        logger.info("No response data")
        return CurrencyPriceFetchResult(price=-1, quantity=0)
    
    all_prices = calculate_listing_values(response_data['result'], divine_price)

    if len(all_prices) == 0:
        logger.info("No prices")
        return CurrencyPriceFetchResult(price=-1, quantity=0)


    filtered_prices = filter_outliers(all_prices)


    if len(filtered_prices) == 0:
        logger.info("No filtered prices")
        return CurrencyPriceFetchResult(price=-1, quantity=0)
    
    best_exchange_rate = min(rate for rate, _, _ in filtered_prices)    
    total_stock = sum(stock for _, _, stock in filtered_prices)

    logger.info(f"Best exchange rate: {best_exchange_rate}, total stock: {total_stock}")
    return CurrencyPriceFetchResult(price=best_exchange_rate, quantity=total_stock)

