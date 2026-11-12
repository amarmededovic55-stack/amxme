# Signed: ASDHEM | AMXME Web Solutions
import os
import uuid
import warnings

from flask import current_app
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_W = 1800
Image.MAX_IMAGE_PIXELS = 40_000_000  # reject "decompression bomb" images (~40 MP max)
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP", "GIF"}


class UploadError(Exception):
    pass


def save_image(file_storage, max_w=MAX_W):
    """Validate an uploaded image, re-encode it as WebP and return its public URL path."""
    if not file_storage or not file_storage.filename:
        return None
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)  # ASDHEM | >40 MP = rejected, not just warned
            img = Image.open(file_storage.stream, formats=sorted(ALLOWED_FORMATS))
            img.load()
    except (Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise UploadError("The image is too large (max ~40 megapixels).")
    except (UnidentifiedImageError, OSError, ValueError):
        raise UploadError("The file is not a valid image (use JPG, PNG, WebP or GIF).")
    img = ImageOps.exif_transpose(img)
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA" if "A" in img.getbands() or img.mode == "P" else "RGB")
    if img.width > max_w:
        img = img.resize((max_w, round(img.height * max_w / img.width)), Image.LANCZOS)
    name = f"{uuid.uuid4().hex}.webp"
    img.save(os.path.join(current_app.config["UPLOAD_DIR"], name), "WEBP", quality=86, method=6)
    return f"/uploads/{name}"


def delete_upload(url):
    if url and url.startswith("/uploads/"):
        path = os.path.join(current_app.config["UPLOAD_DIR"], os.path.basename(url))
        try:
            os.remove(path)
        except OSError:
            pass
