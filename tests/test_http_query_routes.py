"""HTTP-level tests for /api/query and resolve — TestClient on the real app.

Pipeline (handle_query / resolve_bifurcation) is stubbed so no models run.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

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
os.environ["LAWSHIFT_MAX_CONCURRENT"] = "2"
os.environ["LAWSHIFT_GENERATION_WAIT_SEC"] = "5"
os.environ.pop("SUPABASE_JWT_SECRET", None)

from app.limits import reset_generation_semaphore, reset_rate_limits  # noqa: E402
from app.main import app  # noqa: E402
from app.schemas import ClarifyResponse  # noqa: E402


def _mint(*, tamper: bool = False, exp_delta: timedelta = timedelta(hours=1)) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "http-test-user",
        "role": "authenticated",
        "aud": _AUD,
        "iss": _ISSUER,
        "iat": int(now.timestamp()),
        "exp": int((now + exp_delta).timestamp()),
    }
    token = jwt.encode(payload, _PRIV_PEM, algorithm="RS256")
    if tamper:
        head, body, sig = token.split(".")
        flipped = ("A" if not sig.startswith("A") else "B") + sig[1:]
        token = f"{head}.{body}.{flipped}"
    return token


STUB_CLARIFY = ClarifyResponse(
    question="stub: please give the offence date.",
    reason="missing_date",
)


@pytest.fixture(autouse=True)
def _reset_and_stub(monkeypatch):
    reset_rate_limits()
    reset_generation_semaphore()
    os.environ["LAWSHIFT_JWT_TEST_PUBLIC_KEY_PEM"] = _PUB_PEM
    os.environ["LAWSHIFT_ANON_QUERY_PER_HOUR"] = "3"

    async def stub_handle(req):
        return STUB_CLARIFY

    async def stub_resolve(req):
        return STUB_CLARIFY

    monkeypatch.setattr("app.main.handle_query", stub_handle)
    monkeypatch.setattr("app.main.resolve_bifurcation", stub_resolve)
    yield
    reset_rate_limits()
    reset_generation_semaphore()


def _client() -> TestClient:
    # Do not enter the context manager: that would run the real lifespan
    # (Stage 3 load + Ollama warm-up). Plain TestClient still serves routes.
    return TestClient(app)


def test_query_valid_body_anonymous_200():
    with _client() as client:
        r = client.post(
            "/api/query",
            json={
                "message": "theft on 25 June 2024",
                "conversation_id": "http-anon-1",
                "language": "en",
            },
        )
        assert r.status_code == 200, r.text
        assert r.json()["kind"] == "clarify"
        assert r.json()["reason"] == "missing_date"


def test_query_valid_body_with_token_200():
    with _client() as client:
        r = client.post(
            "/api/query",
            json={
                "message": "theft on 25 June 2024",
                "conversation_id": "http-auth-1",
                "language": "en",
            },
            headers={"Authorization": f"Bearer {_mint()}"},
        )
        assert r.status_code == 200, r.text
        assert r.json()["kind"] == "clarify"


def test_query_bad_token_401():
    with _client() as client:
        r = client.post(
            "/api/query",
            json={
                "message": "theft on 25 June 2024",
                "conversation_id": "http-bad-1",
                "language": "en",
            },
            headers={"Authorization": f"Bearer {_mint(tamper=True)}"},
        )
        assert r.status_code == 401
        assert r.json()["detail"]["error"] == "unauthorized"


def test_query_empty_body_422_names_fields():
    with _client() as client:
        r = client.post("/api/query", json={})
        assert r.status_code == 422
        locs = [tuple(e.get("loc", ())) for e in r.json().get("detail", [])]
        flat = " ".join(".".join(str(x) for x in loc) for loc in locs)
        assert "message" in flat
        assert "conversation_id" in flat
        # Must not nest under body.req (the hardening regression).
        assert not any(loc[:2] == ("body", "req") for loc in locs)


def test_resolve_accepts_normal_body():
    with _client() as client:
        r = client.post(
            "/api/query/resolve_bifurcation",
            json={
                "conversation_id": "http-resolve-1",
                "chosen_section": "IPC 292",
                "language": "en",
            },
        )
        assert r.status_code == 200, r.text
        assert r.json()["kind"] == "clarify"


def test_query_anon_rate_limit_429():
    with _client() as client:
        body = {
            "message": "x on 25 June 2024",
            "conversation_id": "http-rl",
            "language": "en",
        }
        assert client.post("/api/query", json={**body, "conversation_id": "http-rl-1"}).status_code == 200
        assert client.post("/api/query", json={**body, "conversation_id": "http-rl-2"}).status_code == 200
        assert client.post("/api/query", json={**body, "conversation_id": "http-rl-3"}).status_code == 200
        r = client.post("/api/query", json={**body, "conversation_id": "http-rl-4"})
        assert r.status_code == 429
        assert r.json()["detail"]["error"] == "rate_limited"
