from datasets import load_dataset
import os

os.makedirs("data/raw", exist_ok=True)

# 1. Statutory text corpus — retrieval target for Stage 3
statutes = load_dataset("GSMS-B/indian-legal-sections-bns-bnss-bsa-2023", split="train")
statutes.to_pandas().to_json("data/raw/statutes.jsonl", orient="records", lines=True)
print(f"Statutes: {len(statutes)} rows")
print("Columns:", statutes.column_names)

# 2. QA corpus — doubles as retrieval ground truth (each question has a known section)
qa = load_dataset("GSMS-B/Indian-Legal-QA-BNS-BNSS-BSA",
                   data_files="bns_bnss_bsa_combined_legal_qa.jsonl", split="train")
qa.to_pandas().to_json("data/raw/qa.jsonl", orient="records", lines=True)
print(f"QA pairs: {len(qa)} rows")
print("Columns:", qa.column_names)

# 3. IPC-BNS mapping table
mapping = load_dataset("nandhakumarg/IPC_and_BNS_transformation", split="train")
mapping.to_pandas().to_json("data/raw/mapping.jsonl", orient="records", lines=True)
print(f"Mapping rows: {len(mapping)}")
print("Columns:", mapping.column_names)

# 4. ILDC — only needed later for stress-testing on real case text; large,
#    so leave commented out for now
# ildc = load_dataset("Exploration-Lab/ILDC", split="train")
# ildc.to_pandas().to_json("data/raw/ildc.jsonl", orient="records", lines=True)
