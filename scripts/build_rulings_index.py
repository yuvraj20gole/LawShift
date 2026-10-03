#!/usr/bin/env python3
"""Build data/rulings_index.json from free OpenNyAI-style judgment archives.

Metadata only (parquet). Anonymous S3 access. No API keys, no models, no HTML scraping.

Buckets (ap-south-1):
  - indian-supreme-court-judgments
  - indian-high-court-judgments  (Bombay High Court = court=27_1)
"""
from __future__ import annotations

import io
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

import boto3
import pyarrow.parquet as pq
from botocore import UNSIGNED
from botocore.config import Config

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "data" / "rulings_index.json"

SC_BUCKET = "indian-supreme-court-judgments"
HC_BUCKET = "indian-high-court-judgments"
REGION = "ap-south-1"
BOMBAY_COURT_PREFIX = "court=27_1"
PER_COURT_SC = 200
BOMBAY_PER_WEEK = 60
BOMBAY_WEEKS = 26
# Synthetic / QA partition under court=27_1 — skip.
BOMBAY_SKIP_BENCHES = frozenset({"testcase"})

# Substantive merits outcomes kept for Bombay (normalized UPPER).
# Routine "DISPOSED OFF" / withdrawals / transfers are listed separately and excluded.
BOMBAY_OUTCOMES_KEPT = frozenset(
    {
        "ALLOWED",
        "APPLICATION ALLOWED",
        "GRANTED",
        "DISMISSED",
        "REJECTED",
        "ADMITTED/ALLOWED/GRANTED/RULE ABSOLUTE",
        "ADMITTED/ALLWD/GRANTED/RULE ABSOLUTE",
        "RULE MADE ABSOLUTE",
        "RULE ABSOLUTE",
        "ABSOLUTE",
        "RULE DISCHARGED",
        "PARTLY ALLOWED",
        "PARTLY ALLOWED AND PARTLY DISMISSED",
        "BAIL GRANTED",
        "BAIL REJECTED",
        "ANTICIPATORY BAIL REJECTED",
        "BAIL GRANTED / REJECTED",
        "DISMISSED FOR NON-COMPLYING CONDITIONAL ORDER",
        "DISMISSED/RULE DISCHARGED",
        "REJECTED AT ADMISSION STAGE",
        "REJECTED FOR NOT REMOVING OFFICE OBJECTIONS",
        "REJECTED U/S 986",
        "REJECTED /DISPOSED OF AT ADMISSION STAGE(EXCEPT APPEAL)",
        "DISCHARGED",
        "DECREE",
        "EX-PARTE DECREE",
        "DECREE ON ADMISSION",
        "REMANDED BACK",
        "DELAY CONDONATED/REJECTED.",
        "JUDGEMENT",
        "APPEAL ALLOWED/REVERSED",
        "APPEAL DISMISSED",
        "ENHANCED",
        "MODIFIED",
        "EXPARTY DECISION AT ADMISSION STAGE",
        "PLAINT RETURNED TO PLAINTIFF",
    }
)

# Explicit routine / administrative outcomes excluded for Bombay (normalized UPPER).
BOMBAY_OUTCOMES_EXCLUDED = frozenset(
    {
        "DISPOSED OFF",
        "DISPOSED-OFF",
        "DISPOSED OF",
        "C.A. DISPOSED OFF",
        "OTHER DISPOSED OFF",
        "OTHERS DISPOSED- OFF",
        "DISPOSED AT ADMISSION STAGE",
        "ADMITTED AND DISPOSED OFF",
        "DISPOSED OFF AS WITHDRAWN",
        "DISPOSED OFF AS A WITHDRAWN",
        "DISPOSED OFF (CONVERTED TO CRIMINAL)",
        "DISPOSED OFF (CONVERTED TO CIVIL)",
        "DISPOSED OFF AS PER ADMINISTRATIVE ORDER",
        "DISPOSED OFF AS PER ORDER OF SUPREME COURT",
        "DISPOSED OFF/DISMISSED FOR DEFAULT",
        "WITHDRAWN",
        "ALLOWED TO BE WITHDRAWN",
        "DISMISSED AS WITHDRAWN",
        "ALLOWED TO BE WITHDRAWN AT ADMISSION STAGE",
        "TRANSFER TO OTHER COURT",
        "TRANSFER TO OTHER COURT.",
        "TRANSFER TO OTHER COURT AT ADMISSION STAGE",
        "TRANSFER TO PRINCIPAL BENCH BOMBAY",
        "TRANSFER TO AURANGABAD BENCH.",
        "TRANSFERED TO APPELLATE SIDE",
        "TRANSFERED TO OTHER COURTS",
        "TRANSFERRED TO CITY CIVIL COURT",
        "TRANSFERRED TO KOLHAPUR BENCH",
        "R AND P TRANSFERED TO NAGPUR BENCH",
        "GRANT ISSUED",
        "CONVERTED TO OTHER TYPE",
        "SPEAKING TO MINUTES",
        "CERTIFIED COPY ISSUE",
        # Default / non-prosecution dismissals (not merits)
        "DISSMISS FOR DEFAULT/NON-PROSECUTION",
        "DISMISSED FOR NON-PROSECUTION/DEFAULT AT ADMISSION STAGE",
        "DISMISSED FOR NON-PROSECUTION/DEFAULT",
        "DISMISSED FOR NON PROSECUTION",
        "DISMISSED FOR NON-PROSECUTION/DEFAULT AT FINAL HEARING STAGE",
        # Non-merits closures
        "INFRUCTIOUS",
        "INFRUCTUOS",
        "ABATED",
        "APPEAL ABATED",
        "CONSENT TERM",
        "",
    }
)

# Supreme Court has no is_final; keep disposal natures that read as final merits
# disposals. Exclude empty and procedural "Directions issued".
SC_FINAL_DISPOSALS = {
    "appeal(s) allowed",
    "dismissed",
    "disposed off",
    "case partly allowed",
    "case allowed",
}

# Skip minors / POCSO / sexual-offence matters (title or case type).
SKIP_RE = re.compile(
    r"\b("
    r"pocso|"
    r"protection\s+of\s+children|"
    r"minor\b|"
    r"juvenile|"
    r"child\s+abuse|"
    r"sexual\s+offence|"
    r"sexual\s+offense|"
    r"rape\b|"
    r"molest|"
    r"outraging\s+(?:the\s+)?modesty|"
    r"section\s*376|"
    r"s\.?\s*376|"
    r"ipc\s*376|"
    r"bns\s*6[3-9]|"  # BNS sexual offence range often cited
    r"unnatural\s+offence|"
    r"indecent\s+representation"
    r")\b",
    re.IGNORECASE,
)

# Explicit case-type → branch. Keys are normalised UPPERCASE.
# Unmapped types fall through to OTHER_CASE_TYPES heuristics, then "other".
CASE_TYPE_BRANCH: dict[str, str] = {
    # --- criminal ---
    "CRL.A.": "criminal",
    "CRL.A": "criminal",
    "CRLA": "criminal",
    "CRIMINAL APPEAL": "criminal",
    "CRL.M.C.": "criminal",
    "CRL.M.C": "criminal",
    "CRLMC": "criminal",
    "CRL.REV.P.": "criminal",
    "CRL.REV.P": "criminal",
    "CRL.REV": "criminal",
    "CRIMINAL REVISION": "criminal",
    "CRL.W.P.": "criminal",
    "CRL.W.P": "criminal",
    "CRLWP": "criminal",
    "WPCR": "criminal",
    "WP(CRL)": "criminal",
    "WP (CRL)": "criminal",
    "W.P.(CRL.)": "criminal",
    "W.P.(CRL)": "criminal",
    "SLP(CRL)": "criminal",
    "SLP (CRL)": "criminal",
    "SLP(CRL.)": "criminal",
    "SPECIAL LEAVE PETITION (CRIMINAL)": "criminal",
    "CRL.A.D.": "criminal",
    "CRL.REF.": "criminal",
    "CRL.CONF.": "criminal",
    "ABA": "criminal",
    "BA": "criminal",
    "BAIL": "criminal",
    "ANTICIPATORY BAIL": "criminal",
    "CRI": "criminal",
    "CR.": "criminal",
    "CR": "criminal",
    "SESSIONS": "criminal",
    "CRIMINAL": "criminal",
    # --- civil ---
    "C.A.": "civil",
    "CA": "civil",
    "CIVIL APPEAL": "civil",
    "C.A.D.": "civil",
    "SLP(C)": "civil",
    "SLP (C)": "civil",
    "SLP(C.)": "civil",
    "SPECIAL LEAVE PETITION (CIVIL)": "civil",
    "W.P.(C)": "civil",
    "W.P.(C.)": "civil",
    "WP(C)": "civil",
    "WP (C)": "civil",
    "WRIT PETITION (CIVIL)": "civil",
    "RFA": "civil",
    "RSA": "civil",
    "SA": "civil",
    "FAO": "civil",
    "FAO(OS)": "civil",
    "CS": "civil",
    "CS(OS)": "civil",
    "SUIT": "civil",
    "CIVIL": "civil",
    "CIVIL SUIT": "civil",
    "FIRST APPEAL": "civil",
    "SECOND APPEAL": "civil",
    "EXECUTION": "civil",
    "EX": "civil",
    "MCA": "civil",
    "CAV": "civil",
    "OMP": "civil",
    "ARB": "civil",
    "ARBITRATION": "civil",
    "COMPANY": "civil",
    "CO.": "civil",
    "CP": "civil",
    "INSOLVENCY": "civil",
    "TESTAMENTARY": "civil",
    "PROBATE": "civil",
    "GUARDIANSHIP": "civil",
    "FAMILY": "civil",
    "MAT": "civil",
    "MATRIMONIAL": "civil",
    "WC": "civil",
    "LPA": "civil",
    "LETTER PATENT APPEAL": "civil",
    "AO": "civil",
    "CRA": "civil",  # often Civil Revision Application in Bombay
    "CIVIL REVISION APPLICATION": "civil",
    # Bare WP cannot be split civil/criminal from Bombay metadata → branch "writ".
    "WP": "writ",
    "W.P.": "writ",
    "WRIT PETITION": "writ",
    "PIL": "civil",
    "PUBLIC INTEREST LITIGATION": "civil",
    # Bombay High Court codes seen in metadata-mobile
    "ABA": "criminal",  # Anticipatory Bail Application
    "BA": "criminal",
    "CRIR": "criminal",  # Criminal Revision
    "CRMAB": "criminal",
    "WPCR": "criminal",
    "APEAL": "criminal",  # Bombay criminal appeal spelling variant
    "APL": "criminal",  # Application (often criminal leave) — mapped criminal when FIR fields exist; default other below overridden
    "FA": "civil",  # First Appeal
    "ARBAP": "civil",
    "ARBP": "civil",
    "CARAP": "civil",
    "CAF": "civil",
    "CAS": "civil",
    "CAW": "civil",
    "MCAM": "civil",
    "IA": "other",  # Interlocutory Application
    "APPLN": "other",
    "REVN": "other",
    "ITXA": "other",  # Income Tax Appeal
    "ALS": "other",
    "TS": "civil",  # Testamentary Suit
    "S": "other",
    "UNKNOWN": "other",
    "INSC": "other",  # Supreme Court rows without extractable type
    "CRIMINAL APPEAL": "criminal",
    "CIVIL APPEAL": "civil",
    # --- other / constitutional / tax / service / etc. ---
    "T.C.(C)": "other",
    "TRANSFER PETITION": "other",
    "TP": "other",
    "T.P.": "other",
    "CONTEMPT": "other",
    "CONT.CAS": "other",
    "REVIEW": "other",
    "CURATIVE": "other",
    "REFERENCE": "other",
    "TAX": "other",
    "ITR": "other",
    "ITA": "other",
    "CUSTOM": "other",
    "EXCISE": "other",
    "SERVICE": "other",
    "OA": "other",
    "CAT": "other",
    "ELECTION": "other",
    "EP": "other",
}

CRIMINAL_HINT = re.compile(
    r"\b(crl|criminal|bail|anticipatory|pocso|fir|sessions|ndps|ipc|bns)\b",
    re.I,
)
CIVIL_HINT = re.compile(
    r"\b(civil|rfa|rsa|suit|arbitration|matrimonial|company|probate|lpa)\b",
    re.I,
)


def s3_client():
    return boto3.client(
        "s3",
        region_name=REGION,
        config=Config(signature_version=UNSIGNED),
    )


def list_year_prefixes(s3, bucket: str) -> list[int]:
    years: list[int] = []
    token = None
    while True:
        kwargs = {"Bucket": bucket, "Prefix": "metadata/parquet/", "Delimiter": "/", "MaxKeys": 1000}
        if token:
            kwargs["ContinuationToken"] = token
        resp = s3.list_objects_v2(**kwargs)
        for p in resp.get("CommonPrefixes", []):
            m = re.search(r"year=(\d{4})/", p["Prefix"])
            if m:
                years.append(int(m.group(1)))
        token = resp.get("NextContinuationToken")
        if not token:
            break
    return sorted(set(years), reverse=True)


def read_parquet_s3(s3, bucket: str, key: str):
    obj = s3.get_object(Bucket=bucket, Key=key)
    data = obj["Body"].read()
    return pq.read_table(io.BytesIO(data))


def list_keys(s3, bucket: str, prefix: str) -> list[str]:
    keys: list[str] = []
    token = None
    while True:
        kwargs = {"Bucket": bucket, "Prefix": prefix, "MaxKeys": 1000}
        if token:
            kwargs["ContinuationToken"] = token
        resp = s3.list_objects_v2(**kwargs)
        for item in resp.get("Contents", []):
            keys.append(item["Key"])
        token = resp.get("NextContinuationToken")
        if not token:
            break
    return keys


def parse_sc_date(value) -> date | None:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(s[:10] if len(s) >= 10 and fmt.startswith("%Y") else s, fmt).date()
        except ValueError:
            continue
    # try first 10 chars as ISO
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def parse_hc_date(value) -> date | None:
    if value is None:
        return None
    if hasattr(value, "to_pydatetime"):
        try:
            return value.to_pydatetime().date()
        except Exception:
            pass
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    s = str(value).strip()
    if not s or s.lower() in {"none", "nat", "nan"}:
        return None
    # timestamp string / ISO
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s[:19] if " " in s else s[:10], fmt).date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def normalize_case_type(raw: str | None) -> str:
    if not raw:
        return "UNKNOWN"
    t = re.sub(r"\s+", " ", str(raw)).strip()
    return t or "UNKNOWN"


def sc_case_type_from_row(
    title: str,
    case_id: str | None,
    raw_html: str | None = None,
    description: str | None = None,
) -> str:
    """Supreme Court parquet has no case_type column — derive from raw_html Case No, then title."""
    text = f"{raw_html or ''} {description or ''} {title or ''} {case_id or ''}"
    # Prefer explicit "Case No" block when present
    m_case = re.search(
        r"Case\s*No\s*:?\s*</span>\s*<font[^>]*>\s*([^<]+)</font>",
        raw_html or "",
        re.I,
    )
    if m_case:
        text = m_case.group(1) + " " + text
    patterns = [
        (r"Special\s+Leave\s+Petition\s*\(\s*Criminal\s*\)", "SLP(CRL)"),
        (r"Special\s+Leave\s+Petition\s*\(\s*Civil\s*\)", "SLP(C)"),
        (r"\bSLP\s*\(\s*Crl\.?\s*\)", "SLP(CRL)"),
        (r"\bSLP\s*\(\s*C\.?\s*\)", "SLP(C)"),
        (r"Writ\s+Petition\s*\(\s*Criminal\s*\)", "W.P.(CRL)"),
        (r"Writ\s+Petition\s*\(\s*Civil\s*\)", "W.P.(C)"),
        (r"\bW\.?\s*P\.?\s*\(\s*Crl\.?\s*\)", "W.P.(CRL)"),
        (r"\bW\.?\s*P\.?\s*\(\s*C\.?\s*\)", "W.P.(C)"),
        (r"Criminal\s+Appeal", "Criminal Appeal"),
        (r"Civil\s+Appeal", "Civil Appeal"),
        (r"Transfer\s+Petition", "Transfer Petition"),
        (r"Review\s+Petition", "Review"),
        (r"Curative\s+Petition", "Curative"),
        (r"Contempt", "Contempt"),
        (r"Public\s+Interest\s+Litigation|\bPIL\b", "PIL"),
    ]
    for pat, label in patterns:
        if re.search(pat, text, re.I):
            return label
    if CRIMINAL_HINT.search(text):
        return "CRIMINAL"
    if CIVIL_HINT.search(text):
        return "CIVIL"
    return "INSC"


def run_date_today() -> date:
    """Calendar 'today' for excluding future-dated rows (Asia/Kolkata)."""
    try:
        from zoneinfo import ZoneInfo

        return datetime.now(ZoneInfo("Asia/Kolkata")).date()
    except Exception:
        return datetime.now(timezone.utc).date()


def is_sc_final_disposal(disposal: str | None) -> bool:
    if disposal is None:
        return False
    key = re.sub(r"\s+", " ", str(disposal)).strip().casefold()
    if not key:
        return False
    return key in SC_FINAL_DISPOSALS


def map_branch(case_type: str, judicial_section: str | None = None) -> str:
    """Map case type → branch. Bare WP/W.P. → writ (civil/criminal side unknown)."""
    del judicial_section  # kept for call-site compatibility; not used for WP anymore
    key = case_type.upper().strip()
    if key in CASE_TYPE_BRANCH:
        return CASE_TYPE_BRANCH[key]
    key2 = re.sub(r"[.\s]+$", "", key)
    if key2 in CASE_TYPE_BRANCH:
        return CASE_TYPE_BRANCH[key2]
    for mapped, branch in sorted(CASE_TYPE_BRANCH.items(), key=lambda x: -len(x[0])):
        if key.startswith(mapped) or mapped.startswith(key):
            if len(mapped) >= 2 and len(key) >= 2:
                return branch
    if CRIMINAL_HINT.search(case_type):
        return "criminal"
    if CIVIL_HINT.search(case_type):
        return "civil"
    return "other"


def normalize_disposal(disposal: str | None) -> str:
    if disposal is None:
        return ""
    return re.sub(r"\s+", " ", str(disposal)).strip().upper()


def is_bombay_routine_excluded(norm: str) -> bool:
    """True for DISPOSED OFF-like / withdrawn / transfer / non-merits closures."""
    if not norm or norm in BOMBAY_OUTCOMES_EXCLUDED:
        return True
    if "DISPOSED OFF" in norm or "DISPOSED-OFF" in norm or norm == "DISPOSED OF":
        return True
    if "WITHDRAWN" in norm:
        return True
    if norm.startswith("TRANSFER") or " TRANSFER" in f" {norm}":
        return True
    if norm == "GRANT ISSUED":
        return True
    if "NON-PROSECUTION" in norm or "NON PROSECUTION" in norm:
        return True
    if "DEFAULT" in norm and "DISMISS" in norm:
        return True
    if "INFRUCTIO" in norm or "INFRUCTUO" in norm:  # INFRUCTIOUS / INFRUCTUOS
        return True
    if norm == "ABATED" or norm.endswith(" ABATED") or "ABATED" == norm:
        return True
    if "CONSENT TERM" in norm:
        return True
    return False


def is_bombay_kept_outcome(disposal: str | None) -> bool:
    norm = normalize_disposal(disposal)
    if is_bombay_routine_excluded(norm):
        return False
    return norm in BOMBAY_OUTCOMES_KEPT


def should_skip(title: str, case_type: str) -> bool:
    blob = f"{title} {case_type}"
    return bool(SKIP_RE.search(blob))


def make_entry(
    *,
    court: str,
    decided: date,
    title: str,
    case_type: str,
    branch: str,
    link: str,
) -> dict:
    return {
        "court": court,
        "decidedOn": decided.isoformat(),
        "title": title.strip(),
        "caseType": case_type,
        "branch": branch,
        "branchBasis": "case_type_mapping",
        "link": link,
        "linkKind": "archive",  # S3 OpenNyAI-style archive, not sci.gov.in / bombayhighcourt.nic.in
    }


def bombay_case_number(title: str, case_type: str, case_no: str | None) -> str:
    """Case identity without party names (title often embeds petitioner/respondent)."""
    m = re.match(r"^([A-Za-z().]+/\S+)\s+of\b", (title or "").strip(), re.I)
    if m:
        return m.group(1)
    if case_no:
        cn = str(case_no).strip()
        if case_type and case_type.upper() not in {"UNKNOWN", ""}:
            return f"{case_type}/{cn}"
        return cn
    return case_type or "UNKNOWN"


def make_bombay_entry(
    *,
    decided: date,
    case_type: str,
    case_number: str,
    bench: str,
    disposal_outcome: str,
    branch: str,
    link: str,
) -> dict:
    return {
        "court": "Bombay High Court",
        "decidedOn": decided.isoformat(),
        "caseType": case_type,
        "caseNumber": case_number,
        "bench": bench,
        "benchLabel": None,  # no place-name map in metadata; do not invent
        "disposalOutcome": disposal_outcome,
        "branch": branch,
        "branchBasis": "case_type_mapping",
        "link": link,
        "linkKind": "archive",
    }


def last_n_iso_weeks(today: date, n: int) -> list[tuple[int, int]]:
    """Newest-first list of (iso_year, iso_week) covering today and the prior n-1 weeks."""
    monday = date.fromordinal(today.toordinal() - (today.isoweekday() - 1))
    out: list[tuple[int, int]] = []
    seen: set[tuple[int, int]] = set()
    for i in range(n):
        d = date.fromordinal(monday.toordinal() - 7 * i)
        key = (d.isocalendar()[0], d.isocalendar()[1])
        if key not in seen:
            seen.add(key)
            out.append(key)
    return out


def month_histogram(rows: list[dict]) -> dict[str, int]:
    counts: Counter = Counter()
    for r in rows:
        counts[r["decidedOn"][:7]] += 1
    return dict(sorted(counts.items()))


def week_histogram(rows: list[dict]) -> dict[str, int]:
    counts: Counter = Counter()
    for r in rows:
        d = date.fromisoformat(r["decidedOn"])
        iso = d.isocalendar()
        counts[f"{iso.year}-W{iso.week:02d}"] += 1
    return dict(sorted(counts.items()))


def span_days(rows: list[dict]) -> int | None:
    if not rows:
        return None
    dates = [date.fromisoformat(r["decidedOn"]) for r in rows]
    return (max(dates) - min(dates)).days


def sc_pdf_link(year: int, path: str | None) -> str:
    if not path:
        return f"https://{SC_BUCKET}.s3.{REGION}.amazonaws.com/metadata/parquet/year={year}/metadata.parquet"
    # path is typically without extension; English PDF convention from archive layout
    path = path.lstrip("/")
    if not path.endswith(".pdf"):
        # common: ..._EN.pdf under english/
        base = path
        if not base.endswith("_EN"):
            # many paths already include language suffix in filename stem
            pass
        key = f"data/pdf/year={year}/english/{base}_EN.pdf"
        # if path already looks like a full relative pdf path
        if path.startswith("data/pdf/"):
            key = path
        elif path.endswith("_EN.pdf") or path.endswith(".pdf"):
            key = f"data/pdf/year={year}/english/{path}" if not path.startswith("data/") else path
        else:
            key = f"data/pdf/year={year}/english/{path}_EN.pdf"
    else:
        key = path if path.startswith("data/") else f"data/pdf/year={year}/english/{path}"
    return f"https://{SC_BUCKET}.s3.{REGION}.amazonaws.com/{key}"


def hc_pdf_link(year: int, court_part: str, bench: str, pdf_link: str | None, cnr: str | None, decision: date | None) -> str:
    base = f"https://{HC_BUCKET}.s3.{REGION}.amazonaws.com"
    if pdf_link:
        pl = str(pdf_link).lstrip("/")
        if pl.startswith("http"):
            return pl
        if pl.startswith("data/pdf/") or pl.startswith("court/"):
            # relative site path — still expose S3 if under data/pdf
            if pl.startswith("data/pdf/"):
                return f"{base}/{pl}"
            return f"{base}/data/pdf/year={year}/{court_part}/bench={bench}/{Path(pl).name}"
        # short filename
        return f"{base}/data/pdf/year={year}/{court_part}/bench={bench}/{pl}"
    # fallback: metadata key (no PDF name)
    return f"{base}/metadata/parquet/year={year}/{court_part}/bench={bench}/metadata-mobile.parquet"


def collect_supreme_court(
    s3, today: date, limit: int = PER_COURT_SC
) -> tuple[list[dict], dict]:
    records: list[dict] = []
    type_counts: Counter = Counter()
    branch_counts: Counter = Counter()
    disposal_counts: Counter = Counter()
    future_examples: list[dict] = []
    future_count = 0
    schema_reported = False

    for year in list_year_prefixes(s3, SC_BUCKET):
        key = f"metadata/parquet/year={year}/metadata.parquet"
        try:
            table = read_parquet_s3(s3, SC_BUCKET, key)
        except Exception as exc:
            print(f"[sc] skip {key}: {exc}", file=sys.stderr)
            continue
        if not schema_reported:
            print("[sc] schema:", table.column_names)
            schema_reported = True

        rows = table.to_pydict()
        n = table.num_rows
        batch: list[tuple[date, dict]] = []
        for i in range(n):
            title = rows.get("title", [None] * n)[i] or ""
            case_id = rows.get("case_id", [None] * n)[i]
            raw_html = rows.get("raw_html", [None] * n)[i] if "raw_html" in rows else None
            description = rows.get("description", [None] * n)[i] if "description" in rows else None
            disposal = rows.get("disposal_nature", [None] * n)[i] if "disposal_nature" in rows else None
            decided = parse_sc_date(rows.get("decision_date", [None] * n)[i])
            if decided is None:
                continue
            case_type = sc_case_type_from_row(title, case_id, raw_html, description)
            if decided > today:
                future_count += 1
                if len(future_examples) < 5:
                    future_examples.append(
                        {
                            "caseType": case_type,
                            "disposalNature": disposal or "",
                            "decisionDateRaw": str(rows.get("decision_date", [None] * n)[i]),
                            "decidedOn": decided.isoformat(),
                        }
                    )
                continue
            if should_skip(title, case_type) or should_skip(str(raw_html or ""), case_type):
                continue
            disposal_counts[str(disposal or "(empty)")] += 1
            if not is_sc_final_disposal(disposal):
                continue
            branch = map_branch(case_type)
            path = rows.get("path", [None] * n)[i]
            item = make_entry(
                court="Supreme Court of India",
                decided=decided,
                title=title,
                case_type=case_type,
                branch=branch,
                link=sc_pdf_link(year, path),
            )
            batch.append((decided, item))

        batch.sort(key=lambda x: x[0], reverse=True)
        for decided, item in batch:
            type_counts[item["caseType"]] += 1
            branch_counts[item["branch"]] += 1
            records.append(item)
            if len(records) >= limit:
                break
        print(f"[sc] year={year}: kept so far {len(records)}/{limit}")
        if len(records) >= limit:
            break

    records = records[:limit]
    records.sort(key=lambda r: r["decidedOn"], reverse=True)
    newest = date.fromisoformat(records[0]["decidedOn"]) if records else None
    oldest = date.fromisoformat(records[-1]["decidedOn"]) if records else None
    stats = {
        "newest": newest,
        "oldest": oldest,
        "type_counts": type_counts,
        "branch_counts": branch_counts,
        "disposal_counts": disposal_counts,
        "future_count": future_count,
        "future_examples": future_examples,
        "week_histogram": week_histogram(records),
        "span_days": span_days(records),
    }
    return records, stats


def collect_bombay_hc(s3, today: date) -> tuple[list[dict], dict]:
    """Final judgments only; exclude routine DISPOSED OFF-like outcomes;
    newest BOMBAY_PER_WEEK per ISO week over the last BOMBAY_WEEKS weeks.
    Entries omit party names.
    """
    week_keys = last_n_iso_weeks(today, BOMBAY_WEEKS)
    week_set = set(week_keys)
    # Years that can intersect the 26-week window (+1 earlier for ISO week spill)
    year_lo = min(y for y, _ in week_keys) - 1
    year_hi = max(y for y, _ in week_keys)

    candidates_by_week: dict[tuple[int, int], list[tuple[date, dict]]] = defaultdict(list)
    disposal_counts: Counter = Counter()  # all seen (pre-filter)
    kept_outcome_counts: Counter = Counter()
    excluded_outcome_counts: Counter = Counter()
    is_final_counts: Counter = Counter()
    future_examples: list[dict] = []
    future_count = 0
    schema_reported = False
    seen_cnr: set[str] = set()
    bench_codes: set[str] = set()
    wp_writ = 0

    for year in list_year_prefixes(s3, HC_BUCKET):
        if year < year_lo or year > year_hi:
            continue
        prefix = f"metadata/parquet/year={year}/{BOMBAY_COURT_PREFIX}/"
        keys = [
            k
            for k in list_keys(s3, HC_BUCKET, prefix)
            if k.endswith("metadata-mobile.parquet") or k.endswith("/metadata.parquet")
        ]
        mobile = [k for k in keys if k.endswith("metadata-mobile.parquet")]
        desktop = [k for k in keys if k.endswith("/metadata.parquet") and "mobile" not in k]
        ordered = mobile + desktop
        if not ordered:
            continue

        for key in ordered:
            m = re.search(r"bench=([^/]+)/", key)
            bench = m.group(1) if m else ""
            if bench in BOMBAY_SKIP_BENCHES:
                continue
            try:
                table = read_parquet_s3(s3, HC_BUCKET, key)
            except Exception as exc:
                print(f"[hc] skip {key}: {exc}", file=sys.stderr)
                continue
            if not schema_reported:
                print("[hc-bombay] schema:", table.column_names)
                schema_reported = True

            cols = set(table.column_names)
            rows = table.to_pydict()
            n = table.num_rows
            for i in range(n):
                title = (rows.get("title", [None] * n)[i] or "") if "title" in cols else ""
                court_name = (rows.get("court", [None] * n)[i] or "") if "court" in cols else ""
                if court_name and "bombay" not in court_name.lower():
                    continue
                decided = (
                    parse_hc_date(rows.get("decision_date", [None] * n)[i])
                    if "decision_date" in cols
                    else None
                )
                if decided is None:
                    continue
                iso_key = (decided.isocalendar()[0], decided.isocalendar()[1])
                if iso_key not in week_set:
                    continue

                if "case_type" in cols and rows["case_type"][i]:
                    case_type = normalize_case_type(rows["case_type"][i])
                else:
                    mtype = re.match(r"^([A-Za-z().]+)\s*/", title.strip())
                    case_type = normalize_case_type(mtype.group(1) if mtype else "UNKNOWN")

                disposal = (
                    rows.get("disposal_nature", [None] * n)[i] if "disposal_nature" in cols else None
                )
                is_final = rows.get("is_final", [None] * n)[i] if "is_final" in cols else None
                disposal_norm = normalize_disposal(disposal)

                if decided > today:
                    future_count += 1
                    if len(future_examples) < 5:
                        future_examples.append(
                            {
                                "caseType": case_type,
                                "disposalNature": disposal or "",
                                "is_final": is_final,
                                "decisionDateRaw": str(rows.get("decision_date", [None] * n)[i]),
                                "decidedOn": decided.isoformat(),
                            }
                        )
                    continue

                if should_skip(title, case_type):
                    continue
                cnr = rows.get("cnr", [None] * n)[i] if "cnr" in cols else None
                if cnr and cnr in seen_cnr:
                    continue

                disposal_counts[disposal_norm or "(empty)"] += 1
                is_final_counts[str(is_final)] += 1

                # Prefer is_final when the column exists (mobile parquet).
                if "is_final" in cols:
                    if is_final is not True:
                        continue
                else:
                    # Desktop parquet without is_final: require kept outcome only.
                    pass

                if not is_bombay_kept_outcome(disposal):
                    excluded_outcome_counts[disposal_norm or "(empty)"] += 1
                    continue
                kept_outcome_counts[disposal_norm] += 1

                case_no = rows.get("case_no", [None] * n)[i] if "case_no" in cols else None
                case_number = bombay_case_number(title, case_type, case_no)
                branch = map_branch(case_type)
                if case_type.upper() in {"WP", "W.P.", "WRIT PETITION"}:
                    branch = "writ"
                    wp_writ += 1

                pdf_link = rows.get("pdf_link", [None] * n)[i] if "pdf_link" in cols else None
                item = make_bombay_entry(
                    decided=decided,
                    case_type=case_type,
                    case_number=case_number,
                    bench=bench,
                    disposal_outcome=disposal_norm,
                    branch=branch,
                    link=hc_pdf_link(
                        year, BOMBAY_COURT_PREFIX, bench, pdf_link, cnr, decided
                    ),
                )
                candidates_by_week[iso_key].append((decided, item))
                if cnr:
                    seen_cnr.add(cnr)
                if bench:
                    bench_codes.add(bench)

        print(
            f"[hc] year={year}: weeks_filled="
            f"{sum(1 for w in week_set if candidates_by_week[w])}/"
            f"{len(week_set)} candidates="
            f"{sum(len(v) for v in candidates_by_week.values())}"
        )

    # Cap at newest BOMBAY_PER_WEEK per ISO week
    kept: list[dict] = []
    per_week_kept: dict[str, int] = {}
    for y, w in week_keys:
        batch = candidates_by_week.get((y, w), [])
        batch.sort(key=lambda x: x[0], reverse=True)
        # Dedup by link within week
        seen_link: set[str] = set()
        week_rows: list[dict] = []
        for decided, item in batch:
            if item["link"] in seen_link:
                continue
            seen_link.add(item["link"])
            week_rows.append(item)
            if len(week_rows) >= BOMBAY_PER_WEEK:
                break
        label = f"{y}-W{w:02d}"
        per_week_kept[label] = len(week_rows)
        kept.extend(week_rows)

    kept.sort(key=lambda r: r["decidedOn"], reverse=True)
    # Recompute branch / type on kept set
    type_counts: Counter = Counter(r["caseType"] for r in kept)
    branch_counts: Counter = Counter(r["branch"] for r in kept)
    wp_writ_kept = sum(1 for r in kept if r["branch"] == "writ")
    benches_kept = sorted({r["bench"] for r in kept if r.get("bench")})

    # Metadata does not map path codes → place names; expose codes only.
    benches_report = [{"code": code} for code in benches_kept]

    outcomes_excluded_list = sorted(BOMBAY_OUTCOMES_EXCLUDED - {""})
    outcomes_kept_list = sorted(BOMBAY_OUTCOMES_KEPT)

    stats = {
        "newest": date.fromisoformat(kept[0]["decidedOn"]) if kept else None,
        "oldest": date.fromisoformat(kept[-1]["decidedOn"]) if kept else None,
        "type_counts": type_counts,
        "branch_counts": branch_counts,
        "disposal_counts": disposal_counts,
        "kept_outcome_counts": kept_outcome_counts,
        "excluded_outcome_counts": excluded_outcome_counts,
        "is_final_counts": is_final_counts,
        "future_count": future_count,
        "future_examples": future_examples,
        "week_histogram": week_histogram(kept),
        "month_histogram": month_histogram(kept),
        "per_week_kept": per_week_kept,
        "span_days": span_days(kept),
        "wp_writ": wp_writ_kept,
        "kept": len(kept),
        "benches": benches_report,
        "sample_rule": {
            "perWeek": BOMBAY_PER_WEEK,
            "weeks": BOMBAY_WEEKS,
            "outcomesKept": outcomes_kept_list,
            "outcomesExcluded": outcomes_excluded_list,
        },
    }
    return kept, stats


def load_existing_supreme_court() -> tuple[list[dict], dict] | None:
    """Reuse the on-disk Supreme Court slice so a Bombay rebuild does not alter it."""
    if not OUT_PATH.is_file():
        return None
    try:
        data = json.loads(OUT_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None
    sc_rows = [
        r for r in (data.get("rulings") or []) if r.get("court") == "Supreme Court of India"
    ]
    if not sc_rows:
        return None
    court_meta = (data.get("courts") or {}).get("Supreme Court of India") or {}
    branch_counts = Counter(
        (data.get("branchCounts") or {}).get("supremeCourt")
        or Counter(r.get("branch", "other") for r in sc_rows)
    )
    type_counts = Counter(r.get("caseType", "UNKNOWN") for r in sc_rows)
    newest = date.fromisoformat(sc_rows[0]["decidedOn"]) if sc_rows else None
    oldest = date.fromisoformat(sc_rows[-1]["decidedOn"]) if sc_rows else None
    # Prefer stored newest/oldest if present
    if court_meta.get("newestRecordDate"):
        newest = date.fromisoformat(court_meta["newestRecordDate"])
    if court_meta.get("oldestRecordDate"):
        oldest = date.fromisoformat(court_meta["oldestRecordDate"])
    disposal_counts = Counter(
        (data.get("disposalNatureCounts") or {}).get("supremeCourt") or {}
    )
    stats = {
        "newest": newest,
        "oldest": oldest,
        "type_counts": type_counts,
        "branch_counts": branch_counts,
        "disposal_counts": disposal_counts,
        "future_count": court_meta.get("excludedFutureDated", 0),
        "future_examples": (data.get("futureDatedExcluded") or {}).get("supremeCourt") or [],
        "week_histogram": court_meta.get("weekHistogram") or week_histogram(sc_rows),
        "span_days": court_meta.get("spanDays", span_days(sc_rows)),
        "court_meta": court_meta,
    }
    return sc_rows, stats


def main() -> None:
    s3 = s3_client()
    today = run_date_today()
    generated_on = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"Run date (Asia/Kolkata calendar): {today.isoformat()}")

    existing_sc = load_existing_supreme_court()
    if existing_sc:
        print("Reusing existing Supreme Court slice from", OUT_PATH)
        sc_rows, sc_stats = existing_sc
    else:
        print("Collecting Supreme Court…")
        sc_rows, sc_stats = collect_supreme_court(s3, today)

    print("Collecting Bombay High Court…")
    hc_rows, hc_stats = collect_bombay_hc(s3, today)

    all_types = Counter()
    all_types.update(sc_stats["type_counts"])
    all_types.update(hc_stats["type_counts"])
    mapping_report = []
    for ct, n in sorted(all_types.items(), key=lambda x: (-x[1], x[0])):
        mapping_report.append({"caseType": ct, "branch": map_branch(ct), "count": n})

    sc_court_block = {
        "groupLabel": "Recent judgments",
        "newestRecordDate": sc_stats["newest"].isoformat() if sc_stats["newest"] else None,
        "oldestRecordDate": sc_stats["oldest"].isoformat() if sc_stats["oldest"] else None,
        "count": len(sc_rows),
        "spanDays": sc_stats["span_days"],
        "weekHistogram": sc_stats["week_histogram"],
        "excludedFutureDated": sc_stats["future_count"],
    }
    if existing_sc and sc_stats.get("court_meta"):
        # Preserve any extra SC keys from the prior index, then force current labels/stats.
        merged = dict(sc_stats["court_meta"])
        merged.update(sc_court_block)
        sc_court_block = merged

    payload = {
        "generatedOn": generated_on,
        "runDate": today.isoformat(),
        "courts": {
            "Supreme Court of India": sc_court_block,
            "Bombay High Court": {
                "groupLabel": "Recent final orders and judgments (sample)",
                "newestRecordDate": hc_stats["newest"].isoformat() if hc_stats["newest"] else None,
                "oldestRecordDate": hc_stats["oldest"].isoformat() if hc_stats["oldest"] else None,
                "count": len(hc_rows),
                "spanDays": hc_stats["span_days"],
                "weekHistogram": hc_stats["week_histogram"],
                "monthHistogram": hc_stats["month_histogram"],
                "perWeekKept": hc_stats["per_week_kept"],
                "excludedFutureDated": hc_stats["future_count"],
                "benches": hc_stats["benches"],
                "sampleRule": hc_stats["sample_rule"],
            },
        },
        "branchCounts": {
            "supremeCourt": dict(sc_stats["branch_counts"]),
            "bombayHighCourt": dict(hc_stats["branch_counts"]),
            "combined": dict(
                Counter(sc_stats["branch_counts"]) + Counter(hc_stats["branch_counts"])
            ),
        },
        "disposalNatureCounts": {
            "supremeCourt": dict(Counter(sc_stats["disposal_counts"]).most_common(20)),
            "bombayHighCourt": dict(hc_stats["disposal_counts"].most_common(40)),
            "bombayKeptOutcomes": dict(hc_stats["kept_outcome_counts"].most_common(40)),
            "bombayExcludedOutcomes": dict(hc_stats["excluded_outcome_counts"].most_common(40)),
            "bombayIsFinal": dict(hc_stats["is_final_counts"]),
        },
        "caseTypeMapping": mapping_report,
        "wpBranchSplit": {
            "bombayWpWrit": hc_stats["wp_writ"],
        },
        "linkKindNote": (
            "All links use linkKind=archive pointing at the OpenNyAI-style S3 "
            "buckets (indian-*-judgments.s3.ap-south-1.amazonaws.com), not "
            "sci.gov.in or bombayhighcourt.nic.in. Bombay entries omit party "
            "names; identity is caseType/caseNumber/bench/disposalOutcome."
        ),
        "futureDatedExcluded": {
            "supremeCourt": sc_stats["future_examples"],
            "bombayHighCourt": hc_stats["future_examples"],
        },
        "rulings": sc_rows + hc_rows,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    try:
        from app.main import _load_rulings_index

        _load_rulings_index.cache_clear()
    except Exception:
        pass
    size = OUT_PATH.stat().st_size
    print("Wrote", OUT_PATH, f"({size} bytes)")
    print(
        "SC:",
        f"n={len(sc_rows)} newest={sc_stats['newest']} oldest={sc_stats['oldest']} "
        f"span={sc_stats['span_days']}d future_excluded={sc_stats['future_count']}",
    )
    print(
        "HC:",
        f"n={len(hc_rows)} newest={hc_stats['newest']} oldest={hc_stats['oldest']} "
        f"span={hc_stats['span_days']}d future_excluded={hc_stats['future_count']}",
    )
    print("HC month counts:", hc_stats["month_histogram"])
    print("HC per-week kept:", hc_stats["per_week_kept"])
    print("SC branches:", dict(sc_stats["branch_counts"]))
    print("HC branches:", dict(hc_stats["branch_counts"]))
    print("Bombay WP → writ:", hc_stats["wp_writ"])
    print("Bombay benches:", hc_stats["benches"])
    print("Outcomes kept:", hc_stats["sample_rule"]["outcomesKept"])
    print("Outcomes excluded:", hc_stats["sample_rule"]["outcomesExcluded"])
    print("Future SC examples:", sc_stats["future_examples"])
    print("Future HC examples:", hc_stats["future_examples"])
    print("Case types mapped:")
    for row in mapping_report:
        print(f"  {row['caseType']!r:40} -> {row['branch']:8} ({row['count']})")


if __name__ == "__main__":
    main()
