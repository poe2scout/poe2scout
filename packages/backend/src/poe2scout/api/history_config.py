from typing import Annotated

from fastapi import Depends, HTTPException, Query

from poe2scout.api.api_model import ApiModel


ALLOWED_CATEGORY_HISTORY_DATA_POINTS = {7, 8}
ALLOWED_CATEGORY_HISTORY_FREQUENCY_HOURS = {1, 2, 3, 4, 6, 8, 12, 24}


class CategoryPriceHistoryConfig(ApiModel):
    data_points: int = 7
    frequency_hours: int = 24


def get_category_price_history_config(
    data_points: Annotated[int, Query(alias="DataPoints")] = 7,
    frequency_hours: Annotated[int, Query(alias="FrequencyHours")] = 24,
) -> CategoryPriceHistoryConfig:
    if data_points not in ALLOWED_CATEGORY_HISTORY_DATA_POINTS:
        raise HTTPException(400, "DataPoints must be 7 or 8")

    if frequency_hours not in ALLOWED_CATEGORY_HISTORY_FREQUENCY_HOURS:
        raise HTTPException(
            400,
            "FrequencyHours must be one of 1, 2, 3, 4, 6, 8, 12, or 24",
        )

    return CategoryPriceHistoryConfig(
        data_points=data_points,
        frequency_hours=frequency_hours,
    )


CategoryPriceHistoryConfigDep = Annotated[
    CategoryPriceHistoryConfig,
    Depends(get_category_price_history_config),
]
