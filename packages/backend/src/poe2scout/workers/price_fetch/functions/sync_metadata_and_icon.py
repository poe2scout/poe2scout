from poe2scout.db.repositories.currency_item_repository import CurrencyItemRepository
from poe2scout.db.repositories.item_repository import ItemRepository
from poe2scout.db.repositories.currency_item_repository.get_all_currency_items import CurrencyItem
import logging

from .extract_currency_item_metadata import extract_currency_item_metadata
from poe2scout.integrations.poe.client import ClientError, PoeTradeClient

logger = logging.getLogger(__name__)


async def sync_metadata_and_icon(
    want_currency: CurrencyItem,
    repo: ItemRepository,
    currency_item_repo: CurrencyItemRepository,
    client: PoeTradeClient,
    base_url: str,
    realm: str,
    league: str,
):
    query_url = f"{base_url}/search/{realm}/{league}"
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
    items_url = f"{base_url}/fetch/{','.join(item_ids)}"
    params = {"query": query_data["id"], "realm": realm}
    fetch_response = await client.get(items_url, params=params)

    if fetch_response.status_code != 200:
        raise Exception(
            f"Fetch request failed for {want_currency.text} " +\
            f"with status code {fetch_response.status_code}"
        )

    fetch_data = fetch_response.json()

    if len(fetch_data["result"]) == 0:
        logger.info(f"No results found for {want_currency.text} ")

    logger.info(f"Fetch data: {fetch_data['result'][0]['item']}")
    item_metadata = extract_currency_item_metadata(fetch_data["result"][0]["item"])
    logger.info(f"Item metadata: {item_metadata}")

    if want_currency.item_metadata is None:
        await currency_item_repo.set_currency_item_metadata(
            item_metadata, 
            want_currency.currency_item_id
        )

    if want_currency.icon_url is None:
        await currency_item_repo.update_currency_icon_url(
            item_metadata["icon"], 
            want_currency.currency_item_id
        )
