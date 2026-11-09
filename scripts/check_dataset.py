"""
Sanity checks before publishing / after downloading.

  - every LabelMe JSON has no embedded image (imageData is null)
  - every JSON has exactly one C2, one C3 and one C4 polygon
  - every mask contains classes 1, 2 and 3 and nothing else
  - JSON-derived masks match the PNG masks (when both exist)

Usage:
  python scripts/check_dataset.py
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from json_to_mask import json_to_mask  # noqa: E402

ROOT = Path(__file__).resolve().parents[1] / "annotations"
problems = []

jsons = sorted((ROOT / "labelme").glob("*.json"))
for f in jsons:
    d = json.loads(f.read_text(encoding="utf-8"))
    if d.get("imageData"):
        problems.append(f"{f.name}: contains embedded image data")
    labels = sorted(s["label"].strip().upper() for s in d["shapes"])
    if labels != ["C2", "C3", "C4"]:
        problems.append(f"{f.name}: labels are {labels}, expected C2, C3, C4")

masks = sorted((ROOT / "masks").glob("*.png"))
for f in masks:
    m = np.asarray(Image.open(f))
    vals = set(np.unique(m).tolist())
    if vals != {0, 1, 2, 3}:
        problems.append(f"{f.name}: mask values {sorted(vals)}, expected 0-3")
    j = ROOT / "labelme" / f"{f.stem}.json"
    if j.exists():
        agree = (json_to_mask(j) == m).mean()
        if agree < 0.999:
            problems.append(f"{f.name}: only {agree:.2%} agreement with its JSON")

print(f"Checked {len(jsons)} JSON files and {len(masks)} masks.")
if problems:
    print("PROBLEMS:")
    print("\n".join("  " + p for p in problems))
    sys.exit(1)
print("All checks passed.")
