from PIL import Image
from pathlib import Path
import argparse
import csv
import hashlib
import random
import string
import numpy as np

def bits_from_bytes(data):
    for value in data:
        for shift in range(7, -1, -1):
            yield (value >> shift) & 1

def bytes_from_bits(bits):
    output = bytearray()
    for start in range(0, len(bits) - 7, 8):
        value = 0
        for bit in bits[start:start + 8]:
            value = (value << 1) | bit
        output.append(value)
    return bytes(output)

def embed(input_path, output_path, payload):
    image = Image.open(input_path).convert("RGB")
    array = np.array(image)
    flat = array.reshape(-1)
    data = len(payload).to_bytes(4, "big") + payload
    bits = list(bits_from_bytes(data))
    if len(bits) > len(flat):
        raise ValueError("payload too large")
    flat[:len(bits)] = (flat[:len(bits)] & 0xFE) | np.array(bits, dtype=np.uint8)
    Image.fromarray(flat.reshape(array.shape), "RGB").save(output_path)

def extract(input_path):
    array = np.array(Image.open(input_path).convert("RGB")).reshape(-1)
    bits = (array & 1).tolist()
    length = int.from_bytes(bytes_from_bits(bits[:32]), "big")
    if length > 10_000_000 or 32 + length * 8 > len(bits):
        return None
    return bytes_from_bits(bits[32:32 + length * 8])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["make", "extract"])
    parser.add_argument("--file")
    args = parser.parse_args()

    if args.mode == "extract":
        payload = extract(args.file)
        print("NO_VALID_PAYLOAD" if payload is None else payload.decode("utf-8", "replace"))
    else:
        covers = sorted(p for p in Path("01_COVER").iterdir()
                         if p.suffix.lower() in (".png", ".bmp"))
        Path("03_STEGO").mkdir(exist_ok=True)
        rows = []
        ratios = [("low", 0.01), ("medium", 0.05), ("high", 0.15)]

        for cover in covers:
            capacity = 256 * 256 * 3 // 8 - 4
            for label, ratio in ratios:
                length = max(32, int(capacity * ratio))
                marker = f"DF08_PAYLOAD_{cover.stem}_{label}_"
                seed = int(hashlib.sha256((cover.name + label).encode()).hexdigest()[:8], 16)
                rng = random.Random(seed)
                rest = "".join(
                    rng.choice(string.ascii_uppercase)
                    for _ in range(length - len(marker))
                )
                payload = (marker + rest).encode()
                output = Path("03_STEGO") / f"{cover.stem}_{label}{cover.suffix}"
                embed(cover, output, payload)
                rows.append([
                    cover.name, output.name, label, ratio, len(payload),
                    hashlib.sha256(payload).hexdigest(), marker,
                ])

        with open("02_GROUND_TRUTH/payload_manifest.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                "cover_file", "stego_file", "level", "ratio",
                "payload_length", "payload_sha256", "marker",
            ])
            writer.writerows(rows)

        print("stego images:", len(rows))
