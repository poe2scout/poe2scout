import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from poe2scout.api.routes.leagues.get import (
    GetLeaguesRequest,
    GetResponse,
    get,
)
from poe2scout.db.repositories.game_repository.get_bridge_currencies import BridgeCurrency
from poe2scout.db.repositories.league_repository.get_leagues import League
from poe2scout.db.repositories.models import CurrencyItem
from poe2scout.db.repositories.price_log_repository.get_item_prices_by_league import (
    GetItemPricesByLeagueModel,
)
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
        bridge_currencies = [
            make_bridge_currency(10, "chaos", "Chaos Orb", 1),
            make_bridge_currency(20, "divine", "Divine Orb", 2),
        ]

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
                AsyncMock(return_value=bridge_currencies),
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
                "poe2scout.api.routes.leagues.get.price_log_repository.get_item_prices_by_league",
                AsyncMock(
                    return_value=[
                        GetItemPricesByLeagueModel(
                            league_id=7,
                            item_id=10,
                            price=1.0,
                        ),
                        GetItemPricesByLeagueModel(
                            league_id=7,
                            item_id=20,
                            price=1000.0,
                        ),
                    ]
                ),
            ) as get_item_prices_by_league,
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
        get_item_prices_by_league.assert_awaited_once()
        item_ids, league_ids, realm_id = get_item_prices_by_league.await_args.args
        self.assertEqual(set(item_ids), {10, 20})
        self.assertEqual(league_ids, [7])
        self.assertEqual(realm_id, 2)

    async def test_response_does_not_duplicate_default_bridge_currency(self):
        league = make_league()
        response = GetResponse.from_model(
            league=league,
            exalted_item=make_currency_item(30, "exalted", "Exalted Orb"),
            divine_item=make_currency_item(20, "divine", "Divine Orb"),
            chaos_item=make_currency_item(10, "chaos", "Chaos Orb"),
            bridge_currencies=[
                make_bridge_currency(10, "chaos", "Chaos Orb", 1),
                make_bridge_currency(20, "divine", "Divine Orb", 2),
            ],
            price_lookup={(7, 10): 1, (7, 20): 1000},
        )

        self.assertEqual(response.default_currency.api_id, "chaos")
        self.assertEqual(
            [currency.api_id for currency in response.base_currencies],
            ["chaos", "divine"],
        )

    async def test_response_keeps_missing_prices_as_zero(self):
        league = make_league()
        response = GetResponse.from_model(
            league=league,
            exalted_item=make_currency_item(30, "exalted", "Exalted Orb"),
            divine_item=make_currency_item(20, "divine", "Divine Orb"),
            chaos_item=make_currency_item(10, "chaos", "Chaos Orb"),
            bridge_currencies=[
                make_bridge_currency(10, "chaos", "Chaos Orb", 1),
                make_bridge_currency(20, "divine", "Divine Orb", 2),
            ],
            price_lookup={(7, 10): 1},
        )

        self.assertEqual(response.base_currencies[1].api_id, "divine")
        self.assertEqual(response.base_currencies[1].relative_price, 0)

    async def test_response_raises_500_when_default_currency_is_not_bridged(self):
        league = make_league()

        with self.assertRaises(HTTPException) as context:
            GetResponse.from_model(
                league=league,
                exalted_item=make_currency_item(30, "exalted", "Exalted Orb"),
                divine_item=make_currency_item(20, "divine", "Divine Orb"),
                chaos_item=make_currency_item(10, "chaos", "Chaos Orb"),
                bridge_currencies=[
                    make_bridge_currency(20, "divine", "Divine Orb", 1),
                ],
                price_lookup={(7, 20): 1000},
            )

        self.assertEqual(context.exception.status_code, 500)


if __name__ == "__main__":
    unittest.main()
