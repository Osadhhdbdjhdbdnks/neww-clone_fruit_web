#!/usr/bin/env python3
"""Render the five REAL FRUITS as 360-degree turntable sprite sheets.

Instead of a single mirrored "back" image, every fruit is drawn inside a
virtual cylinder and rendered at 24 yaw angles (0..352.5 deg).  Each frame is
generated procedurally from the fruit's own geometry:

  * papaya          - oblate melon-shaped body, yellow-green skin shading that
                      slides across the surface as it turns; stem scar and a
                      blossom tip orbit with the yaw.
  * melone          - netted cantaloupe sphere; the crosshatched netting and a
                      curly stem are painted in cylindrical coordinates so the
                      pattern visibly wraps around the ball while spinning.
  * canna-zucchero  - a sheaf of five jointed sugarcane stalks standing on a
                      circle; stalks swap draw order when they pass behind /
                      in front of each other, nodes, rind gradients and crown
                      leaves all follow the true 3D projection.
  * rambutan        - red hairy ball whose soft spines are projected from
                      spherical directions; spines pointing away from the
                      camera are hidden, giving a genuine rotating tuft.
  * frutta-drago    - magenta oval body carrying eight recurved green scales
                      placed around its silhouette; scales on the far side are
                      drawn first (behind), near-side scales overlap the body.

Outputs (public/assets/agrumea):
  fruit-<slug>.webp            front view           (1080 x 1737, transparent)
  fruit-<slug>-side.webp       back view (yaw 180)  (kept for compatibility)
  fruit-<slug>-turn-{i}.webp   24 frames, i = 0..23, yaw = i * 15 deg

Canvas geometry matches the slider (jar-slider.tsx): 1080 x 1737 canvas,
content centred in the same art box the old jar assets used.

Run:  python3 scripts/render-fruits.py     (requires: pip install pillow numpy)
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SS = 2  # supersampling factor
BASE_W, BASE_H = 1080, 1737
W, H = BASE_W * SS, BASE_H * SS
CX, CY = W // 2, H // 2
BOX_W, BOX_H = 995 * SS, 1600 * SS
OUT_DIR = "public/assets/agrumea"
N_FRAMES = 24
STEP = 360.0 / N_FRAMES


def sc(*pts):
    """design space (1080x1737) -> supersampled canvas coords"""
    return [(p[0] * SS, p[1] * SS) for p in pts]


def ell(d, cx, cy, rx, ry, fill=None, outline=None, width=1):
    if fill is not None:
        d.ellipse([cx * SS - rx * SS, cy * SS - ry * SS, cx * SS + rx * SS, cy * SS + ry * SS], fill=fill)
    if outline is not None:
        d.ellipse([cx * SS - rx * SS, cy * SS - ry * SS, cx * SS + rx * SS, cy * SS + ry * SS],
                  outline=outline, width=width * SS)


def poly(d, pts, fill):
    d.polygon(sc(*pts), fill=fill)


def line(d, pts, fill, width):
    d.line(sc(*pts), fill=fill, width=width * SS)


def arc(d, cx, cy, rx, ry, a0, a1, fill, width):
    d.arc([cx * SS - rx * SS, cy * SS - ry * SS, cx * SS + rx * SS, cy * SS + ry * SS],
          a0, a1, fill=fill, width=width * SS)


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


# ---------------------------------------------------------------- papaya ----
def render_papaya(yaw):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = 540, 870
    rx, ry = 330, 470
    y = math.radians(yaw)
    sx = math.sin(y)  # stem horizontal offset (-1 .. 1)

    skin_dark = (176, 132, 44)
    skin_mid = (226, 176, 66)
    skin_hi = (250, 214, 116)
    ell(d, cx, cy, rx, ry, fill=skin_dark)
    ell(d, cx, cy, rx - 14, ry - 14, fill=skin_mid)
    # specular highlight sliding opposite the stem as the fruit turns
    hx = cx - 110 - 150 * sx
    ell(d, hx, cy - 150, 150, 240, fill=skin_hi)
    ell(d, hx - 30, cy - 230, 80, 130, fill=(255, 232, 158))
    # subtle longitudinal ribs
    for k in (-1, 0, 1):
        rib_x = cx + k * 120 - 60 * sx
        arc(d, rib_x, cy, 40, ry - 30, 300, 60, fill=(212, 158, 56), width=5)
    # freckles
    rng = np.random.default_rng(11)
    for _ in range(70):
        fx = rng.uniform(cx - rx + 40, cx + rx - 40)
        fy = rng.uniform(cy - ry + 60, cy + ry - 60)
        if ((fx - cx) / rx) ** 2 + ((fy - cy) / ry) ** 2 > 0.92:
            continue
        dr = rng.integers(2, 5)
        ell(d, fx, fy, dr, dr, fill=(196, 140, 48))
    # stem scar orbits with yaw
    stx = cx + sx * 235
    sty = cy - ry + 34 - abs(sx) * 26
    ell(d, stx, sty, 40, 26, fill=(96, 128, 60))
    ell(d, stx, sty, 26, 15, fill=(128, 160, 84))
    line(d, [(stx, sty - 8), (stx + 18 * sx, sty - 74)], fill=(92, 128, 58), width=16)
    # blossom tip at the bottom
    blx = cx - sx * 250
    bly = cy + ry - 26 - abs(sx) * 18
    ell(d, blx, bly, 26, 20, fill=(150, 104, 36))
    return img


# ---------------------------------------------------------------- melon ----
def render_melone(yaw):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy, r = 540, 880, 420
    y = math.radians(yaw)

    ell(d, cx, cy, r, r, fill=(150, 168, 84))
    ell(d, cx, cy, r - 12, r - 12, fill=(214, 198, 116))
    ell(d, cx - 120, cy - 140, 190, 210, fill=(238, 224, 148))

    # netting painted in cylindrical coords: vertical meridians
    for m in range(12):
        lon = math.radians(m * 30)
        phase = lon + y
        px = math.sin(phase)
        depth = math.cos(phase)
        if depth <= 0.02:
            continue
        wdt = 3 + 5 * depth
        alpha = int(120 * depth + 40)
        col = (150, 136, 70, alpha)
        xs = cx + px * r * 0.94
        span = r * 0.97 * abs(depth) ** 0.5
        arc(d, xs, cy, max(6, span * 0.22), r - 14, 90, 270, fill=col, width=int(wdt))
    # latitude rings
    for la in range(-3, 4):
        lat = math.radians(la * 24)
        ring_r = r * math.cos(lat) * 0.95
        ring_y = cy - r * math.sin(lat)
        squish = max(8, ring_r * 0.16)
        arc(d, cx, ring_y, ring_r, squish, 180, 360, fill=(168, 152, 82, 150), width=5)
        arc(d, cx, ring_y, ring_r, squish, 0, 180, fill=(186, 172, 104, 90), width=4)

    # curly stem anchored near the top pole, orbits with yaw
    stx = cx + math.sin(y) * 120
    sty = cy - r + 26 - abs(math.cos(y)) * 6
    line(d, [(stx, sty), (stx + 10, sty - 60), (stx + 46, sty - 96)], fill=(110, 88, 48), width=18)
    arc(d, stx + 70, sty - 96, 34, 26, 0, 300, fill=(122, 150, 70), width=8)
    # small leaf at the stem
    lx = stx + 96
    poly(d, [(lx, sty - 70), (lx + 120, sty - 130), (lx + 150, sty - 60), (lx + 40, sty - 20)], fill=(96, 148, 64))
    line(d, [(lx + 8, sty - 52), (lx + 140, sty - 92)], fill=(140, 180, 96), width=4)
    return img


# ------------------------------------------------------------- sugarcane ----
def render_cane(yaw):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y = math.radians(yaw)
    base_y = 1430
    radius = 235
    stalks = []
    for i in range(5):
        ang = math.radians(i * 72 + 15)
        depth = math.cos(ang + y)
        horiz = math.sin(ang + y)
        bx = 540 + horiz * radius
        ln = 760 + 70 * math.cos(i * 2.1)
        stalks.append((depth, bx, ln, i))
    stalks.sort(key=lambda s: s[0])  # far stalks first

    for depth, bx, ln, idx in stalks:
        shade = 0.55 + 0.45 * (depth + 1) / 2  # nearer stalks brighter
        w = 34 + 6 * depth
        top_y = base_y - ln
        tilt = (bx - 540) * 0.10
        seg = 118
        n = max(2, int(ln // seg))
        for s in range(n):
            t0, t1 = s / n, (s + 1) / n
            yy0, yy1 = base_y - ln * t0, base_y - ln * t1
            xx0, xx1 = bx + tilt * t0, bx + tilt * t1
            g = int(255 * shade)
            r0 = (int(150 * shade), int(190 * shade), int(96 * shade))
            r1 = (int(124 * shade), int(166 * shade), int(80 * shade))
            col = r0 if s % 2 == 0 else r1
            poly(d, [(xx0 - w, yy0), (xx0 + w, yy0), (xx1 + w * 0.86, yy1), (xx1 - w * 0.86, yy1)], fill=col)
            # waxy bloom stripe
            line(d, [(xx0 - w * 0.35, yy0), (xx1 - w * 0.35, yy1)],
                 fill=(min(255, int(216 * shade) + 20), min(255, int(234 * shade) + 16), min(255, int(168 * shade))), width=9)
            # node ring
            ell(d, xx1, yy1, w * 0.95, 9, fill=(int(86 * shade), int(120 * shade), int(56 * shade)))
            ell(d, xx1, yy1 - 6, w * 0.8, 7, fill=(int(200 * shade), int(218 * shade), int(142 * shade)))
        # crown leaves
        tx, ty = bx + tilt, top_y
        for la, ll, lw in ((58, 300, 26), (95, 350, 30), (132, 270, 24)):
            a = math.radians(la)
            ex = tx + ll * math.cos(a) * (0.7 + 0.3 * depth)
            ey = ty - ll * math.sin(a)
            mx = tx + ll * 0.5 * math.cos(a) - ll * 0.14 * math.sin(a)
            my = ty - ll * 0.5 * math.sin(a) - ll * 0.14 * math.cos(a)
            mx2 = tx + ll * 0.5 * math.cos(a) + ll * 0.05 * math.sin(a)
            my2 = ty - ll * 0.5 * math.sin(a) + ll * 0.05 * math.cos(a)
            g = int(255 * shade)
            poly(d, [(tx, ty), (mx, my), (ex, ey), (mx2, my2)],
                 fill=(int(92 * shade), int(146 * shade), int(60 * shade)))
    return img


# -------------------------------------------------------------- rambutan ----
def render_rambutan(yaw):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy, r = 540, 880, 380
    y = math.radians(yaw)

    # spines: spherical directions, only those facing the camera are drawn
    rng = np.random.default_rng(7)
    dirs = rng.normal(size=(240, 3))
    dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
    rot = np.array([[math.cos(y), 0, math.sin(y)], [0, 1, 0], [-math.sin(y), 0, math.cos(y)]])
    spines = []
    for v in dirs:
        w = rot @ v
        if w[2] < 0.12:
            continue
        spines.append(w)
    spines.sort(key=lambda w: w[2])  # rim spines first, centre last
    for w in spines:
        depth = w[2]
        px, py = cx + w[0] * r * depth, cy - w[1] * r * depth
        dx, dy = w[0], -w[1]
        nn = math.hypot(dx, dy) or 1
        dx, dy = dx / nn, dy / nn
        bx, by = cx + w[0] * r * 0.92, cy - w[1] * r * 0.92
        ln = 70 + 40 * depth
        ex, ey = bx + dx * ln, by + dy * ln
        mx, my = bx + dx * ln * 0.5 - dy * 12, by + dy * ln * 0.5 + dx * 12
        col = mix((150, 24, 34), (214, 46, 58), depth)
        poly(d, [(bx - dy * 6, by + dx * 6), (mx, my), (bx + dy * 6, by - dx * 6), (ex, ey)], fill=col + (255,))
        ell(d, ex, ey, 7, 7, fill=mix((196, 90, 40), (236, 132, 52), depth) + (255,))

    ell(d, cx, cy, r, r, fill=(142, 16, 26))
    ell(d, cx, cy, r - 14, r - 14, fill=(216, 44, 54))
    hl = cx - 120 - 90 * math.sin(y)
    ell(d, hl, cy - 130, 150, 170, fill=(240, 92, 88))
    ell(d, hl - 40, cy - 190, 70, 84, fill=(250, 130, 122))
    # a few near-side spine roots overlapping the body edge
    for w in spines[-40:]:
        px, py = cx + w[0] * r * 0.99, cy - w[1] * r * 0.99
        ell(d, px, py, 9, 9, fill=(184, 30, 40))
    # stem
    stx = cx + math.sin(y) * 150
    ell(d, stx, cy - r + 10, 30, 22, fill=(110, 78, 44))
    line(d, [(stx, cy - r - 6), (stx + 30 * math.sin(y), cy - r - 70)], fill=(110, 78, 44), width=16)
    return img


# ---------------------------------------------------------- dragonfruit ----
def render_dragon(yaw):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = 540, 880
    rx, ry = 300, 470
    y = math.radians(yaw)

    scales = []
    for i in range(8):
        ang = math.radians(i * 45 + 22)
        depth = math.cos(ang + y)
        horiz = math.sin(ang + y)
        sy = -math.cos(ang) * 0.82  # fixed vertical placement around body
        px = cx + horiz * rx * 0.92
        py = cy + sy * ry * 0.86
        out = 1 if horiz >= 0 else -1
        scales.append((depth, px, py, out, horiz))

    def scale_shape(px, py, out, depth, ln=250):
        tipx = px + out * ln * 0.62
        tipy = py - ln * 0.55 - depth * 20
        b1 = (px + out * 18, py - 58)
        b2 = (px + out * 18, py + 58)
        ctrl = (px + out * ln * 0.42, py - ln * 0.66)
        col = mix((66, 118, 46), (120, 182, 82), (depth + 1) / 2)
        poly(d, [b1, ctrl, (tipx, tipy), ctrl, b2], fill=col)
        poly(d, [(px + out * 10, py - 34), (px + out * ln * 0.3, py - ln * 0.4),
                 (px + out * 10, py + 34)], fill=mix(col, (170, 214, 120), 0.5))

    # far-side scales behind the body
    for depth, px, py, out, horiz in sorted(scales, key=lambda s: s[0]):
        if depth <= 0:
            scale_shape(px, py, out, depth, ln=210)

    ell(d, cx, cy, rx, ry, fill=(152, 12, 62))
    ell(d, cx, cy, rx - 16, ry - 16, fill=(232, 46, 110))
    hx = cx - 100 - 120 * math.sin(y)
    ell(d, hx, cy - 150, 130, 220, fill=(244, 96, 148))
    ell(d, hx - 30, cy - 230, 60, 110, fill=(250, 130, 170))

    # near-side scales in front
    for depth, px, py, out, horiz in sorted(scales, key=lambda s: s[0], reverse=True):
        if depth > 0:
            scale_shape(px, py, out, depth)

    # top opening
    tox = cx + math.sin(y) * 60
    ell(d, tox, cy - ry + 24, 44, 22, fill=(108, 158, 72))
    return img


RENDERERS = {
    "papaya": render_papaya,
    "melone": render_melone,
    "canna-zucchero": render_cane,
    "rambutan": render_rambutan,
    "frutta-drago": render_dragon,
}


def finish(img):
    """ground shadow + clip to the slider art box + downscale."""
    img = img.filter(ImageFilter.GaussianBlur(1.2 * SS))
    box_mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(box_mask).rounded_rectangle(
        [CX - BOX_W // 2, CY - BOX_H // 2, CX + BOX_W // 2, CY + BOX_H // 2],
        radius=80 * SS, fill=255)
    alpha = Image.composite(img.split()[3], Image.new("L", (W, H), 0), box_mask)
    img.putalpha(alpha)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse(
        [CX - 360 * SS, CY + 690 * SS, CX + 360 * SS, CY + 770 * SS], fill=(0, 0, 0, 42))
    sh = sh.filter(ImageFilter.GaussianBlur(22 * SS))
    img = Image.alpha_composite(sh, img)
    return img.resize((BASE_W, BASE_H), Image.LANCZOS)


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    for kind, fn in RENDERERS.items():
        frames = [finish(fn(int(i * STEP))) for i in range(N_FRAMES)]
        for i, fr in enumerate(frames):
            fr.save(os.path.join(OUT_DIR, f"fruit-{kind}-turn-{i:02d}.webp"), "WEBP", quality=90)
        frames[0].save(os.path.join(OUT_DIR, f"fruit-{kind}.webp"), "WEBP", quality=92)
        frames[N_FRAMES // 2].save(os.path.join(OUT_DIR, f"fruit-{kind}-side.webp"), "WEBP", quality=92)
        print("wrote", kind, len(frames) + 2, "assets")
