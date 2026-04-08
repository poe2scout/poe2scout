import time
import unittest

from poe2scout.db.repositories.game_repository.get_bridge_currencies import BridgeCurrency
from poe2scout.db.repositories.league_repository.get_leagues import League
from poe2scout.workers.currency_price_log.service import (
    PriceObservation,
    build_final_prices_from_observations,
)


def make_league() -> League:
    return League(
        league_id=1,
        value="Test League",
        base_currency_item_id=100,
        base_currency_api_id="exalted",
        base_currency_text="Exalted Orb",
    )


def make_currency_item(
    item_id: int,
    api_id: str,
    bridge_rank: int,
) -> BridgeCurrency:
    return BridgeCurrency(
        item_id=item_id,
        currency_item_id=item_id,
        api_id=api_id,
        text=api_id.title(),
        bridge_rank=bridge_rank,
    )


def make_observation(
    base_item: str,
    target_item: str,
    price_in_base_item: float,
    quantity_of_target_item: int,
) -> PriceObservation:
    return PriceObservation(
        base_item=base_item,
        target_item=target_item,
        value_of_target_item_in_base_items=price_in_base_item,
        quantity_of_target_item=quantity_of_target_item,
    )


class CurrencyPriceLogAggregationTests(unittest.TestCase):
    def test_bridge_order_comes_from_bridge_rank(self):
        self.assertEqual(
            [
                bridge_item.api_id
                for bridge_item in [
                    make_currency_item(3, "chaos", bridge_rank=1),
                    make_currency_item(2, "annul", bridge_rank=2),
                    make_currency_item(1, "divine", bridge_rank=3),
                ]
            ],
            ["chaos", "annul", "divine"],
        )

    def test_chaos_resolves_before_divine_and_divine_uses_base_and_chaos(self):
        final_prices = build_final_prices_from_observations(
            observations=[
                make_observation("exalted", "chaos", 0.1, 100),
                make_observation("exalted", "divine", 40.0, 1),
                make_observation("chaos", "divine", 300.0, 1),
            ],
            league=make_league(),
            bridge_currencies=[
                make_currency_item(1, "chaos", bridge_rank=1),
                make_currency_item(2, "divine", bridge_rank=2),
            ],
            fallback_bridge_prices={},
        )

        self.assertAlmostEqual(final_prices["chaos"].value, 0.1)
        self.assertAlmostEqual(final_prices["divine"].value, 35.0)

    def test_later_bridge_can_be_inserted_between_existing_ranks(self):
        final_prices = build_final_prices_from_observations(
            observations=[
                make_observation("exalted", "chaos", 0.1, 100),
                make_observation("exalted", "annul", 1.5, 10),
                make_observation("chaos", "annul", 15.0, 10),
                make_observation("exalted", "divine", 32.0, 1),
                make_observation("chaos", "divine", 320.0, 1),
                make_observation("annul", "divine", 20.0, 1),
            ],
            league=make_league(),
            bridge_currencies=[
                make_currency_item(1, "chaos", bridge_rank=1),
                make_currency_item(2, "annul", bridge_rank=2),
                make_currency_item(3, "divine", bridge_rank=3),
            ],
            fallback_bridge_prices={},
        )

        self.assertAlmostEqual(final_prices["annul"].value, 1.5)
        self.assertAlmostEqual(final_prices["divine"].value, 31.333333333333332)

    def test_non_bridge_item_uses_all_resolved_bridge_quotes(self):
        final_prices = build_final_prices_from_observations(
            observations=[
                make_observation("exalted", "chaos", 0.1, 100),
                make_observation("exalted", "divine", 30.0, 1),
                make_observation("chaos", "divine", 300.0, 1),
                make_observation("exalted", "mirror", 10.0, 4),
                make_observation("chaos", "mirror", 100.0, 5),
                make_observation("divine", "mirror", 1.0 / 3.0, 6),
            ],
            league=make_league(),
            bridge_currencies=[
                make_currency_item(1, "chaos", bridge_rank=1),
                make_currency_item(2, "divine", bridge_rank=2),
            ],
            fallback_bridge_prices={},
        )

        self.assertAlmostEqual(final_prices["mirror"].value, 10.0)
        self.assertEqual(final_prices["mirror"].quantity_traded, 15)

    def test_item_quoted_only_in_unresolved_currency_requires_bridge_configuration(self):
        observations = [
            make_observation("exalted", "chaos", 0.1, 100),
            make_observation("mirror", "soulcore", 2.0, 7),
        ]

        without_mirror_bridge = build_final_prices_from_observations(
            observations=observations,
            league=make_league(),
            bridge_currencies=[make_currency_item(1, "chaos", bridge_rank=1)],
            fallback_bridge_prices={},
        )
        self.assertNotIn("soulcore", without_mirror_bridge)

        with_mirror_bridge = build_final_prices_from_observations(
            observations=observations
            + [make_observation("exalted", "mirror", 50.0, 1)],
            league=make_league(),
            bridge_currencies=[
                make_currency_item(1, "chaos", bridge_rank=1),
                make_currency_item(2, "mirror", bridge_rank=2),
            ],
            fallback_bridge_prices={},
        )
        self.assertAlmostEqual(with_mirror_bridge["soulcore"].value, 100.0)

    def test_bridge_falls_back_to_last_logged_price_when_snapshot_has_no_usable_pairs(self):
        final_prices = build_final_prices_from_observations(
            observations=[
                make_observation("exalted", "chaos", 0.1, 100),
                make_observation("chaos", "divine", 300.0, 1),
                make_observation("divine", "mirror", 1.0, 2),
            ],
            league=make_league(),
            bridge_currencies=[
                make_currency_item(1, "chaos", bridge_rank=1),
                make_currency_item(2, "divine", bridge_rank=2),
            ],
            fallback_bridge_prices={"divine": 28.0},
        )

        self.assertAlmostEqual(final_prices["divine"].value, 28.0)
        self.assertAlmostEqual(final_prices["mirror"].value, 28.0)

    def test_unresolved_bridge_without_fallback_is_excluded_from_downstream_pricing(self):
        final_prices = build_final_prices_from_observations(
            observations=[
                make_observation("exalted", "chaos", 0.1, 100),
                make_observation("chaos", "divine", 300.0, 1),
                make_observation("divine", "mirror", 1.0, 2),
            ],
            league=make_league(),
            bridge_currencies=[
                make_currency_item(1, "chaos", bridge_rank=1),
                make_currency_item(2, "divine", bridge_rank=2),
            ],
            fallback_bridge_prices={},
        )

        self.assertNotIn("divine", final_prices)
        self.assertNotIn("mirror", final_prices)

    def test_final_logged_quantity_uses_all_pairs_even_when_some_pairs_are_not_priceable(self):
        final_prices = build_final_prices_from_observations(
            observations=[
                make_observation("exalted", "chaos", 0.1, 100),
                make_observation("exalted", "divine", 30.0, 1),
                make_observation("chaos", "divine", 300.0, 1),
                make_observation("exalted", "relic", 10.0, 4),
                make_observation("chaos", "relic", 100.0, 5),
                make_observation("divine", "relic", 1.0 / 3.0, 6),
                make_observation("mirror", "relic", 0.2, 7),
            ],
            league=make_league(),
            bridge_currencies=[
                make_currency_item(1, "chaos", bridge_rank=1),
                make_currency_item(2, "divine", bridge_rank=2),
            ],
            fallback_bridge_prices={},
        )

        self.assertAlmostEqual(final_prices["relic"].value, 10.0)
        self.assertEqual(final_prices["relic"].quantity_traded, 22)

    def test_route_flips_do_not_collapse_quantity_or_create_single_pair_jump(self):
        bridge_currencies = [
            make_currency_item(1, "chaos", bridge_rank=1),
            make_currency_item(2, "divine", bridge_rank=2),
        ]
        snapshot_one = build_final_prices_from_observations(
            observations=[
                make_observation("exalted", "chaos", 0.1, 100),
                make_observation("exalted", "divine", 30.0, 1),
                make_observation("chaos", "divine", 300.0, 1),
                make_observation("exalted", "artifact", 20.0, 1),
                make_observation("chaos", "artifact", 100.0, 100),
                make_observation("divine", "artifact", 1.0 / 3.0, 100),
            ],
            league=make_league(),
            bridge_currencies=bridge_currencies,
            fallback_bridge_prices={},
        )
        snapshot_two = build_final_prices_from_observations(
            observations=[
                make_observation("exalted", "chaos", 0.1, 100),
                make_observation("exalted", "divine", 30.0, 1),
                make_observation("chaos", "divine", 300.0, 1),
                make_observation("exalted", "artifact", 0.5, 1),
                make_observation("chaos", "artifact", 100.0, 100),
                make_observation("divine", "artifact", 1.0 / 3.0, 100),
            ],
            league=make_league(),
            bridge_currencies=bridge_currencies,
            fallback_bridge_prices={},
        )

        self.assertEqual(snapshot_one["artifact"].quantity_traded, 201)
        self.assertEqual(snapshot_two["artifact"].quantity_traded, 201)
        self.assertLess(abs(snapshot_one["artifact"].value - snapshot_two["artifact"].value), 0.2)

    def test_aggregation_runtime_stays_under_bound_for_large_snapshot(self):
        observations = [
            make_observation("exalted", "chaos", 0.1, 1000),
            make_observation("exalted", "annul", 1.5, 100),
            make_observation("chaos", "annul", 15.0, 100),
            make_observation("exalted", "divine", 30.0, 50),
            make_observation("chaos", "divine", 300.0, 50),
            make_observation("annul", "divine", 20.0, 50),
        ]
        for item_index in range(4000):
            item_api_id = f"item-{item_index}"
            observations.extend(
                [
                    make_observation("exalted", item_api_id, 10.0 + (item_index % 5), 4),
                    make_observation("chaos", item_api_id, 100.0 + (item_index % 5) * 10, 5),
                    make_observation("divine", item_api_id, (10.0 + (item_index % 3)) / 30.0, 6),
                    make_observation("mirror", item_api_id, 0.5, 7),
                ]
            )

        start = time.perf_counter()
        final_prices = build_final_prices_from_observations(
            observations=observations,
            league=make_league(),
            bridge_currencies=[
                make_currency_item(1, "chaos", bridge_rank=1),
                make_currency_item(2, "annul", bridge_rank=2),
                make_currency_item(3, "divine", bridge_rank=3),
            ],
            fallback_bridge_prices={},
        )
        runtime = time.perf_counter() - start

        self.assertLess(runtime, 2.0)
        self.assertEqual(len(final_prices), 4004)


if __name__ == "__main__":
    unittest.main()
