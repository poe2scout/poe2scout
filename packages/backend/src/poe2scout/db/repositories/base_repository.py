from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Any, Callable, Dict, Sequence, TypeVar, overload
from psycopg import Cursor
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import RowMaker, dict_row
import logging
import asyncio
from psycopg.rows import RowFactory
from psycopg.cursor_async import AsyncCursor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


RowT = TypeVar("RowT")


class BaseRepository:
    _pool = None

    @classmethod
    async def init_pool(cls, connection_string: str, min_conn=5, max_conn=20):
        """Initialize the connection pool if it doesn't exist"""
        try:
            if cls._pool is None:
                logger.info("Initializing database connection pool...")
                cls._pool = AsyncConnectionPool(
                    conninfo=connection_string, min_size=min_conn, max_size=max_conn
                )
                logger.info("Opening connection pool...")
                await cls._pool.open()
                logger.info("Connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {str(e)}")
            raise

    @overload
    @classmethod
    def get_db_cursor(
        cls,
    ) -> AbstractAsyncContextManager[AsyncCursor[Dict[str, Any]]]:
        """Overload for the default case with no rowFactory."""
        ...

    @overload
    @classmethod
    def get_db_cursor(
        cls, rowFactory: RowFactory[RowT]
    ) -> AbstractAsyncContextManager[AsyncCursor[RowT]]:
        """Overload for the generic case with a specific rowFactory."""
        ...

    @classmethod
    @asynccontextmanager
    async def get_db_cursor(cls, rowFactory=dict_row):
        """Get a database cursor from the connection pool"""
        if cls._pool is None:
            raise RuntimeError("Database pool not initialized")

        try:
            async with asyncio.timeout(10):  # 10 second timeout
                async with cls._pool.connection() as conn:
                    async with conn.cursor(row_factory=rowFactory) as cursor:
                        logger.debug("Database cursor acquired")
                        yield cursor
                        await conn.commit()
                        logger.debug("Transaction committed")
        except asyncio.TimeoutError:
            logger.error("Database operation timed out")
            raise
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            raise


T = TypeVar("T")

def scalar_as(cast: Callable[[Any], T]) -> RowFactory[T]:
    def factory(cursor: Cursor[Any]) -> RowMaker[T]:
        if cursor.description is None or len(cursor.description) != 1:
            raise ValueError("scalar_as() requires exactly one selected column")

        def make_row(values: Sequence[Any]) -> T:
            return cast(values[0])

        return make_row

    return factory