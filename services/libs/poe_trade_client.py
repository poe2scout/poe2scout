from httpx import AsyncClient, Auth, Response
from typing import Any, Dict, Optional
import logging
import asyncio

import httpx

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

    async def _handle_response(self, response: Response) -> Optional[Response]:
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
        response = None
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
        assert response is not None
        raise ServiceUnavailableError(f"Max retries ({self.max_retries}) exceeded. Last status: {response.status_code}")

    async def post(self, *args, **kwargs) -> Response:
        """Override post method with custom error handling and retries"""
        attempts = 0
        response = None
        while attempts < self.max_retries:
            await asyncio.sleep(17)
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
        
        assert response is not None
        raise ServiceUnavailableError(f"Max retries ({self.max_retries}) exceeded. Last status: {response.status_code}")


class PoeApiClient(AsyncClient):
    def __init__(self, clientId: str, clientSecret: str, headers: Optional[Dict[str, str]] = None):
        if headers == None:
            headers =  {
            "User-Agent": "POE2SCOUT (contact: b@girardet.co.nz)"
            }
        super().__init__(headers=headers, auth=PoeApiAuth(client_id=clientId, client_secret=clientSecret))
        self.client_id = clientId
        self.client_secret = clientSecret
        self.max_retries = 5
        self.retry_delay = 300  # 5 minutes in seconds

        if self.client_id == None or self.client_id == "":
            raise ValueError
        if self.client_secret == None or self.client_secret == "":
            raise ValueError


    async def _handle_response(self, response: Response) -> Optional[Response]:
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
        response = None
        while attempts < self.max_retries:
            await asyncio.sleep(3)
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
        assert response is not None
        raise ServiceUnavailableError(f"Max retries ({self.max_retries}) exceeded. Last status: {response.status_code}")

    async def post(self, *args, **kwargs) -> Response:
        """Override post method with custom error handling and retries"""
        attempts = 0
        response = None
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
        assert response is not None
        raise ServiceUnavailableError(f"Max retries ({self.max_retries}) exceeded. Last status: {response.status_code}")

class PoeApiAuth(httpx.Auth):
    requires_response_body = True

    def __init__(self, client_id: str, client_secret: str, scope: str = "service:cxapi"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.token_url = "https://www.pathofexile.com/oauth/token"
        self.access_token = None

    def auth_flow(self, request: httpx.Request):
        # If we don't have a token yet, fetch one before sending the request.
        logger.info(f"access_token_value: {self.access_token}")
        if self.access_token is None:
            token_response = yield self.build_token_request()
            self.update_token(token_response)

        request.headers["Authorization"] = f"Bearer {self.access_token}"
        request.headers["User-Agent"] = f"OAuth {self.client_id}/1.0.0 (contact: b@girardet.co.nz)"
        response = yield request

        if response.status_code == 401:
            refresh_response = yield self.build_token_request()
            self.update_token(refresh_response)

            request.headers["Authorization"] = f"Bearer {self.access_token}"
            yield request

    def build_token_request(self) -> httpx.Request:
        return httpx.Request(
            method="POST",
            url=self.token_url,
            headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Poe2scout (b@girardet.co.nz)"},
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
                "scope": self.scope,
            },
        )

    def update_token(self, response: httpx.Response):
        response.raise_for_status()
        data = response.json()
        self.access_token = data["access_token"]
