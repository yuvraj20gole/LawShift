import pandas as pd
import ast
import json

raw = pd.read_json("data/raw/mapping.jsonl", lines=True)

parsed_rows = []
parse_failures = []

for idx, row in raw.iterrows():
    try:
        d = ast.literal_eval(row["response"])
        parsed_rows.append({
            "ipc_section": d.get("IPC Section"),
            "ipc_heading": d.get("IPC Heading"),
            "ipc_description": d.get("IPC Descriptions"),
            "bns_section": d.get("BNS Section"),
            "bns_heading": d.get("BNS Heading"),
            "bns_description": d.get("BNS description"),
            "prompt": row["prompts"],
        })
    except Exception as e:
        parse_failures.append({"row_index": idx, "error": str(e), "raw_response": row["response"][:200]})

df = pd.DataFrame(parsed_rows)
df.to_json("data/raw/mapping_parsed.jsonl", orient="records", lines=True)

print(f"Total rows: {len(raw)}")
print(f"Successfully parsed: {len(df)}")
print(f"Parse failures: {len(parse_failures)}")
if parse_failures:
    print("First few failures:")
    for f in parse_failures[:5]:
        print(f)

print("\n--- BNS Section value patterns ---")
print(f"Unique bns_section values (sample of 20): {df['bns_section'].dropna().unique()[:20].tolist()}")

# Flag non-standard values specifically
repealed = df[df["bns_section"].astype(str).str.contains("repeal", case=False, na=False)]
print(f"\nRows where bns_section mentions 'repeal': {len(repealed)}")
if len(repealed) > 0:
    print(repealed[["ipc_section", "bns_section"]].to_string())

sub_section = df[df["bns_section"].astype(str).str.contains(r"\(", na=False)]
print(f"\nRows where bns_section has a sub-reference like '1(3)': {len(sub_section)}")

null_bns = df["bns_section"].isna().sum()
print(f"\nRows with null bns_section: {null_bns}")

# Check for duplicate ipc_section values (does one IPC section appear more than once?)
dupes = df[df.duplicated(subset=["ipc_section"], keep=False)].sort_values("ipc_section")
print(f"\nIPC sections appearing more than once: {df['ipc_section'].duplicated().sum()}")
if len(dupes) > 0:
    print(dupes[["ipc_section", "bns_section"]].head(20).to_string())
