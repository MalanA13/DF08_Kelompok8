import csv
from pathlib import Path

out = Path("00_README")
out.mkdir(exist_ok=True)

# --- experimental_matrix.csv ---
covers_png = [f"PNG_{i:02d}.png" for i in range(1, 21)]
covers_bmp = [f"BMP_{i:02d}.bmp" for i in range(1, 21)]
all_covers = covers_png + covers_bmp
transforms = ["none", "resave", "resize", "convert", "jpeg"]
payload_levels = ["low", "medium", "high"]

rows = []
idx = 1
for cover in all_covers:
    # clean rows
    for tr in transforms:
        rows.append([idx, cover, "clean", "none", tr, 0])
        idx += 1
    # stego rows
    for level in payload_levels:
        for tr in transforms:
            rows.append([idx, cover, "stego", level, tr, 1 if tr != "jpeg" else 0])
            idx += 1

with open(out / "experimental_matrix.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "cover_file", "truth", "payload_level", "transform", "expected_detected"])
    w.writerows(rows)

print(f"experimental_matrix.csv: {len(rows)} baris")

# --- data_dictionary.csv ---
fields = [
    ("case_id",            "string",  "Kode unik format DF08-STEG-XXX-R1",                    "DF08-STEG-001-R1"),
    ("source_id",          "string",  "Nama file source dari manifest ground truth",           "PNG_01.png"),
    ("file_type",          "string",  "Format file PNG/BMP/JPEG",                             "PNG"),
    ("is_stego",           "int",     "1=stego image 0=clean image",                          "1"),
    ("payload_ratio",      "string",  "Level payload low/medium/high/none",                   "low"),
    ("transform",          "string",  "Transformasi resave/resize/convert/jpeg/none",          "none"),
    ("tool",               "string",  "Nama dan versi tool",                                  "zsteg 0.2.14"),
    ("detected",           "int",     "1=marker DF08_PAYLOAD_ ditemukan 0=tidak",             "1"),
    ("payload_extracted",  "int",     "1=extractor berhasil ekstrak payload valid 0=tidak",   "1"),
    ("payload_hash_match", "int",     "1=SHA256 payload cocok manifest 0=tidak",              "1"),
    ("tp",                 "int",     "True positive baris ini",                              "1"),
    ("fp",                 "int",     "False positive baris ini",                             "0"),
    ("tn",                 "int",     "True negative baris ini",                              "0"),
    ("fn",                 "int",     "False negative baris ini",                             "0"),
    ("runtime_sec",        "float",   "Durasi proses dalam detik",                            "2.34"),
    ("notes",              "string",  "Error/exception/observasi penting",                    "ok"),
]

with open(out / "data_dictionary.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["field_name", "tipe_data", "keterangan", "contoh_nilai"])
    w.writerows(fields)

print(f"data_dictionary.csv: {len(fields)} field")
