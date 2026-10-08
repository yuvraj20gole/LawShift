"""Rate limits, generation concurrency, upload/body size checks."""
from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque
from typing import Deque

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from .auth_supabase import AuthUser
from .security_settings import SecuritySettings, get_settings

# ip -> timestamps of /api/query hits in the last hour
_QUERY_HITS: dict[str, Deque[float]] = defaultdict(deque)
_HITS_LOCK = asyncio.Lock()
_GEN_SEMAPHORE: asyncio.Semaphore | None = None
_GEN_SEMAPHORE_SIZE: int | None = None


def client_ip(request: Request, settings: SecuritySettings | None = None) -> str:
    """Resolve client IP.

    When ``LAWSHIFT_TRUST_PROXY=1``, use the left-most address in
    ``X-Forwarded-For`` (the original client as set by a trusted tunnel /
    reverse proxy). Otherwise use the direct peer ``request.client.host``.
    """
    settings = settings or get_settings()
    if settings.trust_proxy:
        xff = request.headers.get("x-forwarded-for") or request.headers.get(
            "X-Forwarded-For"
        )
        if xff:
            # "client, proxy1, proxy2" — first hop is the client.
            first = xff.split(",")[0].strip()
            if first:
                return first
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _window_hits(bucket: Deque[float], now: float, window_sec: float = 3600.0) -> int:
    cutoff = now - window_sec
    while bucket and bucket[0] < cutoff:
        bucket.popleft()
    return len(bucket)


async def enforce_query_rate_limit(
    request: Request,
    user: AuthUser | None,
    settings: SecuritySettings | None = None,
) -> None:
    """Per-IP hourly cap on POST /api/query (anonymous vs logged-in)."""
    settings = settings or get_settings()
    limit = (
        settings.auth_query_per_hour if user is not None else settings.anon_query_per_hour
    )
    ip = client_ip(request, settings)
    key = f"{'auth' if user else 'anon'}:{ip}"
    now = time.time()
    async with _HITS_LOCK:
        bucket = _QUERY_HITS[key]
        n = _window_hits(bucket, now)
        if n >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "rate_limited",
                    "message": (
                        f"Too many requests from this address "
                        f"({limit} per hour). Try again later."
                    ),
                },
            )
        bucket.append(now)


def reset_rate_limits() -> None:
    """Test helper."""
    _QUERY_HITS.clear()


def reset_generation_semaphore() -> None:
    """Test helper: drop the generation semaphore so size/wait re-bind."""
    global _GEN_SEMAPHORE, _GEN_SEMAPHORE_SIZE
    _GEN_SEMAPHORE = None
    _GEN_SEMAPHORE_SIZE = None


def _semaphore(settings: SecuritySettings) -> asyncio.Semaphore:
    global _GEN_SEMAPHORE, _GEN_SEMAPHORE_SIZE
    size = max(1, settings.max_concurrent_generations)
    if _GEN_SEMAPHORE is None or _GEN_SEMAPHORE_SIZE != size:
        _GEN_SEMAPHORE = asyncio.Semaphore(size)
        _GEN_SEMAPHORE_SIZE = size
    return _GEN_SEMAPHORE


class GenerationSlot:
    """Acquire a generation slot or 503 after the wait budget."""

    def __init__(self, settings: SecuritySettings | None = None):
        self.settings = settings or get_settings()
        self._acquired = False

    async def __aenter__(self) -> "GenerationSlot":
        sem = _semaphore(self.settings)
        try:
            await asyncio.wait_for(
                sem.acquire(), timeout=self.settings.generation_wait_seconds
            )
        except asyncio.TimeoutError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "error": "busy",
                    "message": "busy, try again",
                },
            ) from exc
        self._acquired = True
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._acquired:
            _semaphore(self.settings).release()
            self._acquired = False


def sniff_upload_kind(data: bytes) -> str | None:
    """Return 'pdf' | 'jpeg' | 'png' from magic bytes, else None."""
    if data[:4] == b"%PDF":
        return "pdf"
    if len(data) >= 3 and data[:3] == b"\xff\xd8\xff":
        return "jpeg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    return None


def enforce_upload_size(data: bytes, settings: SecuritySettings | None = None) -> None:
    settings = settings or get_settings()
    if len(data) > settings.max_upload_bytes:
        mb = settings.max_upload_bytes // (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail={
                "error": "upload_too_large",
                "message": f"Upload exceeds the {mb} MB limit.",
            },
        )


def enforce_upload_type(data: bytes) -> str:
    kind = sniff_upload_kind(data)
    if kind is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail={
                "error": "unsupported_type",
                "message": "Unsupported file type. PDF, JPEG, and PNG are supported.",
            },
        )
    return kind


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject non-upload JSON/form bodies larger than max_body_bytes."""

    def __init__(self, app, settings: SecuritySettings | None = None):
        super().__init__(app)
        self.settings = settings or get_settings()

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        # Multipart uploads use the upload size cap instead.
        if path.rstrip("/").endswith("/upload_document"):
            return await call_next(request)
        if request.method in {"POST", "PUT", "PATCH"}:
            cl = request.headers.get("content-length")
            if cl is not None:
                try:
                    n = int(cl)
                except ValueError:
                    n = -1
                if n > self.settings.max_body_bytes:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "error": "body_too_large",
                            "message": (
                                f"Request body exceeds the "
                                f"{self.settings.max_body_bytes} byte limit."
                            ),
                        },
                    )
        return await call_next(request)
