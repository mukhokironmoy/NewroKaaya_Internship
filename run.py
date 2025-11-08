"""
Unified JPG-only image processing pipeline (Final Version — Black Background)
------------------------------------------------------------------------------
Loads configuration from JSON and applies:
  1. Optional sample creation
  2. Convex hull masking (with optional cropping)
  3. Optional grayscale conversion
  4. Optional downscaling
All input and output are strictly .jpg.
This version:
  ✅ Fixes color inversion
  ✅ Maintains black background outside hull
  ✅ Handles grayscale + MozJPEG properly
"""

import cv2, json, shutil, random, subprocess
import numpy as np
from pathlib import Path
from PIL import Image
import mediapipe as mp

# ==========================
# Load Configuration
# ==========================
CONFIG_PATH = Path("config.json")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CFG = json.load(f)

# Convert to Path objects
CFG["INPUT_DIR"] = Path(CFG["INPUT_DIR"])
CFG["OUTPUT_DIR"] = Path(CFG.get("OUTPUT_DIR", "output/final_results"))
CFG["TEMP_DIR"] = Path(CFG.get("TEMP_DIR", "test_sample"))

# Ensure directories exist
for key in ["INPUT_DIR", "OUTPUT_DIR", "TEMP_DIR"]:
    CFG[key].mkdir(parents=True, exist_ok=True)

# ==========================
# Global Controls
# ==========================
TOGGLE_SAMPLE_CREATOR = CFG.get("TOGGLE_SAMPLE_CREATOR", True)
TOGGLE_CONVEX_HULL = CFG.get("TOGGLE_CONVEX_HULL", True)
TOGGLE_CONVEX_HULL_CROP = CFG.get("TOGGLE_CONVEX_HULL_CROP", False)
TOGGLE_GRAYSCALE = CFG.get("TOGGLE_GRAYSCALE", True)
TOGGLE_DOWNSCALE = CFG.get("TOGGLE_DOWNSCALE", False)

SAMPLE_SIZE = CFG.get("SAMPLE_SIZE", 50)
JPEG_QUALITY = CFG.get("JPEG_QUALITY", 80)
SCALE_FACTOR = CFG.get("SCALE_FACTOR", 1.0)
PADDING = CFG.get("PADDING", 60)
SAVE_DEBUG = CFG.get("SAVE_DEBUG", False)

# Mediapipe setup
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, model_complexity=2)
mp_drawing = mp.solutions.drawing_utils

# ==========================
# Utility functions
# ==========================
def clean_dir(path: Path):
    """Remove and recreate directory."""
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def save_jpg(image: np.ndarray, path: Path):
    """
    Save image as JPG using MozJPEG for better compression.
    Accepts BGR or grayscale; outputs correct color with black background.
    """
    CJPEG_PATH = Path(CFG.get("MOZJPEG_PATH", "cjpeg.exe"))
    path.parent.mkdir(parents=True, exist_ok=True)

    temp_png = path.with_name(path.stem + "_temp.png")

    # Write temporary PNG
    if len(image.shape) == 2:  # grayscale
        cv2.imwrite(str(temp_png), image)
    else:  # BGR color
        cv2.imwrite(str(temp_png), image)

    # Try MozJPEG first
    if CJPEG_PATH.exists():
        try:
            subprocess.run([
                str(CJPEG_PATH),
                "-quality", str(JPEG_QUALITY),
                "-progressive",
                "-optimize",
                "-outfile", str(path),
                str(temp_png)
            ], check=True)
            print(f"✅ [MozJPEG] Saved {path.name} (Q={JPEG_QUALITY})")
        except Exception as e:
            print(f"⚠️ MozJPEG failed for {path.name}: {e}")
            _save_with_pillow(image, path)
    else:
        _save_with_pillow(image, path)

    if temp_png.exists():
        temp_png.unlink()


def _save_with_pillow(image: np.ndarray, path: Path):
    """Fallback save using Pillow if MozJPEG unavailable."""
    if len(image.shape) == 2:  # grayscale
        Image.fromarray(image).save(path, "JPEG", quality=JPEG_QUALITY, optimize=True)
    else:  # color image (BGR → RGB)
        Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)).save(path, "JPEG", quality=JPEG_QUALITY, optimize=True)
    print("⚠️ Saved with Pillow fallback.")


def crop_to_mask(image: np.ndarray, mask: np.ndarray):
    """Crops the image tightly around the nonzero region of the mask."""
    ys, xs = np.where(mask > 0)
    if len(xs) == 0 or len(ys) == 0:
        return image
    return image[ys.min():ys.max(), xs.min():xs.max()]


# ==========================
# Stage 1 — Sample Creation
# ==========================
def create_sample(input_dir: Path, output_dir: Path, sample_size: int):
    images = sorted([p for p in input_dir.glob("*.jpg")])
    if not images:
        raise ValueError(f"No .jpg files in {input_dir}")
    sample = random.sample(images, min(sample_size, len(images)))
    for img in sample:
        shutil.copy(img, output_dir / img.name)
    print(f"✅ Copied {len(sample)} samples to {output_dir}")


# ==========================
# Stage 2 — Convex Hull Mask
# ==========================
def apply_convex_hull(img: np.ndarray, crop=False):
    """
    Apply convex hull around detected pose landmarks.
    Keeps inside of hull, fills background with black.
    """
    h, w, _ = img.shape
    rgb_for_pose = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_for_pose)

    if not results.pose_landmarks:
        return img

    # Extract pose points and convex hull
    points = np.array([[int(lm.x * w), int(lm.y * h)] for lm in results.pose_landmarks.landmark])
    hull = cv2.convexHull(points)

    # Create binary mask and apply padding
    mask = np.zeros((h, w), np.uint8)
    cv2.fillConvexPoly(mask, hull, 255)
    mask = cv2.dilate(mask, np.ones((PADDING, PADDING), np.uint8), iterations=1)

    # Black background instead of white
    result = np.zeros_like(img)
    result[mask == 255] = img[mask == 255]

    if crop:
        result = crop_to_mask(result, mask)

    return result  # stays BGR


# ==========================
# Stage 3 — Grayscale
# ==========================
def to_grayscale(img: np.ndarray):
    """Convert color (BGR) image to grayscale."""
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


# ==========================
# Stage 4 — Downscale
# ==========================
def downscale(img: np.ndarray, factor: float):
    """Resize image by given factor."""
    h, w = img.shape[:2]
    new_size = (int(w * factor), int(h * factor))
    return cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)


# ==========================
# Main Pipeline
# ==========================
def pipeline():
    clean_dir(CFG["OUTPUT_DIR"])
    if TOGGLE_SAMPLE_CREATOR:
        clean_dir(CFG["TEMP_DIR"])
        create_sample(CFG["INPUT_DIR"], CFG["TEMP_DIR"], SAMPLE_SIZE)
        source = CFG["TEMP_DIR"]
    else:
        source = CFG["INPUT_DIR"]

    files = list(source.glob("*.jpg"))
    if not files:
        print("⚠️ No input JPG files found.")
        return

    for f in files:
        img = cv2.imread(str(f))
        if img is None:
            print(f"⚠️ Could not read {f.name}")
            continue

        # 1️⃣ Convex Hull
        if TOGGLE_CONVEX_HULL:
            img = apply_convex_hull(img, crop=TOGGLE_CONVEX_HULL_CROP)

        # 2️⃣ Grayscale
        if TOGGLE_GRAYSCALE:
            img = to_grayscale(img)

        # 3️⃣ Downscale
        if TOGGLE_DOWNSCALE and SCALE_FACTOR < 1:
            img = downscale(img, SCALE_FACTOR)

        # 4️⃣ Save result
        out_path = CFG["OUTPUT_DIR"] / f.name
        save_jpg(img, out_path)
        print(f"✅ Saved {out_path.name}")

    print("🎉 Processing complete!")


# ==========================
# Run
# ==========================
if __name__ == "__main__":
    print(f"🚀 Running unified JPG pipeline: {CFG.get('name', 'Unnamed run')}")
    pipeline()
