"""Environment-backed security settings for the public API surface."""
from __future__ import annotations

import os
from dataclasses import dataclass


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    return int(raw)


def _env_str(name: str, default: str = "") -> str:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip()


@dataclass(frozen=True)
class SecuritySettings:
    supabase_url: str
    supabase_jwt_secret: str
    jwt_audience: str
    jwt_test_public_key_pem: str
    allowed_origins: list[str]
    enable_docs: bool
    trust_proxy: bool
    anon_query_per_hour: int
    auth_query_per_hour: int
    max_concurrent_generations: int
    generation_wait_seconds: float
    max_upload_bytes: int
    max_body_bytes: int
    extract_per_hour: int
    max_concurrent_extract: int
    extract_wait_seconds: float

    @classmethod
    def from_environ(cls) -> "SecuritySettings":
        origins_raw = _env_str("LAWSHIFT_ALLOWED_ORIGINS", "http://localhost:3000")
        origins = [o.strip() for o in origins_raw.split(",") if o.strip()]
        if not origins:
            origins = ["http://localhost:3000"]
        return cls(
            supabase_url=_env_str(
                "SUPABASE_URL", "https://xkrbmuljvznwchbdseyi.supabase.co"
            ).rstrip("/"),
            supabase_jwt_secret=_env_str("SUPABASE_JWT_SECRET", ""),
            jwt_audience=_env_str("LAWSHIFT_JWT_AUDIENCE", "authenticated"),
            # Tests only: PEM public key so verification needs no network.
            jwt_test_public_key_pem=_env_str("LAWSHIFT_JWT_TEST_PUBLIC_KEY_PEM", ""),
            allowed_origins=origins,
            enable_docs=_env_bool("LAWSHIFT_ENABLE_DOCS", False),
            trust_proxy=_env_bool("LAWSHIFT_TRUST_PROXY", False),
            anon_query_per_hour=_env_int("LAWSHIFT_ANON_QUERY_PER_HOUR", 12),
            auth_query_per_hour=_env_int("LAWSHIFT_AUTH_QUERY_PER_HOUR", 120),
            max_concurrent_generations=_env_int("LAWSHIFT_MAX_CONCURRENT", 2),
            generation_wait_seconds=float(
                os.environ.get("LAWSHIFT_GENERATION_WAIT_SEC", "45")
            ),
            max_upload_bytes=_env_int("LAWSHIFT_MAX_UPLOAD_BYTES", 10 * 1024 * 1024),
            max_body_bytes=_env_int("LAWSHIFT_MAX_BODY_BYTES", 100 * 1024),
            extract_per_hour=_env_int("LAWSHIFT_EXTRACT_PER_HOUR", 10),
            max_concurrent_extract=_env_int("LAWSHIFT_MAX_CONCURRENT_EXTRACT", 1),
            extract_wait_seconds=float(
                os.environ.get("LAWSHIFT_EXTRACT_WAIT_SEC", "20")
            ),
        )


def get_settings() -> SecuritySettings:
    return SecuritySettings.from_environ()
