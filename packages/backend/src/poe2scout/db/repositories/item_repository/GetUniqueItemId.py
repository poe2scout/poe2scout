from ..base_repository import BaseRepository, scalar_as
from pydantic import BaseModel


class GetUniqueItemIdModel(BaseModel):
    name: str


class GetUniqueItemId(BaseRepository):
    async def execute(self, name: str) -> int | None:
        async with self.get_db_cursor(
            rowFactory=scalar_as(int)
        ) as cursor:
            query = """
                SELECT "itemId" FROM "UniqueItem"
                WHERE "name" = %s
            """

            await cursor.execute(query, (name,))

            return await cursor.fetchone()
