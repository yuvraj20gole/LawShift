"""In-memory attached case facts + date lock per conversation.

Files live in Supabase (browser upload). The backend only keeps confirmed
facts_text and offence_date for follow-ups, with TTL and ownership checks.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal

ATTACH_TTL_SEC = 2 * 60 * 60
ATTACH_MAX_CONVERSATIONS = 200
DATE_MIN = date(1860, 1, 1)


@dataclass
class AttachedCase:
    user_id: str
    facts_text: str
    offence_date: date
    date_source: Literal["document", "edited"]
    filename: str | None
    attached_at: float


_ATTACHED: dict[str, AttachedCase] = {}


def reset_attached_cases() -> None:
    """Test helper."""
    _ATTACHED.clear()


def _purge_expired(now: float | None = None) -> None:
    now = now if now is not None else time.time()
    expired = [
        cid
        for cid, row in _ATTACHED.items()
        if now - row.attached_at > ATTACH_TTL_SEC
    ]
    for cid in expired:
        _ATTACHED.pop(cid, None)


def _evict_oldest_if_needed() -> None:
    while len(_ATTACHED) > ATTACH_MAX_CONVERSATIONS:
        oldest_cid = min(_ATTACHED.items(), key=lambda kv: kv[1].attached_at)[0]
        _ATTACHED.pop(oldest_cid, None)


def get_attached(conversation_id: str) -> AttachedCase | None:
    _purge_expired()
    return _ATTACHED.get(conversation_id)


def attach_case(
    *,
    conversation_id: str,
    user_id: str,
    facts_text: str,
    offence_date: date,
    date_source: Literal["document", "edited"],
    filename: str | None,
) -> AttachedCase:
    _purge_expired()
    row = AttachedCase(
        user_id=user_id,
        facts_text=facts_text,
        offence_date=offence_date,
        date_source=date_source,
        filename=filename,
        attached_at=time.time(),
    )
    _ATTACHED[conversation_id] = row
    _evict_oldest_if_needed()
    return row


def detach_case(*, conversation_id: str, user_id: str) -> AttachedCase | None:
    """Remove attach if present and owned by user_id. Returns removed row."""
    _purge_expired()
    row = _ATTACHED.get(conversation_id)
    if row is None:
        return None
    if row.user_id != user_id:
        raise PermissionError("not_owner")
    return _ATTACHED.pop(conversation_id)


def require_owner(conversation_id: str, user_id: str) -> AttachedCase:
    row = get_attached(conversation_id)
    if row is None:
        raise KeyError("not_found")
    if row.user_id != user_id:
        raise PermissionError("not_owner")
    return row


def parse_offence_date(iso: str) -> date:
    """Validate YYYY-MM-DD: real date, not future, not before 1860-01-01."""
    try:
        d = date.fromisoformat((iso or "").strip())
    except ValueError as exc:
        raise ValueError("invalid_date") from exc
    today = datetime.now().date()
    if d > today:
        raise ValueError("future_date")
    if d < DATE_MIN:
        raise ValueError("too_old")
    return d


def attached_count_for_tests() -> int:
    _purge_expired()
    return len(_ATTACHED)
