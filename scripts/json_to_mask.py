"""
Convert LabelMe polygon files (C2, C3, C4) into label masks.

Output: one PNG per JSON, same size as the radiograph, pixel values
  0 = background, 1 = C2, 2 = C3, 3 = C4
(saved as a palette PNG so it also displays in colour).

Usage:
  python scripts/json_to_mask.py annotations/labelme my_masks
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

CLASS_IDS = {"C2": 1, "C3": 2, "C4": 3}
PALETTE = [0, 0, 0, 128, 0, 0, 0, 128, 0, 128, 128, 0]


def json_to_mask(path):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    mask = Image.new("L", (d["imageWidth"], d["imageHeight"]), 0)
    draw = ImageDraw.Draw(mask)
    for shape in d["shapes"]:
        label = shape["label"].strip().upper()
        if label not in CLASS_IDS:
            print(f"  skipping unknown label '{shape['label']}' in {Path(path).name}")
            continue
        draw.polygon([tuple(p) for p in shape["points"]], fill=CLASS_IDS[label])
    return np.array(mask)


def main(src, dst):
    src, dst = Path(src), Path(dst)
    dst.mkdir(parents=True, exist_ok=True)
    files = sorted(src.glob("*.json"))
    for f in files:
        m = Image.fromarray(json_to_mask(f), mode="P")
        m.putpalette(PALETTE + [0] * (768 - len(PALETTE)))
        m.save(dst / f"{f.stem}.png")
    print(f"Done: {len(files)} masks -> {dst}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
