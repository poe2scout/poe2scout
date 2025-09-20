from services.libs import BaseConfig


class PriceFetchConfig(BaseConfig):
    dbstring: str
    POEAPI_CLIENT_ID: str
    POEAPI_CLIENT_SECRET: str
