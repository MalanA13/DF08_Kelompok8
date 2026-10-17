from pathlib import Path
import csv
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from lsb_tool import extract
except ImportError:
    print("ERROR: lsb_tool.py tidak ditemukan.")
    sys.exit(1)

DATASETS = [("clean", Path("01_COVER")), ("stego", Path("03_STEGO"))]
LOG_DIR = Path("06_SIMPLE_EXTRACTOR/logs")
RESULT_DIR = Path("07_RAW_RESULTS")
LOG_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {".png", ".bmp"}
rows = []

for truth, root in DATASETS:
    if not root.exists():
        print(f"WARNING: {root} tidak ditemukan.")
        continue
    for p in sorted(root.iterdir()):
        if not p.is_file() or p.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue
        try:
            payload = extract(p)
            valid_payload = payload is not None
            marker_found = payload is not None and b"DF08_PAYLOAD_" in payload

            if truth == "stego" and marker_found:
                classification = "TP"
            elif truth == "stego" and not marker_found:
                classification = "FN"
            elif truth == "clean" and marker_found:
                classification = "FP"
            else:
                classification = "TN"

            log_file = LOG_DIR / f"{p.name}.txt"
            if payload is None:
                log_file.write_text("NO_VALID_PAYLOAD", encoding="utf-8")
            else:
                try:
                    log_file.write_text(payload.decode("utf-8", errors="replace"), encoding="utf-8")
                except Exception:
                    log_file.write_bytes(payload)

            rows.append([truth, p.name, int(valid_payload), int(marker_found), classification])
            print(f"{truth:6} | {p.name:30} | valid={int(valid_payload)} | marker={int(marker_found)} | {classification}")

        except Exception as e:
            log_file = LOG_DIR / f"{p.name}_ERROR.txt"
            log_file.write_text(f"ERROR: {type(e).__name__}: {e}", encoding="utf-8")
            rows.append([truth, p.name, 0, 0, "ERROR"])
            print(f"ERROR pada {p.name}: {e}")

csv_file = RESULT_DIR / "simple_extractor_detection.csv"
with csv_file.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["truth", "filename", "valid_payload", "marker_found", "classification"])
    writer.writerows(rows)

summary = {"TP": 0, "TN": 0, "FP": 0, "FN": 0, "ERROR": 0}
for row in rows:
    if row[4] in summary:
        summary[row[4]] += 1

print(f"\n=== BATCH SIMPLE EXTRACTOR SELESAI ===")
print(f"Total: {len(rows)} | TP: {summary['TP']} | TN: {summary['TN']} | FP: {summary['FP']} | FN: {summary['FN']} | ERROR: {summary['ERROR']}")
