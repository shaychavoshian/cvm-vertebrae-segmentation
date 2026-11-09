"""
Overlay the C2/C3/C4 masks on your own copy of the Aariz radiographs.

The radiographs are NOT included in this repository: download them from the
official Aariz release first. Images and masks are matched by file name
(e.g. cl76jfqye0e5h076122wx6tkd.bmp  <->  cl76jfqye0e5h076122wx6tkd.png).

Usage:
  python scripts/visualize.py <aariz_image_folder> annotations/masks overlays
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

COLOURS = {1: (128, 0, 0), 2: (0, 128, 0), 3: (128, 128, 0)}  # C2, C3, C4
ALPHA = 0.5
IMAGE_EXTS = {".bmp", ".png", ".jpg", ".jpeg", ".tif", ".tiff"}


def main(img_dir, mask_dir, out_dir):
    img_dir, mask_dir, out_dir = Path(img_dir), Path(mask_dir), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    images = {p.stem: p for p in img_dir.rglob("*") if p.suffix.lower() in IMAGE_EXTS}
    done = missing = 0
    for m_path in sorted(mask_dir.glob("*.png")):
        img_path = images.get(m_path.stem)
        if img_path is None:
            missing += 1
            continue
        img = np.asarray(Image.open(img_path).convert("RGB")).astype(float)
        mask = np.asarray(Image.open(m_path))
        if mask.shape != img.shape[:2]:
            print(f"size mismatch, skipped: {m_path.name}")
            continue
        for k, c in COLOURS.items():
            sel = mask == k
            img[sel] = (1 - ALPHA) * img[sel] + ALPHA * np.array(c)
        Image.fromarray(img.astype(np.uint8)).save(out_dir / m_path.name)
        done += 1
    print(f"Done: {done} overlays -> {out_dir}; {missing} masks had no matching image")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
