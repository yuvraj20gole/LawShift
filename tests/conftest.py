"""Pytest defaults so importing app.main does not require a real Supabase project."""
from __future__ import annotations

import os

os.environ.setdefault("SUPABASE_URL", "https://example-test.supabase.co")
