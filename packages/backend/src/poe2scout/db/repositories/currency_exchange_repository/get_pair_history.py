from decimal import Decimal

from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class PairDataDetails(RepositoryModel):
    currency_item_id: int
    value_traded: Decimal
    relative_price: Decimal
    stock_value: Decimal
    volume_traded: int
    highest_stock: int


class PairData(RepositoryModel):
    currency_one_data: PairDataDetails
    currency_two_data: PairDataDetails


class GetCurrentSnapshotPairModel(RepositoryModel):
    epoch: int
    data: PairData


class GetPairHistoryModel(RepositoryModel):
    history: list[GetCurrentSnapshotPairModel]
    meta: dict[str, object]


class _PairHistoryDbRow(RepositoryModel):
    epoch: int
    currency_one_id: int
    c1_value_traded: Decimal
    c1_relative_price: Decimal
    c1_stock_value: Decimal
    c1_volume_traded: int
    c1_highest_stock: int
    currency_two_id: int
    c2_value_traded: Decimal
    c2_relative_price: Decimal
    c2_stock_value: Decimal
    c2_volume_traded: int
    c2_highest_stock: int


async def get_pair_history(
    currency_one_id: int,
    currency_two_id: int,
    league_id: int,
    realm_id: int,
    end_epoch: int,
    limit: int,
) -> GetPairHistoryModel:
    async with BaseRepository.get_db_cursor(row_factory=class_row(_PairHistoryDbRow)) as cursor:
        query = """
(
    SELECT
        epoch,
        currency_one_item_id AS "currency_one_id",
        c1_value_traded AS "c1_value_traded",
        c1_relative_price AS "c1_relative_price",
        c1_stock_value AS "c1_stock_value",
        c1_volume_traded AS "c1_volume_traded",
        c1_highest_stock AS "c1_highest_stock",
        currency_two_item_id AS "currency_two_id",
        c2_value_traded AS "c2_value_traded",
        c2_relative_price AS "c2_relative_price",
        c2_stock_value AS "c2_stock_value",
        c2_volume_traded AS "c2_volume_traded",
        c2_highest_stock AS "c2_highest_stock"
    FROM currency_exchange_history
    WHERE
        league_id = %(league_id)s
        AND realm_id = %(realm_id)s
        AND epoch < %(end_epoch)s
        AND currency_one_item_id = %(currency_two_id)s
        AND currency_two_item_id = %(currency_one_id)s
    ORDER BY epoch DESC
    LIMIT %(limit)s
)
UNION ALL
(
    SELECT
        epoch AS "epoch",
        currency_one_item_id AS "currency_one_id",
        c1_value_traded AS "c1_value_traded",
        c1_relative_price AS "c1_relative_price",
        c1_stock_value AS "c1_stock_value",
        c1_volume_traded AS "c1_volume_traded",
        c1_highest_stock AS "c1_highest_stock",
        currency_two_item_id AS "currency_two_id",
        c2_value_traded AS "c2_value_traded",
        c2_relative_price AS "c2_relative_price",
        c2_stock_value AS "c2_stock_value",
        c2_volume_traded AS "c2_volume_traded",
        c2_highest_stock AS "c2_highest_stock"
    FROM currency_exchange_history
    WHERE
        league_id = %(league_id)s
        AND realm_id = %(realm_id)s
        AND epoch < %(end_epoch)s
        AND currency_one_item_id = %(currency_one_id)s
        AND currency_two_item_id = %(currency_two_id)s
    ORDER BY epoch DESC
    LIMIT %(limit)s
)
ORDER BY "epoch" DESC
LIMIT %(limit)s;
        """

        params = {
            "currency_one_id": currency_one_id,
            "currency_two_id": currency_two_id,
            "league_id": league_id,
            "realm_id": realm_id,
            "end_epoch": end_epoch,
            "limit": limit + 1,
        }

        await cursor.execute(query, params)

        records = await cursor.fetchall()

        has_more = False

        if len(records) > limit:
            has_more = True
            records.pop()

        return_list: list[GetCurrentSnapshotPairModel] = []
        for record in records:
            c1_pair_data_details = PairDataDetails.model_construct(
                currency_item_id=record.currency_one_id,
                highest_stock=record.c1_highest_stock,
                relative_price=record.c1_relative_price,
                stock_value=record.c1_stock_value,
                value_traded=record.c1_value_traded,
                volume_traded=record.c1_volume_traded,
            )
            c2_pair_data_details = PairDataDetails.model_construct(
                currency_item_id=record.currency_two_id,
                highest_stock=record.c2_highest_stock,
                relative_price=record.c2_relative_price,
                stock_value=record.c2_stock_value,
                value_traded=record.c2_value_traded,
                volume_traded=record.c2_volume_traded,
            )
            if c1_pair_data_details.currency_item_id == currency_one_id:
                record_pair_data = PairData.model_construct(
                    currency_one_data=c1_pair_data_details,
                    currency_two_data=c2_pair_data_details,
                )
            else:
                record_pair_data = PairData.model_construct(
                    currency_one_data=c2_pair_data_details,
                    currency_two_data=c1_pair_data_details,
                )

            record_model = GetCurrentSnapshotPairModel.model_construct(
                epoch=record.epoch,
                data=record_pair_data,
            )
            return_list.append(record_model)

        return GetPairHistoryModel.model_construct(
            history=return_list,
            meta={"has_more": has_more},
        )
