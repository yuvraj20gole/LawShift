"""Supabase access-token verification for FastAPI.

Prefer JWKS at ``{SUPABASE_URL}/auth/v1/.well-known/jwks.json`` (asymmetric
signing keys — this project currently publishes ES256 keys there). Fall back
to ``SUPABASE_JWT_SECRET`` (HS256 legacy shared secret) when JWKS is empty
or unreachable and the secret is set.

For offline tests, set ``LAWSHIFT_JWT_TEST_PUBLIC_KEY_PEM`` to a PEM public
key and mint tokens with the matching private key; no network is used.

Never logs the token value.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

import jwt
from fastapi import Depends, HTTPException, Request, status
from jwt import PyJWKClient

from .security_settings import SecuritySettings, get_settings

log = logging.getLogger("lawshift.auth")

_JWKS_CLIENT: PyJWKClient | None = None
_JWKS_CLIENT_URL: str | None = None
_JWKS_EMPTY_UNTIL: float = 0.0


@dataclass(frozen=True)
class AuthUser:
    """Minimal verified claims from a Supabase access token."""

    sub: str
    role: str
    email: str | None = None


def _jwks_url(settings: SecuritySettings) -> str:
    return f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"


def _issuer(settings: SecuritySettings) -> str:
    return f"{settings.supabase_url}/auth/v1"


def _get_jwks_client(settings: SecuritySettings) -> PyJWKClient | None:
    """Cached JWKS client. Returns None when the set is empty (legacy HS256)."""
    global _JWKS_CLIENT, _JWKS_CLIENT_URL, _JWKS_EMPTY_UNTIL
    url = _jwks_url(settings)
    now = time.time()
    if _JWKS_EMPTY_UNTIL and now < _JWKS_EMPTY_UNTIL and _JWKS_CLIENT_URL == url:
        return None
    if _JWKS_CLIENT is not None and _JWKS_CLIENT_URL == url:
        return _JWKS_CLIENT
    try:
        client = PyJWKClient(url, cache_keys=True, lifespan=600)
        # Probe once: empty keys means legacy shared-secret mode.
        jwks = client.fetch_data()
        keys = (jwks or {}).get("keys") or []
        if not keys:
            _JWKS_CLIENT = None
            _JWKS_CLIENT_URL = url
            _JWKS_EMPTY_UNTIL = now + 300
            log.info("JWKS has no keys; will use SUPABASE_JWT_SECRET if set")
            return None
        _JWKS_CLIENT = client
        _JWKS_CLIENT_URL = url
        _JWKS_EMPTY_UNTIL = 0.0
        return client
    except Exception as exc:  # noqa: BLE001 — network/cache errors
        log.warning("JWKS fetch failed (%s); trying JWT secret fallback", type(exc).__name__)
        return None


def reset_jwks_cache() -> None:
    """Test helper: drop cached JWKS client."""
    global _JWKS_CLIENT, _JWKS_CLIENT_URL, _JWKS_EMPTY_UNTIL
    _JWKS_CLIENT = None
    _JWKS_CLIENT_URL = None
    _JWKS_EMPTY_UNTIL = 0.0


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"error": "unauthorized", "message": detail},
        headers={"WWW-Authenticate": "Bearer"},
    )


def extract_bearer(request: Request) -> str | None:
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth:
        return None
    parts = auth.split(None, 1)
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        raise _unauthorized("Authorization header must be Bearer <token>")
    return parts[1].strip()


def verify_access_token(
    token: str,
    settings: SecuritySettings | None = None,
) -> dict[str, Any]:
    """Verify signature, expiry and audience. Raises HTTPException on failure."""
    settings = settings or get_settings()
    options = {
        "require": ["exp", "aud"],
        "verify_aud": True,
        "verify_exp": True,
        "verify_signature": True,
    }
    audience = settings.jwt_audience
    issuer = _issuer(settings)

    # 1) Offline / unit-test public key (no network).
    if settings.jwt_test_public_key_pem:
        try:
            return jwt.decode(
                token,
                settings.jwt_test_public_key_pem,
                algorithms=["RS256", "ES256", "ES384", "ES512"],
                audience=audience,
                issuer=issuer,
                options=options,
            )
        except jwt.ExpiredSignatureError as exc:
            raise _unauthorized("Token expired") from exc
        except jwt.InvalidAudienceError as exc:
            raise _unauthorized("Invalid token audience") from exc
        except jwt.InvalidIssuerError as exc:
            raise _unauthorized("Invalid token issuer") from exc
        except jwt.PyJWTError as exc:
            raise _unauthorized("Invalid or tampered token") from exc

    # 2) Prefer JWKS (asymmetric — current Supabase signing keys).
    client = _get_jwks_client(settings)
    if client is not None:
        try:
            signing_key = client.get_signing_key_from_jwt(token)
            return jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256", "ES256", "ES384", "ES512"],
                audience=audience,
                issuer=issuer,
                options=options,
            )
        except jwt.ExpiredSignatureError as exc:
            raise _unauthorized("Token expired") from exc
        except jwt.InvalidAudienceError as exc:
            raise _unauthorized("Invalid token audience") from exc
        except jwt.InvalidIssuerError as exc:
            raise _unauthorized("Invalid token issuer") from exc
        except jwt.PyJWTError as exc:
            raise _unauthorized("Invalid or tampered token") from exc
        except Exception as exc:  # noqa: BLE001
            log.warning("JWKS verify failed (%s)", type(exc).__name__)
            raise _unauthorized("Invalid or tampered token") from exc

    # 3) Legacy shared secret (HS256) when JWKS has no keys.
    if settings.supabase_jwt_secret:
        try:
            return jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                audience=audience,
                issuer=issuer,
                options=options,
            )
        except jwt.ExpiredSignatureError as exc:
            raise _unauthorized("Token expired") from exc
        except jwt.InvalidAudienceError as exc:
            raise _unauthorized("Invalid token audience") from exc
        except jwt.InvalidIssuerError as exc:
            raise _unauthorized("Invalid token issuer") from exc
        except jwt.PyJWTError as exc:
            raise _unauthorized("Invalid or tampered token") from exc

    raise _unauthorized("Auth is not configured on the server")


def claims_to_user(claims: dict[str, Any]) -> AuthUser:
    sub = str(claims.get("sub") or "")
    if not sub:
        raise _unauthorized("Token missing subject")
    role = str(claims.get("role") or "authenticated")
    email = claims.get("email")
    return AuthUser(sub=sub, role=role, email=str(email) if email else None)


async def optional_auth(request: Request) -> AuthUser | None:
    """Bearer optional: missing → anonymous; present but bad → 401.

    Do not take ``SecuritySettings`` as a plain parameter: FastAPI would treat
    it as a second body model and nest the real body under the route's
    parameter name (``req``), yielding 422 ``body.req`` missing.
    """
    settings = get_settings()
    try:
        token = extract_bearer(request)
    except HTTPException:
        raise
    if token is None:
        return None
    claims = verify_access_token(token, settings)
    return claims_to_user(claims)


async def require_auth(request: Request) -> AuthUser:
    """Bearer required."""
    user = await optional_auth(request)
    if user is None:
        raise _unauthorized("Authentication required")
    return user


# FastAPI Depends aliases
OptionalUser = Depends(optional_auth)
RequiredUser = Depends(require_auth)
