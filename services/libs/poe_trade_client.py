from httpx import AsyncClient, Response
from typing import Any, Dict, Optional
import logging
import asyncio

# Replace this:
# async with AsyncClient(headers=headers) as client:

# With this:
class PoeTradeError(Exception):
    """Base exception for POE Trade API errors"""
    pass

class RateLimitError(PoeTradeError):
    """Raised when rate limit is exceeded"""
    pass

class ServiceUnavailableError(PoeTradeError):
    """Raised when service is unavailable"""
    pass

class AuthenticationError(PoeTradeError):
    """Raised when authentication fails"""
    pass

class ClientError(PoeTradeError):
    """Raised for 4xx errors not covered by specific exceptions"""
    pass

class ServerError(PoeTradeError):
    """Raised for 5xx errors not covered by specific exceptions"""
    pass


logger = logging.getLogger(__name__)

class PoeTradeClient(AsyncClient):
    def __init__(self, headers: Optional[Dict[str, str]] = None):
        super().__init__(headers=headers)
        self.max_retries = 5
        self.retry_delay = 300  # 5 minutes in seconds

    async def _handle_response(self, response: Response) -> Response:
        """Handle different response status codes"""
        if response.status_code == 200:
            return response
            
        error_mapping = {
            429: (RateLimitError, "Rate limit exceeded", False),  # No retry
            503: (ServiceUnavailableError, "Service temporarily unavailable", True),
            405: (ClientError, "Method not allowed", True),
            403: (ClientError, "Forbidden", True),
        }

        if response.status_code in error_mapping:
            ErrorClass, message, should_retry = error_mapping[response.status_code]
            if not should_retry:
                raise ErrorClass(f"{message} - Status Code: {response.status_code}")
            return None  # Signal that this error should be retried
        
            
        if 400 <= response.status_code < 500:
            raise ClientError(f"Client error occurred - Status Code: {response.status_code}")
            
        if response.status_code >= 500:
            raise ServerError(f"Server error occurred - Status Code: {response.status_code}")

        return response

    async def get(self, *args, **kwargs) -> Response:
        """Override get method with custom error handling and retries"""
        attempts = 0
        while attempts < self.max_retries:
            response = await super().get(*args, **kwargs)
            handled_response = await self._handle_response(response)
            if handled_response is not None:
                return handled_response
            
            attempts += 1
            if attempts < self.max_retries:
                logger.warning(f"Request failed with status {response.status_code}. "
                             f"Retrying in {self.retry_delay} seconds... "
                             f"(Attempt {attempts + 1}/{self.max_retries})")
                await asyncio.sleep(self.retry_delay)
            
        raise ServiceUnavailableError(f"Max retries ({self.max_retries}) exceeded. Last status: {response.status_code}")

    async def post(self, *args, **kwargs) -> Response:
        """Override post method with custom error handling and retries"""
        await asyncio.sleep(17)
        attempts = 0
        while attempts < self.max_retries:
            response = await super().post(*args, **kwargs)
            handled_response = await self._handle_response(response)
            if handled_response is not None:
                return handled_response
            
            attempts += 1
            if attempts < self.max_retries:
                logger.warning(f"Request failed with status {response.status_code}. "
                             f"Retrying in {self.retry_delay} seconds... "
                             f"(Attempt {attempts + 1}/{self.max_retries})")
                await asyncio.sleep(self.retry_delay)
            
        raise ServiceUnavailableError(f"Max retries ({self.max_retries}) exceeded. Last status: {response.status_code}")