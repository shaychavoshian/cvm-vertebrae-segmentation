"""
Make LabelMe JSON files safe to publish: remove the embedded X-ray.

For every .json in <input_folder>, writes a cleaned copy to <output_folder>:
  - "imageData" -> null       (removes the embedded radiograph)
  - "imagePath" -> file name only, no local folders
Polygons, labels and image size are kept unchanged.
Original files are never modified.

Usage:
  python clean_labelme_json.py <input_folder> <output_folder>
"""
import json
import sys
from pathlib import Path, PureWindowsPath


def main(src, dst):
    src, dst = Path(src), Path(dst)
    dst.mkdir(parents=True, exist_ok=True)
    files = sorted(src.glob("*.json"))
    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        had_image = bool(d.get("imageData"))
        d["imageData"] = None
        if d.get("imagePath"):
            d["imagePath"] = PureWindowsPath(d["imagePath"]).name  # handles C:\... and /...
        labels = sorted(s["label"] for s in d.get("shapes", []))
        (dst / f.name).write_text(json.dumps(d, indent=2), encoding="utf-8")
        print(f"{f.name}: image removed={had_image}, labels={labels}")

    # Final check: nothing published may still carry image data
    bad = [p.name for p in dst.glob("*.json")
           if json.loads(p.read_text(encoding="utf-8")).get("imageData")]
    if bad:
        sys.exit(f"ERROR: still contains imageData: {bad}")
    print(f"Done: {len(files)} files cleaned -> {dst} (no image data left)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
