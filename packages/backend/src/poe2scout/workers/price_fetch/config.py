from poe2scout.shared import BaseConfig


class PriceFetchConfig(BaseConfig):
    dbstring: str
    POEAPI_CLIENT_ID: str
    POEAPI_CLIENT_SECRET: str
