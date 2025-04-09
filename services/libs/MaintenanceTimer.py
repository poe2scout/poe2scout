import asyncio
from typing import Callable, Awaitable
import logging

logger = logging.getLogger(__name__)

class MaintenanceTimer:
    def __init__(self, 
                 get_next_maintenance: Callable[[], float]): 
        self._task = None
        self._current_maintenance_task = None
        self._shutdown = False
        self._get_next_maintenance = get_next_maintenance

    async def _maintenance_timer(self):
        while not self._shutdown:
            seconds_until_maintenance = self._get_next_maintenance()
            logger.info(f"Seconds until maintenance: {seconds_until_maintenance}")
            try:
                await asyncio.sleep(seconds_until_maintenance)
                if self._current_maintenance_task and not self._shutdown:
                    logger.info("Maintenance window approaching, cancelling current task")
                    self._current_maintenance_task.cancel()
            except asyncio.CancelledError:
                break

    async def __aenter__(self):
        self._task = asyncio.create_task(self._maintenance_timer())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._shutdown = True
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def run_cancellable(self, coro: Awaitable):
        """Run a coroutine that can be cancelled during maintenance"""
        self._current_maintenance_task = asyncio.current_task()
        try:
            return await coro
        finally:
            self._current_maintenance_task = None