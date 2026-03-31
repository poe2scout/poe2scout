from services.libs import BaseConfig


class CurrencyExchangeServiceConfig(BaseConfig):
    dbstring: str
    POEAPI_CLIENT_ID: str
    POEAPI_CLIENT_SECRET: str
