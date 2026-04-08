from poe2scout.db.repositories.models import PriceLogEntry


def resolve_reference_currency_api_id(
    reference_currency: str | None,
    default_currency_api_id: str,
) -> str:
    return reference_currency or default_currency_api_id


def convert_price_history_from_base(
    history: list[PriceLogEntry],
    reference_currency_history: list[PriceLogEntry],
) -> list[PriceLogEntry]:
    reference_currency_history_lookup = {
        price_log.time: price_log for price_log in reference_currency_history
    }

    adjusted_price_history: list[PriceLogEntry] = []
    last_reference_price = 0.0  

    for price_log in history:
        current_reference_log = reference_currency_history_lookup.get(price_log.time)

        if current_reference_log is not None:
            last_reference_price = current_reference_log.price

        if last_reference_price == 0:
            continue

        adjusted_price_history.append(
            PriceLogEntry(
                price=price_log.price / last_reference_price,
                time=price_log.time,
                quantity=price_log.quantity,
            )
        )

    return adjusted_price_history


def convert_price_log_matrix_from_base(
    price_logs_by_item_id: dict[int, list[PriceLogEntry | None]],
    reference_currency_logs: list[PriceLogEntry | None],
) -> dict[int, list[PriceLogEntry | None]]:
    converted_logs: dict[int, list[PriceLogEntry | None]] = {}

    for item_id, price_logs in price_logs_by_item_id.items():
        converted_logs[item_id] = []

        for price_log, reference_log in zip(
            price_logs,
            reference_currency_logs,
            strict=False,
        ):
            if (
                price_log is None
                or reference_log is None
                or reference_log.price == 0
            ):
                converted_logs[item_id].append(None)
                continue

            converted_logs[item_id].append(
                PriceLogEntry(
                    price=price_log.price / reference_log.price,
                    time=price_log.time,
                    quantity=price_log.quantity,
                )
            )

    return converted_logs


def convert_prices_from_base(
    prices_by_item_id: dict[int, float],
    reference_currency_price: float,
) -> dict[int, float]:
    if reference_currency_price == 0:
        return {item_id: 0.0 for item_id in prices_by_item_id}

    return {
        item_id: price / reference_currency_price
        for item_id, price in prices_by_item_id.items()
    }
