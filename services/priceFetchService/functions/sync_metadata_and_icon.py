from services.repositories.item_repository import ItemRepository
from services.repositories.item_repository.GetAllCurrencyItems import CurrencyItem
import logging
from .extract_currency_item_metadata import extract_currency_item_metadata
from services.libs.poe_trade_client import ClientError, PoeTradeClient

logger = logging.getLogger(__name__)


async def sync_metadata_and_icon(
    want_currency: CurrencyItem,
    repo: ItemRepository,
    client: PoeTradeClient,
    BASE_URL: str,
    REALM: str,
    LEAGUE: str,
):
    query_url = f"{BASE_URL}/search/{REALM}/{LEAGUE}"
    query_data = {
        "query": {
            "status": {"option": "online"},
            "type": want_currency.text,
            "stats": [{"type": "and", "filters": []}],
        },
        "sort": {"price": "asc"},
    }

    try:
        query_response = await client.post(query_url, json=query_data)
    except ClientError:
        logger.warning(f"Failed to sync item metadata for item {want_currency.text}")
        return

    query_data = query_response.json()
    logger.info(f"Query data: {query_data}")
    if len(query_data["result"]) == 0:
        logger.info(f"No results found for {want_currency.text} ")
        return

    item_ids = query_data["result"][:10]

    # Second request - GET items
    items_url = f"{BASE_URL}/fetch/{','.join(item_ids)}"
    params = {"query": query_data["id"], "realm": REALM}
    fetch_response = await client.get(items_url, params=params)

    if fetch_response.status_code != 200:
        raise Exception(
            f"Fetch request failed for {want_currency.text} with status code {fetch_response.status_code}"
        )

    fetch_data = fetch_response.json()

    if len(fetch_data["result"]) == 0:
        logger.info(f"No results found for {want_currency.text} ")

    logger.info(f"Fetch data: {fetch_data['result'][0]['item']}")
    itemMetadata = extract_currency_item_metadata(fetch_data["result"][0]["item"])
    logger.info(f"Item metadata: {itemMetadata}")

    if want_currency.itemMetadata is None:
        await repo.SetCurrencyItemMetadata(itemMetadata, want_currency.id)

    if want_currency.iconUrl is None:
        await repo.UpdateCurrencyIconUrl(itemMetadata["icon"], want_currency.id)
