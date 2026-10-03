import json
from huggingface_hub import hf_hub_download

for fname in ["graph/deterministic_edges.json", "graph/all_edges.json"]:
    path = hf_hub_download("aashnasharma/govintel-legal-dataset", fname, repo_type="dataset")
    with open(path) as f:
        data = json.load(f)

    # Handle both {edges: [...]} and bare [...] shapes
    edges = data["edges"] if isinstance(data, dict) and "edges" in data else data

    ipc_bns_edges = [
        e for e in edges
        if "TEMPORAL" in str(e.get("edge_type", "")).upper()
        or ("IPC" in str(e.get("source", "")).upper() and "BNS" in str(e.get("target", "")).upper())
    ]

    print(f"\n=== {fname}: {len(ipc_bns_edges)} IPC-temporal-style edges found ===")
    for e in ipc_bns_edges[:5]:
        print(json.dumps(e, indent=2))

# Also check: do these edges carry any descriptive text themselves, or ONLY
# node IDs? Cross-check by pulling the actual section text for one example
# pair from the sections/ files, to see whether reconstructing something
# equivalent to a full mapping table requires joining multiple files.
ipc_sections_path = hf_hub_download("aashnasharma/govintel-legal-dataset", "sections/ipc_sections.json", repo_type="dataset")
bns_sections_path = hf_hub_download("aashnasharma/govintel-legal-dataset", "sections/bns_sections.json", repo_type="dataset")

with open(ipc_sections_path) as f:
    ipc_sections = json.load(f)
with open(bns_sections_path) as f:
    bns_sections = json.load(f)

print(f"\nipc_sections.json type: {type(ipc_sections)}, sample entry:")
sample_ipc = ipc_sections[0] if isinstance(ipc_sections, list) else list(ipc_sections.items())[0]
print(json.dumps(sample_ipc, indent=2, default=str)[:500])

print(f"\nbns_sections.json type: {type(bns_sections)}, sample entry:")
sample_bns = bns_sections[0] if isinstance(bns_sections, list) else list(bns_sections.items())[0]
print(json.dumps(sample_bns, indent=2, default=str)[:500])
