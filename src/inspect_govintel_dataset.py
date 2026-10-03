from huggingface_hub import list_repo_files, hf_hub_download
import json

files = list_repo_files("aashnasharma/govintel-legal-dataset", repo_type="dataset")
print("All files in the repo:")
for f in files:
    print(" -", f)

# Download and inspect any file that looks like it could be the knowledge
# graph (not the main training-pairs parquet), e.g. containing "graph",
# "edge", "node", or "mapping" in the filename
for f in files:
    if any(kw in f.lower() for kw in ["graph", "edge", "node", "mapping"]):
        print(f"\nInspecting candidate graph file: {f}")
        local_path = hf_hub_download("aashnasharma/govintel-legal-dataset", f, repo_type="dataset")
        with open(local_path) as file:
            content = file.read(2000)  # first 2000 chars only
        print(content)
