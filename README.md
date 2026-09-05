# Pixel Normalizer (Flask)

A small web app: upload a raster image, it normalizes every pixel value with

    X_norm = (X - Xmin) / (Xmax - Xmin)

rescales that to the 0–255 range, and lets you preview + download the result as a PNG.

Xmin/Xmax are computed globally across the whole image (all pixels, all color channels), so the output always spans the full 0–255 range unless the input was a single flat color.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

## How it works

- `app.py` — Flask routes: `/` (upload form + processing), `/processed/<file>` (serves preview), `/download/<file>` (forces download).
- `templates/index.html` — the single-page upload UI.
- Supported input formats: PNG, JPG, JPEG, BMP, TIF/TIFF, GIF.
- Output is always saved as PNG (lossless, keeps exact normalized pixel values).
- Works on both grayscale and RGB(A) images — normalization is applied elementwise across the whole array.

## Notes / possible extensions

- Currently normalizes using the **global** min/max across all channels combined. If you'd rather normalize each channel (R, G, B) independently, that's a one-line change in `normalize_image()` (compute min/max with `axis=(0,1)` instead of over the whole array).
- No file size limit is set — for a public deployment you'd want to add `MAX_CONTENT_LENGTH` and clean up old files in `processed/`.
- Uses Flask's built-in dev server — fine for local/personal use; use `gunicorn`/`waitress` for anything production-facing.
