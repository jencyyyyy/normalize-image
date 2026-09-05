from flask import Flask, render_template, request, send_file
from PIL import Image
import numpy as np
import os
import uuid

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_FOLDER = os.path.join(BASE_DIR, "processed")
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "tif", "tiff", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def normalize_image(image: Image.Image) -> Image.Image:
    """
    Normalize every pixel value using:
        X_norm = (X - Xmin) / (Xmax - Xmin)
    then rescale to 0-255 so it can be saved/viewed as a standard image.
    Xmin/Xmax are computed globally across the whole image (all channels).
    """
    arr = np.array(image).astype(np.float64)

    x_min = arr.min()
    x_max = arr.max()

    if x_max - x_min == 0:
        # Flat image (all pixels identical) - avoid divide by zero
        normalized = np.zeros_like(arr)
    else:
        normalized = (arr - x_min) / (x_max - x_min)

    scaled = (normalized * 255.0).round().astype(np.uint8)
    return Image.fromarray(scaled)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("image")

        if not file or file.filename == "":
            return render_template("index.html", error="Please choose an image file.")

        if not allowed_file(file.filename):
            return render_template(
                "index.html",
                error="Unsupported file type. Please upload PNG, JPG, JPEG, BMP, TIF, TIFF, or GIF.",
            )

        try:
            image = Image.open(file.stream)
            image.load()
        except Exception:
            return render_template("index.html", error="Could not read that file as an image.")

        normalized = normalize_image(image)

        filename = f"{uuid.uuid4().hex}.png"
        output_path = os.path.join(PROCESSED_FOLDER, filename)
        normalized.save(output_path, format="PNG")

        return render_template("index.html", result_image=filename)

    return render_template("index.html")


@app.route("/processed/<filename>")
def processed_file(filename):
    path = os.path.join(PROCESSED_FOLDER, filename)
    return send_file(path, mimetype="image/png")


@app.route("/download/<filename>")
def download(filename):
    path = os.path.join(PROCESSED_FOLDER, filename)
    return send_file(path, as_attachment=True, download_name=f"normalized_{filename}")


if __name__ == "__main__":
    app.run(debug=True)