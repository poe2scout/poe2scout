from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import Iterator

from fastapi import Request


@dataclass
class RequestContext:
    request: Request
    cache_status: str = "bypass"
    rate_limited: bool = False
    exception_type: str | None = None
    extra_fields: dict[str, str | int | float | bool | None] = field(default_factory=dict)


_REQUEST_CONTEXT: ContextVar[RequestContext | None] = ContextVar(
    "poe2scout_request_context", default=None
)


@contextmanager
def request_context(request: Request) -> Iterator[RequestContext]:
    context = RequestContext(request=request)
    token: Token[RequestContext | None] = _REQUEST_CONTEXT.set(context)
    try:
        yield context
    finally:
        _REQUEST_CONTEXT.reset(token)


def get_current_request_context() -> RequestContext | None:
    return _REQUEST_CONTEXT.get()
