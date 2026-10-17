from pathlib import Path
import subprocess
import csv

sets = [('clean', Path('01_COVER')), ('stego', Path('03_STEGO'))]
rows = []
Path('05_ZSTEG/logs').mkdir(parents=True, exist_ok=True)

for truth, root in sets:
    for p in sorted(root.iterdir()):
        if not p.is_file() or p.suffix.lower() not in ('.png', '.bmp'):
            continue
        print(f"  [{truth}] {p.name} ...", end=' ', flush=True)
        try:
            r = subprocess.run(
                ['zsteg', '-a', str(p)],
                capture_output=True, text=True, timeout=60
            )
            text = (r.stdout or '') + '\n' + (r.stderr or '')
            status = 'ok'
        except subprocess.TimeoutExpired:
            text = 'TIMEOUT'
            r = type('r', (), {'returncode': -1})()
            status = 'timeout'
        (Path('05_ZSTEG/logs') / (p.name + '.txt')).write_text(
            text, encoding='utf-8', errors='replace'
        )
        detected = 'DF08_PAYLOAD_' in text
        rows.append([truth, p.name, int(detected), r.returncode])
        print(f"detected={int(detected)} [{status}]")

with open('07_RAW_RESULTS/zsteg_detection.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['truth', 'filename', 'detected_marker', 'returncode'])
    w.writerows(rows)

print(f"batch zsteg selesai: {len(rows)} file")
