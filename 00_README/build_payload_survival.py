from pathlib import Path
import csv

manifest_path  = Path("02_GROUND_TRUTH/payload_manifest.csv")
detection_path = Path("07_RAW_RESULTS/transformed_detection.csv")
output_path    = Path("08_ANALYSIS/payload_survival.csv")

expected_hash = {}
with manifest_path.open(newline="", encoding="utf-8") as file:
    for row in csv.DictReader(file):
        stem = Path(row["stego_file"]).stem
        expected_hash[stem] = row["payload_sha256"]

rows = []
with detection_path.open(newline="", encoding="utf-8") as file:
    for row in csv.DictReader(file):
        if row["truth"] != "stego" or row["tool"] != "simple_extractor":
            continue
        transformed_stem = Path(row["filename"]).stem
        expected = expected_hash.get(transformed_stem, "")
        actual   = row["payload_sha256"]
        extracted    = row["payload_extracted"]
        marker_match = row["detected_marker"]

        if extracted == "1" and expected and actual:
            payload_hash_match = int(actual == expected)
        else:
            payload_hash_match = 0

        rows.append({
            "original_stego":     transformed_stem,
            "transform":          row["transform"],
            "extracted":          extracted,
            "marker_match":       marker_match,
            "payload_hash_match": payload_hash_match,
            "notes":              row["status"],
        })

output_path.parent.mkdir(exist_ok=True)
with output_path.open("w", newline="", encoding="utf-8") as file:
    fields = ["original_stego", "transform", "extracted",
              "marker_match", "payload_hash_match", "notes"]
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print(f"payload survival rows: {len(rows)}")
