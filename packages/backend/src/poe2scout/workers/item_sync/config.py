from poe2scout.shared import BaseConfig


class ItemSyncConfig(BaseConfig):
    dbstring: str
    unique_item_url: str
    currency_item_url: str
