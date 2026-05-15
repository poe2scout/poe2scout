import unittest
from unittest.mock import AsyncMock, patch

from poe2scout.api.routes.leagues.get import (
    GetLeaguesRequest,
    build_league_currencies,
    get,
)
from poe2scout.db.repositories.game_repository.get_bridge_currencies import BridgeCurrency
from poe2scout.db.repositories.league_repository.get_leagues import League
from poe2scout.db.repositories.models import CurrencyItem
from poe2scout.db.repositories.realm_repository.get_realm import Realm


def make_league(
    *,
    base_api_id: str = "chaos",
    base_text: str = "Chaos Orb",
    base_item_id: int = 10,
) -> League:
    return League(
        league_id=7,
        value="Standard",
        base_currency_item_id=base_item_id,
        base_currency_api_id=base_api_id,
        base_currency_text=base_text,
        base_currency_icon_url=f"{base_api_id}.png",
        current_league=True,
    )


def make_currency_item(item_id: int, api_id: str, text: str) -> CurrencyItem:
    return CurrencyItem(
        currency_item_id=item_id,
        item_id=item_id,
        currency_category_id=1,
        category_api_id="currency",
        api_id=api_id,
        text=text,
        icon_url=f"{api_id}.png",
    )


def make_bridge_currency(
    item_id: int,
    api_id: str,
    text: str,
    bridge_rank: int,
) -> BridgeCurrency:
    return BridgeCurrency(
        item_id=item_id,
        currency_item_id=item_id,
        api_id=api_id,
        text=text,
        icon_url=f"{api_id}.png",
        bridge_rank=bridge_rank,
    )


class GetLeaguesRouteTests(unittest.IsolatedAsyncioTestCase):
    async def test_route_returns_default_and_ordered_base_currencies(self):
        league = make_league()
        divine_item = make_currency_item(20, "divine", "Divine Orb")
        chaos_item = make_currency_item(10, "chaos", "Chaos Orb")

        with (
            patch(
                "poe2scout.api.routes.leagues.get.realm_repository.get_realm",
                AsyncMock(return_value=Realm(realm_id=2, game_id=1)),
            ),
            patch(
                "poe2scout.api.routes.leagues.get.league_repository.get_leagues",
                AsyncMock(return_value=[league]),
            ),
            patch(
                "poe2scout.api.routes.leagues.get.game_repository.get_bridge_currencies",
                AsyncMock(
                    return_value=[
                        make_bridge_currency(20, "divine", "Divine Orb", 1),
                    ]
                ),
            ),
            patch(
                "poe2scout.api.routes.leagues.get.currency_item_repository.get_exalted_item",
                AsyncMock(return_value=make_currency_item(30, "exalted", "Exalted Orb")),
            ),
            patch(
                "poe2scout.api.routes.leagues.get.currency_item_repository.get_divine_item",
                AsyncMock(return_value=divine_item),
            ),
            patch(
                "poe2scout.api.routes.leagues.get.currency_item_repository.get_chaos_item",
                AsyncMock(return_value=chaos_item),
            ),
            patch(
                "poe2scout.api.routes.leagues.get.price_log_repository.get_item_price",
                AsyncMock(side_effect=[1000.0, 1.0, 1000.0]),
            ),
        ):
            response = await get(GetLeaguesRequest(realm="poe"))

        self.assertEqual(len(response), 1)
        self.assertEqual(response[0].default_currency.api_id, "chaos")
        self.assertEqual(response[0].default_currency.relative_price, 1)
        self.assertEqual(
            [currency.api_id for currency in response[0].base_currencies],
            ["chaos", "divine"],
        )
        self.assertEqual(response[0].base_currencies[1].relative_price, 1000)

    async def test_base_currency_builder_does_not_duplicate_default_bridge_currency(self):
        league = make_league()

        with patch(
            "poe2scout.api.routes.leagues.get.price_log_repository.get_item_price",
            AsyncMock(return_value=1000.0),
        ) as get_item_price:
            default_currency, base_currencies = await build_league_currencies(
                league,
                [
                    make_bridge_currency(10, "chaos", "Chaos Orb", 1),
                    make_bridge_currency(20, "divine", "Divine Orb", 2),
                ],
                realm_id=2,
            )

        self.assertEqual(default_currency.api_id, "chaos")
        self.assertEqual([currency.api_id for currency in base_currencies], ["chaos", "divine"])
        get_item_price.assert_awaited_once_with(20, 7, 2, None)

    async def test_base_currency_builder_keeps_missing_prices_as_zero(self):
        league = make_league()

        with patch(
            "poe2scout.api.routes.leagues.get.price_log_repository.get_item_price",
            AsyncMock(return_value=0),
        ):
            _, base_currencies = await build_league_currencies(
                league,
                [make_bridge_currency(20, "divine", "Divine Orb", 1)],
                realm_id=2,
            )

        self.assertEqual(base_currencies[1].api_id, "divine")
        self.assertEqual(base_currencies[1].relative_price, 0)


if __name__ == "__main__":
    unittest.main()
