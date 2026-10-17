from pathlib import Path
import csv

root     = Path(".")
analysis = root / "08_ANALYSIS"
analysis.mkdir(exist_ok=True)

def read_csv(path):
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))

payload_rows = read_csv(root / "02_GROUND_TRUTH/payload_manifest.csv")
zsteg_rows   = read_csv(root / "07_RAW_RESULTS/zsteg_detection.csv")
simple_rows  = read_csv(root / "07_RAW_RESULTS/simple_extractor_detection.csv")

payload_by_stego = {row["stego_file"]: row for row in payload_rows}
all_filenames    = sorted({row["filename"] for row in zsteg_rows})
case_by_filename = {
    fname: f"DF08-STEG-{idx:03d}-R1"
    for idx, fname in enumerate(all_filenames, start=1)
}

rows = []
for tool, detections in [("zsteg", zsteg_rows), ("simple_extractor", simple_rows)]:
    for det in detections:
        filename = det["filename"]
        truth    = det["truth"]
        payload  = payload_by_stego.get(filename)

        is_stego = int(truth == "stego")
        detected = int(det.get("marker_found", det.get("detected_marker", 0)))
        payload_extracted = det.get("valid_payload", det.get("payload_extracted", ""))

        level     = payload["level"] if payload else "none"
        ratio     = payload["ratio"] if payload else "none"
        file_type = Path(filename).suffix.lstrip(".").upper()

        tp = int(is_stego == 1 and detected == 1)
        fp = int(is_stego == 0 and detected == 1)
        tn = int(is_stego == 0 and detected == 0)
        fn = int(is_stego == 1 and detected == 0)

        rows.append({
            "case_id": case_by_filename[filename],
            "source_id": filename,
            "file_type": file_type,
            "is_stego": is_stego,
            "payload_ratio": level,
            "payload_fraction": ratio,
            "transform": "none",
            "tool": tool,
            "detected": detected,
            "payload_extracted": payload_extracted,
            "payload_hash_match": "",
            "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "runtime_sec": det.get("runtime_sec", ""),
            "notes": det.get("status", "ok"),
        })

fields = [
    "case_id", "source_id", "file_type", "is_stego",
    "payload_ratio", "payload_fraction", "transform", "tool",
    "detected", "payload_extracted", "payload_hash_match",
    "tp", "fp", "tn", "fn", "runtime_sec", "notes",
]
output = analysis / "detection_results.csv"
with output.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print(f"wrote {len(rows)} rows: {output}")
