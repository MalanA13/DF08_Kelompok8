from pathlib import Path
import csv
import hashlib
import subprocess
import sys
import time

sys.path.insert(0, "00_README")
from lsb_tool import extract

out_dir = Path("04_TRANSFORMED")
rows = []

for truth_dir in sorted(out_dir.iterdir()):
    if not truth_dir.is_dir():
        continue
    truth = truth_dir.name
    for mode_dir in sorted(truth_dir.iterdir()):
        if not mode_dir.is_dir():
            continue
        mode = mode_dir.name
        for path in sorted(mode_dir.iterdir()):
            if not path.is_file():
                continue
            file_type = path.suffix.lstrip(".").upper()

            if file_type in ("PNG", "BMP"):
                t0 = time.perf_counter()
                r = subprocess.run(["zsteg", "-a", str(path)],
                    capture_output=True, text=True)
                zsteg_time = time.perf_counter() - t0
                zsteg_text = (r.stdout or "") + "\n" + (r.stderr or "")
                zsteg_detected = int("DF08_PAYLOAD_" in zsteg_text)
                zsteg_status = "ok"
            else:
                zsteg_time = 0
                zsteg_detected = 0
                zsteg_status = "unsupported"

            t0 = time.perf_counter()
            try:
                payload = extract(path)
                simple_time = time.perf_counter() - t0
                extracted = int(payload is not None)
                text = "" if payload is None else payload.decode("utf-8", "replace")
                simple_detected = int("DF08_PAYLOAD_" in text)
                p_sha = hashlib.sha256(payload).hexdigest() if payload is not None else ""
                simple_status = "ok"
            except Exception as e:
                simple_time = time.perf_counter() - t0
                extracted = 0; simple_detected = 0; p_sha = ""
                simple_status = f"error: {e}"

            rows.append([truth, path.name, file_type, mode,
                "zsteg", zsteg_detected, "", "", zsteg_time, zsteg_status])
            rows.append([truth, path.name, file_type, mode,
                "simple_extractor", simple_detected, extracted, p_sha,
                simple_time, simple_status])
            print(f"  {mode}/{truth}/{path.name}", flush=True)

with open("07_RAW_RESULTS/transformed_detection.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["truth", "filename", "file_type", "transform",
        "tool", "detected_marker", "payload_extracted",
        "payload_sha256", "runtime_sec", "status"])
    w.writerows(rows)

print(f"\ntransformed detection done: {len(rows)} rows")
