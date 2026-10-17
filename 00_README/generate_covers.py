from PIL import Image
from pathlib import Path
import csv
import hashlib
import numpy as np

out = Path("01_COVER")
gt = Path("02_GROUND_TRUTH")
out.mkdir(exist_ok=True)
gt.mkdir(exist_ok=True)

rows = []

for fmt, ext, base in [("PNG", "png", 0), ("BMP", "bmp", 100)]:
    for i in range(1, 21):
        rng = np.random.default_rng(8000 + base + i)
        arr = rng.integers(0, 256, size=(256, 256, 3), dtype=np.uint8)
        path = out / f"{fmt}_{i:02d}.{ext}"
        Image.fromarray(arr, "RGB").save(path, format=fmt)
        rows.append([
            path.name, fmt,
            hashlib.sha256(path.read_bytes()).hexdigest(),
            path.stat().st_size,
        ])

with open(gt / "cover_manifest.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["filename", "format", "sha256", "size_bytes"])
    writer.writerows(rows)

print("40 covers created")
