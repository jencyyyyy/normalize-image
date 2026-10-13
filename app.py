from flask import Flask, render_template, request
from PIL import Image
import numpy as np
import io
import base64

app = Flask(__name__)

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

        # Encode directly to base64 in memory - no disk writes.
        # Required on serverless platforms like Vercel, where the filesystem
        # is read-only/ephemeral and a saved file may not exist by the time
        # a later request (possibly hitting a different instance) asks for it.
        buffer = io.BytesIO()
        normalized.save(buffer, format="PNG")
        buffer.seek(0)
        encoded = base64.b64encode(buffer.read()).decode("utf-8")
        data_uri = f"data:image/png;base64,{encoded}"

        return render_template("index.html", result_image=data_uri)

    return render_template("index.html")


# Vercel's Python runtime imports this file and looks for a WSGI app object
# named "app" - no app.run() call is needed or used in that environment.
if __name__ == "__main__":
    app.run(debug=True)
