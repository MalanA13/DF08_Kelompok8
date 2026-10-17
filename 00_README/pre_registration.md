## Pre-Registration DF08 Kelompok 8

### RQ Final
- RQ1: Seberapa baik zsteg/simple detector membedakan cover vs LSB-stego
       pada payload level berbeda?
- RQ2: Bagaimana resize, lossless re-save, convert, dan JPEG recompression
       memengaruhi detectability dan payload survival?
- RQ3: Berapa false-positive rate pada clean images?

### Definisi Detected
Output tool mengandung marker string: DF08_PAYLOAD_
(Tidak menganggap semua output zsteg sebagai positive)

### Rule TP/FP/TN/FN
- TP = is_stego=1 AND detected=1
- FP = is_stego=0 AND detected=1
- TN = is_stego=0 AND detected=0
- FN = is_stego=1 AND detected=0

### Jumlah Kasus dan Replikasi
- 160 file (40 clean + 120 stego)
- Minimal 3 replikasi per konfigurasi utama

### Kriteria Excluded/Failed Run
- Failed run TIDAK dihapus, diberi alasan di kolom notes
- Run dianggap failed jika tool error/crash tanpa output
