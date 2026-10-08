"""Security hardening tests — local keys only, no network / no Supabase."""
from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import Depends, FastAPI, Request
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Disposable RSA key pair for this process (never logged / never written to disk).
_PRIV = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_PRIV_PEM = _PRIV.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
).decode()
_PUB_PEM = (
    _PRIV.public_key()
    .public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    .decode()
)

_ISSUER = "https://example-test.supabase.co/auth/v1"
_AUD = "authenticated"

os.environ["SUPABASE_URL"] = "https://example-test.supabase.co"
os.environ["LAWSHIFT_JWT_AUDIENCE"] = _AUD
os.environ["LAWSHIFT_JWT_TEST_PUBLIC_KEY_PEM"] = _PUB_PEM
os.environ["LAWSHIFT_ALLOWED_ORIGINS"] = "http://localhost:3000"
os.environ["LAWSHIFT_ENABLE_DOCS"] = "0"
os.environ["LAWSHIFT_TRUST_PROXY"] = "0"
os.environ["LAWSHIFT_ANON_QUERY_PER_HOUR"] = "3"
os.environ["LAWSHIFT_AUTH_QUERY_PER_HOUR"] = "100"
os.environ["LAWSHIFT_MAX_CONCURRENT"] = "1"
os.environ["LAWSHIFT_GENERATION_WAIT_SEC"] = "0.2"
os.environ["LAWSHIFT_MAX_UPLOAD_BYTES"] = "1024"
os.environ["LAWSHIFT_MAX_BODY_BYTES"] = "512"
os.environ.pop("SUPABASE_JWT_SECRET", None)

from app.auth_supabase import (  # noqa: E402
    optional_auth,
    require_auth,
    reset_jwks_cache,
    verify_access_token,
)
from app.limits import (  # noqa: E402
    BodySizeLimitMiddleware,
    GenerationSlot,
    client_ip,
    enforce_query_rate_limit,
    enforce_upload_size,
    enforce_upload_type,
    reset_generation_semaphore,
    reset_rate_limits,
    sniff_upload_kind,
)
from app.security_settings import SecuritySettings  # noqa: E402


def _settings() -> SecuritySettings:
    return SecuritySettings.from_environ()


def _mint(
    *,
    aud: str = _AUD,
    exp_delta: timedelta = timedelta(hours=1),
    sub: str = "user-test-1",
    tamper: bool = False,
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "role": "authenticated",
        "aud": aud,
        "iss": _ISSUER,
        "iat": int(now.timestamp()),
        "exp": int((now + exp_delta).timestamp()),
        "email": "test@example.com",
    }
    token = jwt.encode(payload, _PRIV_PEM, algorithm="RS256")
    if tamper:
        head, body, sig = token.split(".")
        flipped = ("A" if not sig.startswith("A") else "B") + sig[1:]
        token = f"{head}.{body}.{flipped}"
    return token


@pytest.fixture(autouse=True)
def _reset_state():
    reset_rate_limits()
    reset_jwks_cache()
    reset_generation_semaphore()
    os.environ["LAWSHIFT_JWT_TEST_PUBLIC_KEY_PEM"] = _PUB_PEM
    os.environ["LAWSHIFT_MAX_UPLOAD_BYTES"] = "1024"
    os.environ["LAWSHIFT_MAX_BODY_BYTES"] = "512"
    os.environ["LAWSHIFT_ANON_QUERY_PER_HOUR"] = "3"
    os.environ["LAWSHIFT_MAX_CONCURRENT"] = "1"
    os.environ["LAWSHIFT_GENERATION_WAIT_SEC"] = "0.2"
    yield
    reset_rate_limits()
    reset_jwks_cache()
    reset_generation_semaphore()


# ---------------------------------------------------------------------------
# JWT verification
# ---------------------------------------------------------------------------


def test_valid_token():
    claims = verify_access_token(_mint(), _settings())
    assert claims["sub"] == "user-test-1"
    assert claims["aud"] == _AUD


def test_expired_token():
    token = _mint(exp_delta=timedelta(seconds=-10))
    with pytest.raises(Exception) as ei:
        verify_access_token(token, _settings())
    assert ei.value.status_code == 401
    assert "expired" in ei.value.detail["message"].lower()


def test_wrong_audience():
    token = _mint(aud="anon")
    with pytest.raises(Exception) as ei:
        verify_access_token(token, _settings())
    assert ei.value.status_code == 401
    assert "audience" in ei.value.detail["message"].lower()


def test_tampered_token():
    token = _mint(tamper=True)
    with pytest.raises(Exception) as ei:
        verify_access_token(token, _settings())
    assert ei.value.status_code == 401


def test_missing_token_optional():
    app = FastAPI()

    @app.get("/t")
    async def t(user=Depends(optional_auth)):
        return {"anon": user is None}

    with TestClient(app) as client:
        r = client.get("/t")
        assert r.status_code == 200
        assert r.json()["anon"] is True


def test_require_auth_missing():
    app = FastAPI()

    @app.get("/t")
    async def t(user=Depends(require_auth)):
        return {"sub": user.sub}

    with TestClient(app) as client:
        r = client.get("/t")
        assert r.status_code == 401
        assert r.json()["detail"]["error"] == "unauthorized"


def test_require_auth_valid():
    app = FastAPI()

    @app.get("/t")
    async def t(user=Depends(require_auth)):
        return {"sub": user.sub}

    with TestClient(app) as client:
        r = client.get("/t", headers={"Authorization": f"Bearer {_mint()}"})
        assert r.status_code == 200
        assert r.json()["sub"] == "user-test-1"


def test_bad_token_on_optional_is_401():
    app = FastAPI()

    @app.post("/api/query")
    async def q(user=Depends(optional_auth)):
        return {"ok": True, "anon": user is None}

    with TestClient(app) as client:
        r = client.post(
            "/api/query",
            headers={"Authorization": f"Bearer {_mint(tamper=True)}"},
        )
        assert r.status_code == 401


# ---------------------------------------------------------------------------
# Chat anonymous + upload requires token
# ---------------------------------------------------------------------------


def test_anonymous_allowed_on_chat_route():
    app = FastAPI()

    @app.post("/api/query")
    async def q(user=Depends(optional_auth)):
        return {"ok": True, "anon": user is None}

    with TestClient(app) as client:
        r = client.post("/api/query")
        assert r.status_code == 200, r.text
        assert r.json()["anon"] is True


def test_upload_requires_token():
    app = FastAPI()

    @app.post("/api/upload_document")
    async def up(user=Depends(require_auth)):
        return {"sub": user.sub}

    with TestClient(app) as client:
        r = client.post("/api/upload_document")
        assert r.status_code == 401
        r2 = client.post(
            "/api/upload_document",
            headers={"Authorization": f"Bearer {_mint()}"},
        )
        assert r2.status_code == 200


# ---------------------------------------------------------------------------
# Rate limit + busy
# ---------------------------------------------------------------------------


def test_rate_limit_anonymous():
    app = FastAPI()

    @app.post("/api/query")
    async def q(request: Request, user=Depends(optional_auth)):
        await enforce_query_rate_limit(request, user, _settings())
        return {"ok": True}

    with TestClient(app) as client:
        assert client.post("/api/query").status_code == 200
        assert client.post("/api/query").status_code == 200
        assert client.post("/api/query").status_code == 200
        r = client.post("/api/query")
        assert r.status_code == 429
        assert r.json()["detail"]["error"] == "rate_limited"


def test_busy_generation_slot():
    async def run():
        settings = _settings()
        async with GenerationSlot(settings):
            with pytest.raises(Exception) as ei:
                async with GenerationSlot(settings):
                    pass
            assert ei.value.status_code == 503
            assert ei.value.detail["error"] == "busy"
            assert "busy" in ei.value.detail["message"]

    asyncio.run(run())


# ---------------------------------------------------------------------------
# Upload sniff / size / proxy IP / body limit / docs
# ---------------------------------------------------------------------------


def test_sniff_pdf_jpeg_png():
    assert sniff_upload_kind(b"%PDF-1.4...") == "pdf"
    assert sniff_upload_kind(b"\xff\xd8\xff\xe0rest") == "jpeg"
    assert sniff_upload_kind(b"\x89PNG\r\n\x1a\nrest") == "png"
    assert sniff_upload_kind(b"not-a-file") is None


def test_upload_size_cap():
    with pytest.raises(Exception) as ei:
        enforce_upload_size(b"x" * 2000, _settings())
    assert ei.value.status_code == 413


def test_upload_type_rejected():
    with pytest.raises(Exception) as ei:
        enforce_upload_type(b"MZ\x90\x00")
    assert ei.value.status_code == 415


def test_client_ip_direct_and_forwarded():
    settings = _settings()
    app = FastAPI()

    @app.get("/ip")
    async def ip(request: Request):
        return {"ip": client_ip(request, settings)}

    with TestClient(app) as client:
        r = client.get("/ip")
        assert r.status_code == 200
        assert r.json()["ip"] in {"testclient", "127.0.0.1"}

    trusted = SecuritySettings(
        supabase_url=settings.supabase_url,
        supabase_jwt_secret=settings.supabase_jwt_secret,
        jwt_audience=settings.jwt_audience,
        jwt_test_public_key_pem=settings.jwt_test_public_key_pem,
        allowed_origins=list(settings.allowed_origins),
        enable_docs=settings.enable_docs,
        trust_proxy=True,
        anon_query_per_hour=settings.anon_query_per_hour,
        auth_query_per_hour=settings.auth_query_per_hour,
        max_concurrent_generations=settings.max_concurrent_generations,
        generation_wait_seconds=settings.generation_wait_seconds,
        max_upload_bytes=settings.max_upload_bytes,
        max_body_bytes=settings.max_body_bytes,
        extract_per_hour=settings.extract_per_hour,
        max_concurrent_extract=settings.max_concurrent_extract,
        extract_wait_seconds=settings.extract_wait_seconds,
    )
    app2 = FastAPI()

    @app2.get("/ip")
    async def ip2(request: Request):
        return {"ip": client_ip(request, trusted)}

    with TestClient(app2) as client:
        r = client.get("/ip", headers={"X-Forwarded-For": "203.0.113.9, 10.0.0.1"})
        assert r.json()["ip"] == "203.0.113.9"


def test_body_size_middleware():
    app = FastAPI()
    app.add_middleware(BodySizeLimitMiddleware, settings=_settings())

    @app.post("/api/query")
    async def q():
        return {"ok": True}

    with TestClient(app) as client:
        r = client.post(
            "/api/query",
            content=b"x" * 600,
            headers={"content-length": "600", "content-type": "application/json"},
        )
        assert r.status_code == 413
        assert r.json()["error"] == "body_too_large"


def test_docs_disabled_by_default_setting():
    assert _settings().enable_docs is False
