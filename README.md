# 🧩 Image Compression & Masking Pipeline (Final Build – MozJPEG Integrated)

This project is a complete **image preprocessing and compression pipeline** designed for dataset optimization in projects like **motion capture and rehabilitation analysis**.
It performs **pose-based background masking**, **grayscale conversion**, **downscaling**, and **MozJPEG-based compression** — all driven by a JSON configuration.

You can run a **single configuration** (`run.py`) or **batch experiments** (`test_pipeline_run.py`) to compare performance across datasets.

---

## ⚙️ 1. Setup Guide

### Step 1 — Clone and open project

```bash
git clone https://github.com/mukhokironmoy/NewroKaaya_Internship.git
cd NewroKaaya_Internship
```

### Step 2 — Create and activate environment

```bash
py -3.9 -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate
# Linux/Mac
source .venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Verify folder structure

Since **MozJPEG** is now included directly in your project, your folder tree should look like this:

```
📂 NewroKaaya_Internship
 ┣ 📜 run.py
 ┣ 📜 test_pipeline_run.py
 ┣ 📜 config.json
 ┣ 📁 mozjpeg_4.1.1_x64/
 ┣ 📁 test_cases/
 ┣ 📁 output/
 ┣ 📁 test_sample/
 ┗ 📜 requirements.txt
```

No external installation is needed — `run.py` will automatically reference `mozjpeg_4.1.1_x64/tools/cjpeg.exe`.

---

## 🧾 2. Configuration File (`config.json`)

Every run is controlled by a JSON file like this:

```json
{
  "name": "JPG QF = 10 b/w",
  "INPUT_DIR": "C:/DATA/Dataset/Patient1",
  "OUTPUT_DIR": "output/final_results",
  "TEMP_DIR": "test_sample",
  "SAMPLE_SIZE": 20,
  "TOGGLE_SAMPLE_CREATOR": true,
  "TOGGLE_CONVEX_HULL": true,
  "TOGGLE_CONVEX_HULL_CROP": false,
  "TOGGLE_GRAYSCALE": true,
  "TOGGLE_DOWNSCALE": true,
  "JPEG_QUALITY": 10,
  "SCALE_FACTOR": 1,
  "PADDING": 60,
  "SAVE_DEBUG": false,
  "MOZJPEG_PATH": "mozjpeg_4.1.1_x64/shared/tools/cjpeg.exe"
}
```

### 🔍 Parameter Reference

| Key                       | Description                                             |
| ------------------------- | ------------------------------------------------------- |
| `name`                    | Run label (used in logs and reports).                   |
| `INPUT_DIR`               | Folder path containing `.jpg` source frames.            |
| `OUTPUT_DIR`              | Where processed images are saved.                       |
| `TEMP_DIR`                | Temporary folder for sampled inputs.                    |
| `SAMPLE_SIZE`             | Number of images used per run when sampling is ON.      |
| `TOGGLE_SAMPLE_CREATOR`   | Randomly select a subset from input images.             |
| `TOGGLE_CONVEX_HULL`      | Apply human-body mask via MediaPipe Pose.               |
| `TOGGLE_CONVEX_HULL_CROP` | Crop tightly to the detected body region.               |
| `TOGGLE_GRAYSCALE`        | Convert output to grayscale.                            |
| `TOGGLE_DOWNSCALE`        | Downscale output using `SCALE_FACTOR`.                  |
| `JPEG_QUALITY`            | JPEG compression quality (0–100).                       |
| `SCALE_FACTOR`            | Scaling multiplier (e.g., 0.8 = 80%).                   |
| `PADDING`                 | Adds extra space around the convex hull mask.           |
| `SAVE_DEBUG`              | Save mask/landmark visualization for inspection.        |
| `MOZJPEG_PATH`            | Relative path to MozJPEG’s `cjpeg.exe`. (Now included.) |

---

## ▶️ 3. Running a Single Pipeline (`run.py`)

### Step 1 — Configure

Edit `config.json`:

- Change `INPUT_DIR` to your dataset folder.
- Update `SAMPLE_SIZE` if needed.
- Ensure `"MOZJPEG_PATH": "mozjpeg_4.1.1_x64/shared/tools/cjpeg.exe"`.

### Step 2 — Run

```bash
python run.py
```

### Step 3 — Output

- Processed images are stored in `output/final_results/`.
- Console logs show each stage:

  ```
  🚀 Running unified JPG pipeline: JPG QF = 10 b/w
  ✅ Copied 20 samples to test_sample
  ✅ [MozJPEG] Saved IMG_0001.jpg (Q=10)
  🎉 Processing complete!
  ```

✅ **Black background maintained**
✅ **Grayscale handled properly**
✅ **Compression powered by MozJPEG**

---

## 🧪 4. Batch Testing Multiple Configurations (`test_pipeline_run.py`)

This script automates running several configurations and generates detailed compression analytics.

### Step 1 — Choose test JSON

Inside `test_cases/`, you’ll find prebuilt options like:

- `dataset_comparison.json`
- `combination_of_controls.json`

Each file is a list of configurations (same structure as `config.json`).

Example:

```json
[
  {
    "name": "QF10_Color",
    "INPUT_DIR": "Data/Set1",
    "TOGGLE_GRAYSCALE": false,
    "JPEG_QUALITY": 10
  },
  {
    "name": "QF10_Grayscale",
    "INPUT_DIR": "Data/Set1",
    "TOGGLE_GRAYSCALE": true,
    "JPEG_QUALITY": 10
  }
]
```

### Step 2 — Set paths inside `test_pipeline_run.py`

```python
TEST_NAME = "dataset_comparison"
TEST_JSON_PATH = Path("test_cases/dataset_comparison.json")
```

### Step 3 — Run

```bash
python test_pipeline_run.py
```

### Step 4 — View outputs

All results appear in:

```
test_cases/<TEST_NAME>/<timestamp>/
```

Includes:

| File                      | Description                                       |
| ------------------------- | ------------------------------------------------- |
| `compression_report.csv`  | Table comparing size, compression %, and toggles. |
| `sizes_comparison.png`    | Bar chart: total input vs output size.            |
| `compression_percent.png` | Line chart: compression % by case.                |
| `compression_report.pdf`  | Full PDF report with charts + sample comparisons. |

---

## 🧮 5. How to Interpret Outputs

| Metric           | Meaning                                 |
| ---------------- | --------------------------------------- |
| **SampleSizeKB** | Total size of sampled inputs.           |
| **FinalSizeKB**  | Total size after processing.            |
| **Compression%** | Percent reduction in size.              |
| **Grayscale**    | Whether grayscale improved compression. |

Example report snippet:

| Case            | JPEG_Q | Grayscale | Compression % |
| --------------- | ------ | --------- | ------------- |
| JPG QF = 10     | 10     | False     | 57.9          |
| JPG QF = 10 b/w | 10     | True      | 65.5          |

✅ Grayscale images show higher compression rates (≈8–10% improvement).
✅ MozJPEG ensures smaller file sizes without visible degradation.

---

## 🧠 6. Folder Behavior Summary

| Folder                                | Description                                   |
| ------------------------------------- | --------------------------------------------- |
| `test_sample/`                        | Temporary folder used if sampling is enabled. |
| `output/final_results/`               | Main output directory for processed images.   |
| `test_cases/<TEST_NAME>/<timestamp>/` | Stores analytics and PDF reports.             |
| `mozjpeg_4.1.1_x64/`                  | Internal MozJPEG binaries for compression.    |

---

## 🧰 7. Troubleshooting

| Issue                     | Cause                             | Fix                                              |
| ------------------------- | --------------------------------- | ------------------------------------------------ |
| ⚠️ “No .jpg files found”  | Wrong `INPUT_DIR` path            | Point to folder containing `.jpg` images         |
| ⚠️ MozJPEG failed         | Missing or invalid `MOZJPEG_PATH` | Use `"mozjpeg_4.1.1_x64/shared/tools/cjpeg.exe"` |
| ⚠️ “Could not read image” | Corrupted or non-image files      | Ensure clean dataset                             |
| Empty charts/reports      | No successful test cases          | Check that each test JSON has valid inputs       |

---

## 🧾 8. Typical Workflow

1️⃣ Prepare dataset folder (only `.jpg` frames).
2️⃣ Configure `config.json` with your settings.
3️⃣ Run `python run.py` for single testing.
4️⃣ Validate output images in `output/final_results`.
5️⃣ Create `test_cases/my_experiment.json` to automate comparisons.
6️⃣ Run `python test_pipeline_run.py` for reports.
7️⃣ Review `compression_report.pdf` for insights.

---

## 🧩 9. Version & Credits

**Version:** v3.1 (Integrated MozJPEG Build)

**Core Tools:** OpenCV · MediaPipe · NumPy · Matplotlib · Pandas · Pillow · MozJPEG

**Author:** _Kironmoy Mukherjee_

**Internship:** _Newro Kaaya – AI-based Motion Capture & Background Optimization_

**Goal:** Efficient frame-level image reduction for large medical/rehabilitation datasets.
