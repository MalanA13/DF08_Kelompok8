from PIL import Image
from pathlib import Path

roots = [("clean", Path("01_COVER")), ("stego", Path("03_STEGO"))]
out = Path("04_TRANSFORMED")

for truth, root in roots:
    for p in sorted(root.iterdir()):
        if not p.is_file() or p.suffix.lower() not in ('.png', '.bmp'):
            continue
        with Image.open(p).convert("RGB") as im:
            for mode in ["resave", "resize", "convert", "jpeg"]:
                d = out / truth / mode
                d.mkdir(parents=True, exist_ok=True)
                if mode == "resave":
                    q = d / p.name
                    im.save(q, format="PNG" if p.suffix.lower() == ".png" else "BMP")
                elif mode == "resize":
                    q = d / p.name
                    im.resize((128, 128)).save(
                        q, format="PNG" if p.suffix.lower() == ".png" else "BMP"
                    )
                elif mode == "convert":
                    ext = ".bmp" if p.suffix.lower() == ".png" else ".png"
                    q = d / (p.stem + ext)
                    im.save(q)
                else:
                    q = d / (p.stem + ".jpg")
                    im.save(q, format="JPEG", quality=70)

print("transforms complete")
