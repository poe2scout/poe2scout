from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class GetServiceCacheValueModel(RepositoryModel):
    value: int


async def get_service_cache_value(service_name: str) -> GetServiceCacheValueModel:
    async with BaseRepository.get_db_cursor(
        row_factory=class_row(GetServiceCacheValueModel)
    ) as cursor:
        query = """
            SELECT "Value" AS "value"
              FROM "ServiceCache"
             WHERE "ServiceName" = %(service_name)s
        """

        params = {"service_name": service_name}

        await cursor.execute(query, params)

        return await cursor.fetchone()  # type: ignore