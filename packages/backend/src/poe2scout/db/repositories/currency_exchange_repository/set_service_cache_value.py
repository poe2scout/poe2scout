from ..base_repository import BaseRepository


async def set_service_cache_value(service_name: str, value: int):
    async with BaseRepository.get_db_cursor() as cursor:
        query = """
            UPDATE service_cache
               SET value = %(value)s
             WHERE service_name = %(service_name)s
        """

        params = {"service_name": service_name, "value": value}
        print(f"saving serviceCache value for {service_name} with value {value}")
        await cursor.execute(query, params)
