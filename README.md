# 🧩 Image Processing Pipeline – Beginner Guide

This project helps you process images with different steps like **format conversion, convex hull masking, grayscale, and downscaling**.
You can control everything using **toggles in a JSON config**.

The repo also has tools to **test many different configurations at once** and generate a **report with charts and images**.

---

## 1. 📦 Setup Instructions

### Step 1: Clone the repo

```bash
git clone https://github.com/mukhokironmoy/NewroKaaya_Internship.git
cd your-repo
```

### Step 2: Create a virtual environment (Python 3.9)

```bash
python3.9 -m venv .venv
# Linux/Mac
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate
```

### Step 3: Install requirements

```bash
pip install -r requirements.txt
```

---

## 2. 📂 Project Overview

Key scripts:

- **`run.py`** → Runs the pipeline on one configuration (you edit JSON inside it or load an external one).
- **`test_pipeline_report.py`** → Runs many test cases (from JSON files in `test_cases/`) and generates reports.
- Helper scripts:

  - `sample_creator.py` → picks a random sample of images
  - `convert_format.py` → changes image format (JPG/WEBP)
  - `convex_hull.py` → applies background mask
  - `grayscale.py` → turns images grayscale
  - `downquality_and_downscale.py` → resizes / adjusts quality

Outputs:

- `output/final_results/` → results from your last run
- `test_cases/<TEST_NAME>/<timestamp>/` → results & reports from batch testing

---

## 3. ▶️ Running the Pipeline with `run.py`

There are **two ways to set config in run.py**:

---

### **Option A: Edit Inline JSON (easiest to start with)**

Inside `run.py`, you’ll see:

```python
CONFIG_JSON = """
{
  "name": "WebP Grayscale",
  "SAMPLE_INPUT_DIR": "C:/path/to/your/images",
  "SAMPLE_SIZE": 50,
  "TOGGLE_SAMPLE_CREATOR": true,
  "TOGGLE_CONVERT_FORMAT": true,
  "TOGGLE_CONVEX_HULL": true,
  "TOGGLE_CONVEX_HULL_CROP": false,
  "TOGGLE_GRAYSCALE": true,
  "TOGGLE_DOWNSCALE": false,
  "OUTPUT_FORMAT": "webp",
  "JPEG_QUALITY": 100,
  "WEBP_QUALITY": 100,
  "SCALE_FACTOR": 1,
  "PADDING": 60,
  "SAVE_DEBUG": false
}
"""
```

👉 **What to change here:**

- `SAMPLE_INPUT_DIR`: Path to your input folder of images.

  - Example Windows: `"C:/Users/you/Pictures/my_dataset"`
  - Example Linux/Mac: `"/home/you/Pictures/my_dataset"`

- `SAMPLE_SIZE`: Number of random images to use if `TOGGLE_SAMPLE_CREATOR = true`.

👉 **How to run:**

```bash
python run.py
```

Results go to `output/final_results/`.

---

### **Option B: Use an External JSON Config**

1. Create a new file, e.g. `config.json`, with the same structure as above.
2. In `run.py`, comment out **Option A** and uncomment Option B:

   ```python
   # CONFIG_PATH = Path("config.json")
   # with open(CONFIG_PATH, "r", encoding="utf-8") as f:
   #     CONFIG = json.load(f)
   ```

3. Now run:

   ```bash
   python run.py
   ```

---

## 4. 🧪 Running Batch Tests with `test_pipeline_report.py`

If you want to try **many configs automatically**:

1. Look inside `test_cases/`.

   - Example: `combination_of_controls.json`, `Individual_controls_testing.json`
   - Each file is just a list of JSON objects (multiple configs).

2. In `test_pipeline_report.py`, edit these two lines:

   ```python
   TEST_NAME = "Individual_controls_testing"
   TEST_JSON_PATH = r"test_cases\combination_of_controls.json"
   ```

👉 **What to change here:**

- `TEST_NAME`: Just a label for the output folder.
- `TEST_JSON_PATH`: Path to your test JSON file (choose one from `test_cases/` or create your own).

3. Run:

   ```bash
   python test_pipeline_report.py
   ```

👉 Outputs will appear in:

```
test_cases/<TEST_NAME>/<timestamp>/
```

Includes:

- `compression_report.csv` → table with file sizes & compression
- `sizes_comparison.png` → bar chart (before vs after)
- `compression_percent.png` → line chart (compression %)
- `compression_report.pdf` → summary table + graphs + case-by-case images

---

## 5. 🔀 Explanation of Toggles

Each config JSON can toggle stages on/off:

| Key                       | What it does                            |
| ------------------------- | --------------------------------------- |
| `TOGGLE_SAMPLE_CREATOR`   | Copy random sample into `test_sample/`  |
| `TOGGLE_CONVERT_FORMAT`   | Convert to `OUTPUT_FORMAT` with quality |
| `TOGGLE_CONVEX_HULL`      | Apply background removal mask           |
| `TOGGLE_CONVEX_HULL_CROP` | Crop tightly to mask                    |
| `TOGGLE_GRAYSCALE`        | Convert to grayscale                    |
| `TOGGLE_DOWNSCALE`        | Downscale by `SCALE_FACTOR`             |
| `SAVE_DEBUG`              | Save debug images with landmarks/hull   |

Other parameters:

- `OUTPUT_FORMAT`: `"jpg"`, `"webp"`, `"png"`, etc.
- `JPEG_QUALITY`, `WEBP_QUALITY`: 0–100 quality factors
- `SCALE_FACTOR`: e.g. `0.75` → shrink to 75%
- `PADDING`: Extra pixels around hull mask

---

## 6. 🖼 Example Walkthroughs

### Example 1: Single run with grayscale

- Edit `run.py` → set `SAMPLE_INPUT_DIR` to your dataset
- Set `"TOGGLE_GRAYSCALE": true`
- Run `python run.py`
- Output in `output/final_results/`

### Example 2: Run predefined batch

- Open `test_pipeline_report.py`
- Point to `test_cases/combination_of_controls.json`
- Run `python test_pipeline_report.py`
- Check `test_cases/combination_of_controls/<timestamp>/compression_report.pdf`

### Example 3: Make your own test JSON

- Copy `test_cases/combination_of_controls.json` → `test_cases/my_experiments.json`
- Edit toggles/parameters
- Point `TEST_JSON_PATH` to your file
- Run the test report script

---
