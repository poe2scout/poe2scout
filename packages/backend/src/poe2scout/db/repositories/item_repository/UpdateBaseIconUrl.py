from ..base_repository import BaseRepository


class UpdateBaseItemIconUrl(BaseRepository):
    async def execute(self, iconUrl: str, id: int):
        async with self.get_db_cursor() as cursor:

            query = """
                UPDATE "BaseItem"
                SET "iconUrl" = %(iconUrl)s
                WHERE "id" = %(id)s
            """

            await cursor.execute(
                query, params={"iconUrl": iconUrl, "id": id}
            )
