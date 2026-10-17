import csv
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

fig_dir = "08_ANALYSIS/figures"
os.makedirs(fig_dir, exist_ok=True)

def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

orig  = read("08_ANALYSIS/detection_results.csv")
trans = read("07_RAW_RESULTS/transformed_detection.csv")
surv  = read("08_ANALYSIS/payload_survival.csv")

print("=" * 60)
print("METRIK ORIGINAL SET")
print("=" * 60)

for tool in ["zsteg", "simple_extractor"]:
    subset = [r for r in orig if r["tool"] == tool]
    tp = sum(int(r["tp"]) for r in subset)
    fp = sum(int(r["fp"]) for r in subset)
    tn = sum(int(r["tn"]) for r in subset)
    fn = sum(int(r["fn"]) for r in subset)
    precision   = tp / (tp + fp) if (tp + fp) else "NA"
    recall      = tp / (tp + fn) if (tp + fn) else "NA"
    f1 = (2 * precision * recall / (precision + recall)
          if isinstance(precision, float) and isinstance(recall, float)
          and (precision + recall) else "NA")
    specificity = tn / (tn + fp) if (tn + fp) else "NA"
    fpr         = fp / (fp + tn) if (fp + tn) else "NA"
    print(f"\n{tool}:")
    print(f"  TP={tp}  FP={fp}  TN={tn}  FN={fn}")
    print(f"  Precision={precision}  Recall={recall}  F1={f1}")
    print(f"  Specificity={specificity}  FPR={fpr}")
    for level in ["low", "medium", "high"]:
        s = [r for r in subset if r["payload_ratio"] == level]
        if s:
            det = sum(int(r["detected"]) for r in s)
            print(f"  {level}: {det}/{len(s)} detected")

# Fig 1: Detection vs Payload Level (RQ1)
fig, ax = plt.subplots(figsize=(8, 5))
levels = ["low", "medium", "high"]
for tool in ["zsteg", "simple_extractor"]:
    rates = []
    for lvl in levels:
        subset = [r for r in orig if r["tool"] == tool and r["payload_ratio"] == lvl]
        detected = sum(int(r["detected"]) for r in subset)
        rates.append(detected / len(subset) * 100 if subset else 0)
    ax.plot(levels, rates, marker="o", label=tool)
ax.set_xlabel("Payload Level"); ax.set_ylabel("Detection Rate (%)")
ax.set_title("RQ1: Detection Rate vs Payload Level (Original Set)")
ax.set_ylim(0, 105); ax.legend(); ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(f"{fig_dir}/fig1_detection_vs_payload.png", dpi=150); plt.close()

# Fig 2: FPR pada Clean Images (RQ3)
fig, ax = plt.subplots(figsize=(6, 4))
tools = ["zsteg", "simple_extractor"]; fprs = []
for tool in tools:
    clean = [r for r in orig if r["tool"] == tool and r["is_stego"] == "0"]
    fp = sum(int(r["fp"]) for r in clean)
    fprs.append(fp / len(clean) * 100 if clean else 0)
ax.bar(tools, fprs, color=["steelblue", "coral"])
ax.set_ylabel("False Positive Rate (%)")
ax.set_title("RQ3: FPR on Clean Images")
ax.set_ylim(0, max(max(fprs) + 5, 5))
fig.tight_layout()
fig.savefig(f"{fig_dir}/fig2_fpr_clean.png", dpi=150); plt.close()

# Fig 3: Detection per Transform (RQ2)
transforms = ["resave", "resize", "convert", "jpeg"]
fig, ax = plt.subplots(figsize=(8, 5))
for tool in ["zsteg", "simple_extractor"]:
    rates = []
    for tr in transforms:
        subset = [r for r in trans if r["tool"] == tool and r["transform"] == tr
                  and r["truth"] == "stego" and r["status"] != "unsupported"]
        if not subset: rates.append(0); continue
        detected = sum(int(r["detected_marker"]) for r in subset)
        rates.append(detected / len(subset) * 100)
    ax.plot(transforms, rates, marker="s", label=tool)
ax.set_xlabel("Transformation"); ax.set_ylabel("Detection Rate (%)")
ax.set_title("RQ2: Stego Detection Rate per Transform")
ax.set_ylim(0, 105); ax.legend(); ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(f"{fig_dir}/fig3_detection_per_transform.png", dpi=150); plt.close()

# Fig 4: Payload Survival per Transform (RQ2)
survival = {}
for r in surv:
    tr = r["transform"]
    if tr not in survival: survival[tr] = {"total": 0, "exact": 0}
    survival[tr]["total"] += 1
    if str(r["payload_hash_match"]) == "1": survival[tr]["exact"] += 1
fig, ax = plt.subplots(figsize=(7, 5))
trs = [t for t in transforms if t in survival]
rates_surv = [survival[t]["exact"] / survival[t]["total"] * 100
              if survival[t]["total"] else 0 for t in trs]
colors = ["green" if r > 50 else "orange" if r > 0 else "red" for r in rates_surv]
ax.bar(trs, rates_surv, color=colors)
ax.set_xlabel("Transformation"); ax.set_ylabel("Exact Payload Survival (%)")
ax.set_title("RQ2: Payload Survival Rate per Transform"); ax.set_ylim(0, 105)
for i, v in enumerate(rates_surv): ax.text(i, v + 2, f"{v:.0f}%", ha="center", fontweight="bold")
fig.tight_layout()
fig.savefig(f"{fig_dir}/fig4_payload_survival.png", dpi=150); plt.close()

# Fig 5: Confusion Matrix
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for idx, tool in enumerate(["zsteg", "simple_extractor"]):
    subset = [r for r in orig if r["tool"] == tool]
    tp = sum(int(r["tp"]) for r in subset)
    fp = sum(int(r["fp"]) for r in subset)
    tn = sum(int(r["tn"]) for r in subset)
    fn = sum(int(r["fn"]) for r in subset)
    matrix = np.array([[tn, fp], [fn, tp]]); ax = axes[idx]
    ax.imshow(matrix, cmap="Blues", vmin=0)
    for (y, x), val in np.ndenumerate(matrix):
        ax.text(x, y, str(val), ha="center", va="center",
                fontsize=16, fontweight="bold")
    ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
    ax.set_xticklabels(["Predicted Neg", "Predicted Pos"])
    ax.set_yticklabels(["Actual Neg", "Actual Pos"]); ax.set_title(tool)
fig.suptitle("Confusion Matrix (Original Set)", fontweight="bold")
fig.tight_layout()
fig.savefig(f"{fig_dir}/fig5_confusion_matrix.png", dpi=150); plt.close()

print(f"\nSemua grafik tersimpan di {fig_dir}/")
