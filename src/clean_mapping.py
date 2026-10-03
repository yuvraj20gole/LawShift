import pandas as pd
import re
import json

df = pd.read_json("data/raw/mapping_parsed.jsonl", lines=True)

# 1. Drop the junk row where ipc_section is not a real identifier
junk_mask = df["ipc_section"].astype(str).str.strip().str.lower() == "repealed"
junk_rows = df[junk_mask].to_dict("records")
df = df[~junk_mask].copy()

def parse_bns_section(raw):
    if raw is None:
        return {"mapping_type": None, "bns_base_section": None, "bns_subclauses": [], "bns_note": None, "raw": raw}

    raw = str(raw).strip()

    if re.search(r"repeal", raw, re.IGNORECASE):
        return {"mapping_type": "dropped", "bns_base_section": None, "bns_subclauses": [], "bns_note": None, "raw": raw}

    base_match = re.match(r"^(\d+[A-Za-z]{0,3})", raw)
    base = base_match.group(1) if base_match else None

    subclauses = re.findall(r"\(([^)]*)\)", raw)
    flat_subclauses = []
    for group in subclauses:
        parts = [p.strip() for p in group.split(",") if p.strip()]
        flat_subclauses.extend(parts)

    remainder = raw
    if base_match:
        remainder = remainder[base_match.end():]
    remainder = re.sub(r"\([^)]*\)", "", remainder)
    remainder = re.sub(r"[&,]", "", remainder).strip()
    note = remainder if remainder else None

    mapping_type = "partial" if (flat_subclauses or note) else "section"

    return {
        "mapping_type": mapping_type,
        "bns_base_section": base,
        "bns_subclauses": flat_subclauses,
        "bns_note": note,
        "raw": raw,
    }

parsed = df["bns_section"].apply(parse_bns_section)
parsed_df = pd.DataFrame(list(parsed))
df = pd.concat([df.reset_index(drop=True), parsed_df.reset_index(drop=True)], axis=1)

# Merge detection: multiple different IPC sections pointing at the exact same raw bns_section string
merge_groups = df[df["mapping_type"] != "dropped"].groupby("raw")["ipc_section"].apply(list)
merge_groups = merge_groups[merge_groups.apply(len) > 1]
merged_bns_values = set(merge_groups.index)
df["is_merged"] = df["raw"].isin(merged_bns_values)
df.loc[df["is_merged"], "mapping_type"] = "merged"

df.to_json("data/clean/mapping.jsonl", orient="records", lines=True)

report = {
    "total_rows_raw": len(df) + len(junk_rows),
    "junk_rows_dropped": len(junk_rows),
    "junk_row_examples": junk_rows,
    "final_rows": len(df),
    "mapping_type_counts": df["mapping_type"].value_counts().to_dict(),
    "merged_groups": {k: v for k, v in merge_groups.items()},
    "n_merged_groups": len(merge_groups),
}
with open("results/mapping_cleaning_report.json", "w") as f:
    json.dump(report, f, indent=2, default=str)

print(json.dumps(report, indent=2, default=str))
print("\nSample cleaned rows:")
print(df[["ipc_section", "raw", "mapping_type", "bns_base_section", "bns_subclauses", "bns_note", "is_merged"]].sample(10).to_string())
