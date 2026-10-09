"""Deterministic Rule (statute main clause) + optional Application fields."""
from __future__ import annotations

import json
import os
import sys
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("LAWSHIFT_FIXED_CONCLUSION", "1")
os.environ.setdefault("LAWSHIFT_VERIFY_WITH_APPLICATION", "0")

from app.statute_rule import (  # noqa: E402
    main_clause_rule_text,
    rule_is_truncated,
    strip_context_prefix,
)
from app import stage4  # noqa: E402
from app.main import _build_mapping  # noqa: E402

IPC_PATH = ROOT / "data" / "clean" / "ipc_statutes.jsonl"
STATUTES_PATH = ROOT / "data" / "clean" / "statutes.jsonl"


def _load_by_chunk_id(*chunk_ids: str) -> dict[str, str]:
    want = set(chunk_ids)
    found: dict[str, str] = {}
    for path in (IPC_PATH, STATUTES_PATH):
        for line in path.open(encoding="utf-8"):
            o = json.loads(line)
            cid = o.get("chunk_id") or f"IPC_{o.get('ipc_section')}"
            if cid in want:
                found[cid] = o.get("text") or ""
                if len(found) == len(want):
                    return found
    missing = want - set(found)
    if missing:
        raise AssertionError(f"missing corpus rows: {sorted(missing)}")
    return found


def test_strip_context_prefix():
    raw = "[Context: BNS 303 Theft.] 303. Theft.—Whoever…"
    assert strip_context_prefix(raw).startswith("303.")


def test_main_clause_cuts_explanation():
    text = (
        "[Context: BNS 46.] 46. Abettor.—A person abets an offence who "
        "instigates or intentionally aids its commission. "
        "Explanation 1.—The abetment of the illegal omission of an act may amount "
        "to an offence."
    )
    rule = main_clause_rule_text(text)
    assert rule.startswith("46.")
    assert "Explanation" not in rule
    assert "abets an offence" in rule
    assert len(rule) >= 40
    assert rule_is_truncated(text, rule) is True


def test_main_clause_cuts_provided_that():
    text = (
        "100. Right of private defence.—Nothing is an offence. "
        "Provided that there is no time to have recourse to the public authorities."
    )
    rule = main_clause_rule_text(text)
    assert "Provided that" not in rule
    assert "Nothing is an offence" in rule
    assert rule.endswith("offence.")


def test_main_clause_keeps_except_in_definition():
    """'Except in the cases…' is part of the main clause, not an Exception label."""
    text = (
        "101. Murder.—Except in the cases hereinafter excepted, culpable homicide "
        "is murder,— (a) if the act by which the death is caused is done with the "
        "intention of causing death."
    )
    rule = main_clause_rule_text(text)
    assert rule.startswith("101.")
    assert "Except in the cases hereinafter excepted" in rule


def test_false_positive_cuts_gone_corpus_cases():
    """Former mid-sentence false positives must not recur.

    IPC_7 / IPC_85 / IPC_94 / BNS_23: no anchored marker → full cleaned text.
    IPC_499 / BNS_3: may still cut at a real capitalised Illustration(s) block;
    they must not end on the old false-positive tails.
    """
    texts = _load_by_chunk_id(
        "IPC_499", "IPC_7", "IPC_85", "IPC_94", "BNS_3", "BNS_23"
    )
    full_only = {"IPC_7", "IPC_85", "IPC_94", "BNS_23"}
    for cid, text in texts.items():
        cleaned = strip_context_prefix(text)
        rule = main_clause_rule_text(text)
        assert cleaned.startswith(rule), cid
        # Old false-positive endings (case-insensitive mid-sentence cuts).
        assert not rule.rstrip().endswith("conformity with the"), cid
        assert not rule.rstrip().endswith("within the"), cid
        assert not rule.rstrip().endswith("benefit of this"), cid
        assert not rule.rstrip().endswith("contrary to law;"), cid
        if cid in full_only:
            assert rule == cleaned, f"{cid}: unexpected truncation"
            assert rule_is_truncated(text, rule) is False
        else:
            # Safe Illustration cut is OK; mid-sentence 'exception.' cut is not.
            assert "cashierare within the" not in rule
            if rule != cleaned:
                assert rule_is_truncated(text, rule) is True
                assert len(rule) >= 40


def test_proviso_bnss_413_weak_end_falls_back():
    """Line-start Provided that after 'of' must fall back to full text."""
    texts = _load_by_chunk_id("BNSS_413")
    text = texts["BNSS_413"]
    cleaned = strip_context_prefix(text)
    rule = main_clause_rule_text(text)
    assert rule == cleaned
    assert "Provided that" in rule
    assert rule_is_truncated(text, rule) is False


def test_proviso_ipc_376ab_handling():
    """IPC_376AB: safe proviso cut kept, or full text if cut would be weak."""
    texts = _load_by_chunk_id("IPC_376AB")
    text = texts["IPC_376AB"]
    cleaned = strip_context_prefix(text)
    rule = main_clause_rule_text(text)
    assert cleaned.startswith(rule)
    if rule != cleaned:
        assert "Provided that" not in rule
        assert len(rule) >= 40
        assert not rule.rstrip().endswith(
            ("of", "the", "to", "a", "an", "and", "or", "by", "in", "for", "with", "under")
        )
        assert rule[-1] not in {":", ";", ","}
        assert rule_is_truncated(text, rule) is True
    else:
        # Fallback is acceptable when the only cut ends weakly.
        assert "Provided that" in rule
        assert rule_is_truncated(text, rule) is False


def test_rule_verbatim_prefix_all_1621_sections():
    """Rule is always an exact prefix of cleaned full text (never rewritten)."""
    n = 0
    for path in (IPC_PATH, STATUTES_PATH):
        for line in path.open(encoding="utf-8"):
            o = json.loads(line)
            text = o.get("text") or ""
            cleaned = strip_context_prefix(text)
            rule = main_clause_rule_text(text)
            assert cleaned.startswith(rule), (
                o.get("chunk_id") or o.get("ipc_section"),
                rule[:80],
            )
            n += 1
    assert n == 1621


def test_build_mapping_uses_statute_rule_not_model(monkeypatch):
    chunk = SimpleNamespace(
        text=(
            "[Context: IPC 292.] 292. Sale of obscene books.—Whoever sells any "
            "obscene book shall be punished. Exception.—This section does not "
            "extend to any book kept for religious purposes."
        ),
        act="IPC",
        section_number="292",
        section_title="Sale of obscene books",
        chunk_id="IPC_292",
    )

    def fake_generate(question, retrieved_text, source_citation):
        return (
            "Issue: Whether selling magazines engages the section.\n"
            "Application: The facts describe a sale of magazines.\n"
        )

    def fake_verify(rule_text, conclusion_text, application_text=None):
        fake_verify.last = (rule_text, conclusion_text, application_text)
        return "SUPPORTED", "stub"

    monkeypatch.setattr(stage4, "generate_irac", fake_generate)
    monkeypatch.setattr(stage4, "verify_rule_only_14b_v2", fake_verify)
    monkeypatch.setattr(
        "app.main.stage3.option_description",
        lambda c: c.section_title or "",
    )

    resp = _build_mapping(
        message="On 25 June 2024, a bookstore sold magazines.",
        offense_date=date(2024, 6, 25),
        matched_text="25 June 2024",
        reason="explicit",
        route="IPC",
        top_chunk=chunk,  # type: ignore[arg-type]
        retrieve_detail="stub",
        language="en",
    )
    assert resp.kind == "mapping"
    assert "Exception" not in resp.irac["rule"]
    assert "Whoever sells any obscene book" in resp.irac["rule"]
    assert resp.irac["rule"] == main_clause_rule_text(chunk.text)
    assert resp.rule_truncated is True
    assert "Exception" in resp.sources[0].text
    assert resp.application_generated is True
    assert resp.application_text == resp.irac["application"]
    assert "magazines" in (resp.application_text or "")
    assert resp.fixed_conclusion is not None
    assert "appears to fall within" in resp.irac["conclusion"]
    assert fake_verify.last[0] == resp.irac["rule"]
    assert fake_verify.last[2] is None


def test_build_mapping_verify_with_application_flag(monkeypatch):
    chunk = SimpleNamespace(
        text="303. Theft.—Whoever commits theft shall be punished with imprisonment.",
        act="BNS",
        section_number="303",
        section_title="Theft",
        chunk_id="BNS_303",
    )

    def fake_generate(question, retrieved_text, source_citation):
        return (
            "Issue: Whether the facts engage theft.\n"
            "Application: Taking without consent may engage the section.\n"
        )

    def fake_verify(rule_text, conclusion_text, application_text=None):
        fake_verify.last = (rule_text, conclusion_text, application_text)
        return "NOT_SUPPORTED", "stub flag"

    monkeypatch.setattr(stage4, "generate_irac", fake_generate)
    monkeypatch.setattr(stage4, "verify_rule_only_14b_v2", fake_verify)
    monkeypatch.setattr(
        "app.main.stage3.option_description",
        lambda c: c.section_title or "",
    )
    monkeypatch.setenv("LAWSHIFT_VERIFY_WITH_APPLICATION", "1")

    resp = _build_mapping(
        message="On 10 August 2024, a person took a phone from a table.",
        offense_date=date(2024, 8, 10),
        matched_text="10 August 2024",
        reason="explicit",
        route="BNS",
        top_chunk=chunk,  # type: ignore[arg-type]
        retrieve_detail="stub",
        language="en",
    )
    assert resp.verification["flagged"] is True
    assert fake_verify.last[2] == resp.irac["application"]
    assert resp.rule_truncated is False


def test_hi_skips_rule_translation_keeps_number_guard(monkeypatch):
    chunk = SimpleNamespace(
        text="303. Theft.—Whoever commits theft shall be punished.",
        act="BNS",
        section_number="303",
        section_title="Theft",
        chunk_id="BNS_303",
    )
    statute_rule = main_clause_rule_text(chunk.text)

    def fake_generate(question, retrieved_text, source_citation):
        return (
            "Issue: Whether section 303 applies on 10 August 2024.\n"
            "Application: The facts may engage section 303.\n"
        )

    def fake_verify(rule_text, conclusion_text, application_text=None):
        return "SUPPORTED", "stub"

    def fake_translate(irac, target_lang="hi", skip_fields=None):
        skip = {x.lower() for x in (skip_fields or set())}
        assert "rule" in skip
        assert "conclusion" in skip
        out = dict(irac)
        for k, v in list(out.items()):
            if k.lower() in skip or not isinstance(v, str):
                continue
            out[k] = f"[hi] {v}"
        return out, "ollama_fallback", None, []

    monkeypatch.setattr(stage4, "generate_irac", fake_generate)
    monkeypatch.setattr(stage4, "verify_rule_only_14b_v2", fake_verify)
    monkeypatch.setattr("app.main.stage5_translate.translate_irac", fake_translate)
    monkeypatch.setattr(
        "app.main.stage3.option_description",
        lambda c: c.section_title or "",
    )
    monkeypatch.setenv("LAWSHIFT_VERIFY_WITH_APPLICATION", "0")

    resp = _build_mapping(
        message="On 10 August 2024, a person took a phone.",
        offense_date=date(2024, 8, 10),
        matched_text="10 August 2024",
        reason="explicit",
        route="BNS",
        top_chunk=chunk,  # type: ignore[arg-type]
        retrieve_detail="stub",
        language="hi",
    )
    assert resp.irac["rule"] == statute_rule
    assert resp.irac["issue"].startswith("[hi]")
    assert (resp.application_text or "").startswith("[hi]")
    assert "appears to fall within" in resp.irac["conclusion"]


def test_verify_with_application_enabled_default_off(monkeypatch):
    monkeypatch.delenv("LAWSHIFT_VERIFY_WITH_APPLICATION", raising=False)
    assert stage4.verify_with_application_enabled() is False
    monkeypatch.setenv("LAWSHIFT_VERIFY_WITH_APPLICATION", "1")
    assert stage4.verify_with_application_enabled() is True
