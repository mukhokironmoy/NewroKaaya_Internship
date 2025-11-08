"""
MozJPEG-Integrated Test Pipeline (Fixed Version)
------------------------------------------------
Runs multiple configurations from a JSON file using the updated run.py pipeline
that supports MozJPEG compression and sample creation.
Generates CSV, PNG graphs, and a PDF report comparing compression performance.
Now correctly handles grayscale visualization in Matplotlib (no false color).
"""

import json, shutil, subprocess, sys, textwrap
from pathlib import Path
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image

# ======================
# Config
# ======================
TEST_NAME = "mozjpeg_combination_test"
TEST_JSON_PATH = Path("test_cases\dataset_comparison.json")
PIPELINE_SCRIPT = "run.py"

# Default MozJPEG path (update if needed)
MOZJPEG_PATH = r"C:/DATA/Internships/Newro Kaaya/Working_Build_v3/mozjpeg_4.1.1_x64/mozjpeg_4.1.1_x64/shared/tools/cjpeg.exe"

# ======================
# Helpers
# ======================
def get_folder_size(path: Path) -> int:
    """Returns total folder size in bytes."""
    return sum(f.stat().st_size for f in path.glob("**/*") if f.is_file())

# ======================
# Main test runner
# ======================
def run_experiments():
    with open(TEST_JSON_PATH, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = Path("test_cases") / TEST_NAME / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)
    buffer_dir = run_dir / "buffers"
    buffer_dir.mkdir(parents=True, exist_ok=True)

    results = []

    for idx, case in enumerate(test_cases, start=1):
        print(f"\n=== Running test case {idx}: {case['name']} ===")

        # --- Ensure MozJPEG + Sample Creation are always enabled ---
        case["MOZJPEG_PATH"] = case.get("MOZJPEG_PATH", MOZJPEG_PATH)
        case["TOGGLE_SAMPLE_CREATOR"] = True

        # Write current case config
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(case, f, indent=2)

        # Run pipeline safely
        try:
            subprocess.run([sys.executable, PIPELINE_SCRIPT], check=True)
        except subprocess.CalledProcessError:
            print(f"⚠️ Pipeline failed for case {case['name']}")
            continue

        # Measure compression
        sample_dir = Path("test_sample")
        final_dir = Path("output/final_results")

        sample_size = get_folder_size(sample_dir)
        final_size = get_folder_size(final_dir)
        compression = 100 * (1 - final_size / sample_size) if sample_size > 0 else 0

        # Copy one sample + final example image for comparison
        sample_img = next(sample_dir.glob("*.jpg"), None)
        final_img = next(final_dir.glob("*.jpg"), None)
        if sample_img and final_img:
            case_buf_dir = buffer_dir / f"case_{idx}"
            case_buf_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(sample_img, case_buf_dir / "sample.jpg")
            shutil.copy(final_img, case_buf_dir / "final.jpg")

        # Collect results
        results.append({
            "Case": case["name"],
            "JPEG_Q": case.get("JPEG_QUALITY", 80),
            "Scale": case.get("SCALE_FACTOR", 1.0),
            "ConvexHull": case.get("TOGGLE_CONVEX_HULL", True),
            "Crop": case.get("TOGGLE_CONVEX_HULL_CROP", False),
            "Grayscale": case.get("TOGGLE_GRAYSCALE", True),
            "Downscale": case.get("TOGGLE_DOWNSCALE", False),
            "MozJPEG": Path(case["MOZJPEG_PATH"]).exists(),
            "SampleSizeKB": sample_size / 1024,
            "FinalSizeKB": final_size / 1024,
            "Compression%": compression,
        })

    df = pd.DataFrame(results)
    if not df.empty:
        df.to_csv(run_dir / "compression_report.csv", index=False)
        print(f"\n✅ Results saved → {run_dir/'compression_report.csv'}")
        generate_pdf_report(df, run_dir)
    else:
        print("⚠️ No successful test cases recorded.")
    return df

# ======================
# PDF report generator
# ======================
def generate_pdf_report(df: pd.DataFrame, run_dir: Path):
    df = df.copy()
    df["Case"] = df["Case"].apply(lambda x: "\n".join(textwrap.wrap(x, width=18)))

    # ---------- Charts ----------
    plt.figure(figsize=(10,6))
    bar_width = 0.35
    x = range(len(df))
    plt.bar([i - bar_width/2 for i in x], df["SampleSizeKB"], width=bar_width, label="Sample Total")
    plt.bar([i + bar_width/2 for i in x], df["FinalSizeKB"], width=bar_width, label="Final Total")
    plt.xticks(x, df["Case"], rotation=20, ha="right")
    plt.ylabel("Folder Size (KB)")
    plt.title("Total Size: Sample vs Final Result")
    plt.legend()
    plt.tight_layout()
    plt.savefig(run_dir / "sizes_comparison.png")

    plt.figure(figsize=(10,6))
    plt.plot(df["Case"], df["Compression%"], marker="o")
    plt.ylabel("Compression (%)")
    plt.title("Compression Achieved per Test Case")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(run_dir / "compression_percent.png")

    # ---------- PDF Generation ----------
    with PdfPages(run_dir / "compression_report.pdf") as pdf:
        # Table
        fig, ax = plt.subplots(figsize=(12,4))
        ax.axis("tight"); ax.axis("off")
        table = ax.table(cellText=df.round(2).values, colLabels=df.columns, loc="center")
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1.2, 1.4)
        pdf.savefig(fig); plt.close(fig)

        # Charts
        for img_file in ["sizes_comparison.png", "compression_percent.png"]:
            img = plt.imread(run_dir / img_file)
            fig, ax = plt.subplots(figsize=(10,6))
            ax.imshow(img)
            ax.axis("off")
            ax.set_title(img_file.replace(".png", "").replace("_", " ").title())
            pdf.savefig(fig); plt.close(fig)

        # ---------- Case-by-case comparison ----------
        buffer_dir = run_dir / "buffers"
        for idx, row in df.iterrows():
            case_buf = buffer_dir / f"case_{idx+1}"
            sample = case_buf / "sample.jpg"
            final = case_buf / "final.jpg"
            if not sample.exists() or not final.exists():
                continue

            s_img = Image.open(sample)
            f_img = Image.open(final)
            s_res, f_res = s_img.size, f_img.size
            s_size, f_size = sample.stat().st_size / 1024, final.stat().st_size / 1024

            fig, axs = plt.subplots(1, 2, figsize=(12,6))
            for ax, im, name, res, size in [
                (axs[0], s_img, "Sample", s_res, s_size),
                (axs[1], f_img, "Final", f_res, f_size)
            ]:
                # ✅ FIX: Display grayscale correctly (no false color)
                if im.mode == "L":
                    ax.imshow(im, cmap="gray", vmin=0, vmax=255)
                else:
                    ax.imshow(im)
                ax.axis("off")
                ax.set_title(f"{name}\n{res[0]}×{res[1]} | {size:.1f} KB")

            plt.suptitle(f"Case {idx+1}: {row['Case']}")
            pdf.savefig(fig)
            plt.close(fig)

    print(f"📄 PDF report saved → {run_dir/'compression_report.pdf'}")

# ======================
# Entry point
# ======================
if __name__ == "__main__":
    df = run_experiments()
    print("\n🎉 Done! All reports generated successfully.")
