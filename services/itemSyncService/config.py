from services.libs import BaseConfig

class ItemSyncConfig(BaseConfig):
    dbstring: str
    unique_item_url: str
    currency_item_url: str
