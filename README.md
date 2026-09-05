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

## Deploying to Vercel

This app is structured for Vercel's serverless Python runtime:

```
image_normalizer/
├── api/
│   └── index.py      <- Vercel entrypoint, imports the Flask app
├── app.py            <- Flask app (all processing done in-memory, no disk writes)
├── templates/
│   └── index.html
├── requirements.txt
└── vercel.json        <- routes all requests to api/index.py
```

Steps:
1. Push this folder to a GitHub repo (or run `vercel` from inside it with the Vercel CLI).
2. Import the repo in the Vercel dashboard, or run `vercel deploy`.
3. No extra environment variables or build settings are needed — `vercel.json` already points Vercel at `api/index.py`.

**Why the app is structured this way:** Vercel serverless functions have a read-only, ephemeral filesystem (only `/tmp` is writable, and it isn't guaranteed to persist between requests or across different instances). The original local version saved the normalized image to a `processed/` folder and served it via a second request — this breaks on Vercel because the file may not exist by the time the follow-up request arrives. The current version avoids this entirely: the normalized image is base64-encoded and embedded directly in the HTML response (both the `<img>` preview and the download link use a `data:image/png;base64,...` URI), so everything happens within a single request/response cycle with no server-side file state.

## Notes / possible extensions

- Currently normalizes using the **global** min/max across all channels combined. If you'd rather normalize each channel (R, G, B) independently, that's a one-line change in `normalize_image()` (compute min/max with `axis=(0,1)` instead of over the whole array).
- No file size limit is set — for a public deployment you'd want to add `MAX_CONTENT_LENGTH` and clean up old files in `processed/`.
- Uses Flask's built-in dev server — fine for local/personal use; use `gunicorn`/`waitress` for anything production-facing.
