#!/usr/bin/env python3
"""Turn REAL fruit photographs into 24-frame 360° turntable assets.

Pipeline per fruit (scripts/photos/<slug>.jpg -> public/assets/agrumea/):
  1. rembg (u2net) cuts the fruit out of the photo -> transparent RGBA.
  2. The cutout is wrapped onto a virtual cylinder and rendered at 24 yaw
     angles (i*15 deg).  A cylindrical UV map makes surface features travel
     across the silhouette as the object turns, so front/back/side views all
     show real photographic pixels (this is the standard pseudo-3D turntable
     technique for single photos).
  3. Each frame is centred on the slider's 1080x1737 canvas with a soft
     contact shadow, saved as fruit-<slug>-turn-{i}.webp (+ front/-side.webp
     aliases for compatibility).

Run:  python3 scripts/make-photo-fruits.py   (needs: pip install pillow numpy rembg onnxruntime)
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

try:
    from rembg import remove, new_session
except Exception as e:  # pragma: no cover
    print("rembg missing:", e); sys.exit(1)

SS = 2
BASE_W, BASE_H = 1080, 1737
W, H = BASE_W * SS, BASE_H * SS
CX, CY = W // 2, int(H * 0.50)
N = 24
OUT_DIR = "public/assets/agrumea"
PHOTO_DIR = "scripts/photos"

FRUITS = {
    "papaya":          {"photo": "papaya.jpg",   "arc": 360, "h_ratio": 0.62},
    "melone":          {"photo": "melon.jpg",    "arc": 360, "h_ratio": 0.58},
    "canna-zucchero":  {"photo": "cane.jpg",     "arc": 360, "h_ratio": 0.92},
    "rambutan":        {"photo": "rambutan.jpg", "arc": 360, "h_ratio": 0.60},
    "frutta-drago":    {"photo": "dragon.jpg",   "arc": 360, "h_ratio": 0.66},
}


def cutout(photo_path, cache_dir="scripts/photos/cutouts"):
    """rembg background removal, cached to disk."""
    os.makedirs(cache_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(photo_path))[0]
    dest = os.path.join(cache_dir, stem + ".png")
    if os.path.exists(dest):
        return Image.open(dest).convert("RGBA")
    img = Image.open(photo_path).convert("RGB")
    img = ImageOps.exif_transpose(img)
    # keep memory bounded (container RAM is limited): max 1024 px wide
    if img.width > 768:
        img = img.resize((768, int(img.height * 768 / img.width)), Image.LANCZOS)
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    try:
        import onnxruntime as ort
        so = ort.SessionOptions()
        so.intra_op_num_threads = 1
        so.inter_op_num_threads = 1
        session = new_session("u2net", providers=["CPUExecutionProvider"], sess_options=so)
    except (TypeError, Exception):
        session = new_session("u2net")
    res = remove(img, session=session, alpha_matting=False)
    res.save(dest)
    print("  cutout saved", dest)
    return res.convert("RGBA")


def trim(img):
    """Crop to the fruit's opaque region (alpha > 24), not stray shadow pixels."""
    a = np.asarray(img)[:, :, 3]
    ys, xs = np.where(a > 24)
    if len(ys) == 0:
        return img
    pad = 4
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad, img.height)
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad, img.width)
    return img.crop((x0, y0, x1, y1))


def render_turntable(cut, arc_deg, height_px):
    """Cylindrical wrap of `cut` rendered at 24 yaw angles (memory-lean:
    works at final canvas scale, one frame at a time)."""
    src = np.asarray(cut, dtype=np.float32)
    sh, sw = src.shape[:2]
    tex_w = max(sw, 64)
    pad = tex_w
    # keep texture float only where needed; store as uint8 to halve memory
    tex = np.concatenate([src[:, -pad:], src, src[:, :pad]], axis=1).astype(np.uint8)
    tex_h, tex_w_full = tex.shape[:2]
    off = pad

    frames = []
    for i in range(N):
        yaw = math.radians(i * 360.0 / N)
        aspect = sw / sh
        rx = min(int(height_px * aspect * 0.5), int(W * 0.42))
        ry = int(height_px * 0.5)

        ys, xs = np.mgrid[-ry:ry+1, -rx:rx+1].astype(np.float32)
        mask = (xs / max(rx, 1)) ** 2 + (ys / max(ry, 1)) ** 2 <= 1.0
        yy = np.clip(ys / max(ry, 1), -1, 1)
        xx = np.clip(xs / max(rx, 1), -1, 1)
        theta = np.arcsin(xx) + yaw
        u = ((theta / (2 * math.pi)) * tex_w) % tex_w + off
        v = (yy * 0.5 + 0.5) * (tex_h - 1)

        ui = np.clip(u.round().astype(np.int32), 0, tex_w_full - 1)
        vi = np.clip(v.round().astype(np.int32), 0, tex_h - 1)
        rgb = tex[vi, ui, :3].astype(np.float32)
        a = tex[vi, ui, 3].astype(np.float32) * mask.astype(np.float32)

        edge = np.sqrt(xx ** 2 + yy ** 2)
        shade = (1.0 - 0.35 * np.clip(edge, 0, 1) ** 2)[..., None]
        rgb = np.clip(rgb * shade, 0, 255).astype(np.uint8)

        frame = np.zeros((rgb.shape[0], rgb.shape[1], 4), np.uint8)
        frame[..., :3] = rgb
        frame[..., 3] = a.astype(np.uint8)
        img = Image.fromarray(frame, "RGBA").resize(
            (2 * rx * SS, 2 * ry * SS), Image.LANCZOS)
        del frame, rgb, a, ys, xs, mask, yy, xx, theta, u, v, ui, vi
        frames.append(img)
    return frames


def compose(fruit_img):
    """Place a rendered fruit (already at final scale x SS) on the 1080x1737
    canvas with a soft contact shadow. Memory-lean: shadow blurred at small size."""
    fw, fh = fruit_img.size
    # downscale fruit from SS-space to base-space first (keeps canvas small)
    fruit_small = fruit_img.resize((fw // SS, fh // SS), Image.LANCZOS)
    canvas = Image.new("RGBA", (BASE_W, BASE_H), (0, 0, 0, 0))
    cx, cy = BASE_W // 2, int(BASE_H * 0.50)
    sw_, sh_ = int(fruit_small.width * 0.42), max(int(fruit_small.width * 0.05), 6)
    shy = cy + fruit_small.height // 2 + sh_ // 2
    # small shadow strip -> blur only that strip
    strip_w, strip_h = 2 * sw_ + 40, 4 * sh_ + 40
    strip = Image.new("RGBA", (strip_w, strip_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(strip)
    d.ellipse([20, strip_h // 2 - sh_, strip_w - 20, strip_h // 2 + sh_],
              fill=(20, 16, 8, 90))
    strip = strip.filter(ImageFilter.GaussianBlur(9))
    canvas.alpha_composite(strip, (cx - strip_w // 2, shy - strip_h // 2))
    canvas.paste(fruit_small, (cx - fruit_small.width // 2, cy - fruit_small.height // 2), fruit_small)
    return canvas


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for slug, cfg in FRUITS.items():
        print("==", slug)
        photo = os.path.join(PHOTO_DIR, cfg["photo"])
        if not os.path.exists(photo):
            print("missing photo", photo); continue
        cut = trim(cutout(photo))
        height_px = int(BASE_H * cfg["h_ratio"] * SS)
        frames = render_turntable(cut, cfg["arc"], height_px)
        for i, fr in enumerate(frames):
            comp = compose(fr)
            name = f"fruit-{slug}-turn-{i:02d}.webp"
            comp.save(os.path.join(OUT_DIR, name), "WEBP", quality=82)
        # compatibility aliases
        compose(frames[0]).save(os.path.join(OUT_DIR, f"fruit-{slug}.webp"), "WEBP", quality=82)
        compose(frames[N // 2]).save(os.path.join(OUT_DIR, f"fruit-{slug}-side.webp"), "WEBP", quality=82)
        print("  wrote", N, "frames")
    print("done")


if __name__ == "__main__":
    main()
