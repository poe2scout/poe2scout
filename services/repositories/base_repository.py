import os
from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseRepository:
    _pool = None

    @classmethod
    async def init_pool(cls, connection_string: str, min_conn=5, max_conn=20):
        """Initialize the connection pool if it doesn't exist"""
        try:
            if cls._pool is None:
                logger.info("Initializing database connection pool...")
                cls._pool = AsyncConnectionPool(
                    conninfo=connection_string,
                    min_size=min_conn,
                    max_size=max_conn
                )
                logger.info("Opening connection pool...")
                await cls._pool.open()
                logger.info("Connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {str(e)}")
            raise

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

    async def execute_query(self, query, params=None):
        logger.debug(f"Executing query: {query[:100]}...")  # Log first 100 chars of query
        try:
            async with self.get_db_cursor() as cursor:
                await cursor.execute(query, params)
                result = await cursor.fetchall()
                logger.debug(f"Query returned {len(result)} rows")
                return result
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise

    async def execute_single(self, query, params=None) -> int:
        logger.debug(f"Executing single-row query: {query[:100]}...")
        try:
            async with self.get_db_cursor() as cursor:
                await cursor.execute(query, params)
                return (await cursor.fetchone())['id']
        except Exception as e:
            logger.error(f"Single-row query failed: {str(e)}")
            raise

    async def execute_update(self, query, params=None):
        logger.debug(f"Executing update query: {query[:100]}...")
        try:
            async with self.get_db_cursor() as cursor:
                await cursor.execute(query, params)
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Update query failed: {str(e)}")
            raise

    async def execute_no_return(self, query, params=None):
        logger.debug(f"Executing no-return query: {query[:100]}...")
        try:
            async with self.get_db_cursor() as cursor:
                await cursor.execute(query, params)
        except Exception as e:
            logger.error(f"No-return query failed: {str(e)}")
            raise

    async def execute_many(self, query, params):
        try:
            async with self.get_db_cursor() as cursor:
                await cursor.executemany(query, params)
        except Exception as e:
            logger.error(f"Bulk query failed: {str(e)}")
            raise