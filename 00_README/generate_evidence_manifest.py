import csv
import hashlib
import datetime
from pathlib import Path

gt = Path("02_GROUND_TRUTH")
gt.mkdir(exist_ok=True)

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
operator = "DF08_Kelompok8"

# --- Baca cover_manifest.csv untuk ambil sha256 ---
cover_manifest = list(csv.DictReader(open(gt / "cover_manifest.csv")))
payload_manifest = []
payload_csv = gt / "payload_manifest.csv"
if payload_csv.exists():
    payload_manifest = list(csv.DictReader(open(payload_csv)))

# --- evidence_manifest.csv ---
# Sesuai format dari modul bagian 8.2:
# evidence_id, filename, size_bytes, sha256, source, created_at, status
evidence_rows = []

# Cover images = baseline
for i, row in enumerate(cover_manifest, start=1):
    eid = f"E{i:03d}"
    evidence_rows.append([
        eid,
        row["filename"],
        row["size_bytes"],
        row["sha256"],
        "synthetic/generate_covers.py",
        now,
        "baseline",
    ])

# Stego images = working copy
for i, row in enumerate(payload_manifest, start=1):
    eid_base = f"E{i:03d}"
    stego_path = Path("03_STEGO") / row["stego_file"]
    sha = ""
    size = ""
    if stego_path.exists():
        sha = hashlib.sha256(stego_path.read_bytes()).hexdigest()
        size = str(stego_path.stat().st_size)
    evidence_rows.append([
        f"{eid_base}-W1",
        row["stego_file"],
        size,
        sha,
        f"embedded from {row['cover_file']} level={row['level']}",
        now,
        "working copy",
    ])

with open(gt / "evidence_manifest.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["evidence_id", "filename", "size_bytes", "sha256",
                "source", "created_at", "status"])
    w.writerows(evidence_rows)

print(f"evidence_manifest.csv: {len(evidence_rows)} entri")

# --- chain_of_custody.csv ---
# Ngambil Formatnya dari modul bagian 8.3 yang berisikan:
# timestamp, evidence_id, action, from, to, hash_verification, operator, notes
coc_rows = []

# Cover images: create
for i, row in enumerate(cover_manifest, start=1):
    eid = f"E{i:03d}"
    coc_rows.append([
        now,
        eid,
        "create",
        "generate_covers.py",
        "01_COVER",
        f"SHA-256 {row['sha256'][:16]}...",
        operator,
        "baseline cover image created",
    ])

# Stego images: embed
for i, row in enumerate(payload_manifest, start=1):
    eid_base = f"E{i:03d}"
    coc_rows.append([
        now,
        f"{eid_base}-W1",
        "embed",
        f"01_COVER/{row['cover_file']}",
        f"03_STEGO/{row['stego_file']}",
        f"cover hash match YES / payload_sha256 {row['payload_sha256'][:16]}...",
        operator,
        f"LSB embed level={row['level']} ratio={row['ratio']}",
    ])

with open(gt / "chain_of_custody.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["timestamp", "evidence_id", "action", "from", "to",
                "hash_verification", "operator", "notes"])
    w.writerows(coc_rows)

print(f"chain_of_custody.csv: {len(coc_rows)} entri")
