#!/usr/bin/env python3
"""Generate the five tropical fruit jar models for the Agrumea clone.

Renders transparent 1080x1737 WebP jars (same canvas/aspect as the original
site assets in public/assets/agrumea) with procedurally drawn, botanically
recognisable fruit inside the glass column:

  - papaya            two longitudinal halves with cream seeds
  - melone            netted cantaloupe ball + cut wedge
  - canna-zucchero    jointed sugarcane stalk bundle with leaf blades
  - rambutan          cluster of red fruits with soft spines
  - frutta-drago      magenta oval with recurved green scales

Run:  python3 scripts/generate-jars.py
Requires: pip install pillow
"""
import math
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

W, H = 1080, 1737  # matches the original jar canvases (aspect ~0.62)
CX = W // 2
JAR_TOP = 250
BODY_W = 430
NECK_W = 260
SHOULDER_Y = JAR_TOP + 260
NECK_END_Y = JAR_TOP + 330
JAR_BOTTOM = H - 90
FILL_TOP = SHOULDER_Y + 130

OUT_DIR = "public/assets/agrumea"

FRUIT_COL = {
    "papaya": ((237, 158, 58), (201, 105, 25)),
    "melone": ((214, 224, 140), (124, 158, 60)),
    "canna-zucchero": ((126, 168, 86), (66, 110, 48)),
    "rambutan": ((214, 42, 52), (140, 15, 25)),
    "frutta-drago": ((232, 46, 110), (150, 10, 60)),
}


def jar_path():
    """Silhouette: screw band neck, sloped shoulders, straight body, rounded base."""
    p = []
    L, R = CX - NECK_W, CX + NECK_W
    BL, BR = CX - BODY_W, CX + BODY_W
    p += [(L + 30, JAR_TOP), (L, JAR_TOP + 26), (L, NECK_END_Y - 40)]
    for i in range(13):
        t = i / 12
        p.append((L + (BL - L) * (t**0.65), (NECK_END_Y - 40) + (SHOULDER_Y - (NECK_END_Y - 40)) * t))
    p += [(BL, SHOULDER_Y + 10), (BL, JAR_BOTTOM - 40)]
    for i in range(9):
        t = i / 8
        p.append((BL + 44 * (1 - math.cos(math.pi / 2 * t)), JAR_BOTTOM - 40 + 40 * math.sin(math.pi / 2 * t)))
    p += [(BR, JAR_BOTTOM - 40), (BR, SHOULDER_Y + 10)]
    for i in range(13):
        t = i / 12
        p.append((BR - (BR - R) * (t**0.65), SHOULDER_Y - (SHOULDER_Y - (NECK_END_Y - 40)) * t))
    p += [(R, NECK_END_Y - 40), (R, JAR_TOP + 26), (R - 30, JAR_TOP)]
    return p


PATH = jar_path()
INNER = [
    (CX - BODY_W + 24, SHOULDER_Y + 50),
    (CX + BODY_W - 24, SHOULDER_Y + 50),
    (CX + BODY_W - 24, JAR_BOTTOM - 34),
    (CX - BODY_W + 24, JAR_BOTTOM - 34),
]

_cmask = Image.new("L", (W, H), 0)
ImageDraw.Draw(_cmask).polygon(PATH, fill=255)
_inner = Image.new("L", (W, H), 0)
ImageDraw.Draw(_inner).polygon(INNER, fill=255)
CMASK = ImageChops.multiply(_cmask, _inner)  # content clipped to the glass belly


def draw_fruit(d, kind):
    rnd = random.Random(hash(kind) & 0xFFFF)
    c1, _ = FRUIT_COL[kind]

    def blob(x, y, r, a):
        d.ellipse([x - r, y - r, x + r, y + r], fill=a)

    if kind == "papaya":
        # two longitudinal halves showing the seed cavity
        for sx in (-150, 140):
            cx_, cy_ = CX + sx, FILL_TOP + 230
            d.rounded_rectangle([cx_ - 95, cy_ - 200, cx_ + 95, cy_ + 200], radius=95, fill=c1, outline=(170, 90, 20), width=5)
            d.rounded_rectangle([cx_ - 60, cy_ - 150, cx_ + 60, cy_ + 150], radius=60, fill=(250, 205, 110))
            for _ in range(60):
                bx = cx_ + rnd.uniform(-48, 48)
                by = cy_ + rnd.uniform(-120, 120)
                blob(bx, by, rnd.randint(9, 14), (245, 238, 215))
                blob(bx - 3, by - 3, rnd.randint(3, 5), (255, 255, 250))
        d.polygon([(CX - 30, FILL_TOP + 8), (CX + 80, FILL_TOP - 56), (CX + 8, FILL_TOP + 40)], fill=(70, 120, 50))

    elif kind == "melone":
        # netted cantaloupe sphere + a cut wedge
        mx, my, r = CX - 110, FILL_TOP + 250, 190
        blob(mx, my, r, (224, 168, 88))
        blob(mx, my, r - 14, (238, 190, 110))
        for i in range(14):
            y0 = my - r + i * (2 * r / 14)
            d.line([(mx - r + 8, y0), (mx + r - 8, y0 + 14)], fill=(196, 140, 70), width=4)
            x0 = mx - r + i * (2 * r / 14)
            d.line([(x0, my - r + 8), (x0 + 14, my + r - 8)], fill=(196, 140, 70), width=4)
        wx, wy = CX + 150, FILL_TOP + 240
        d.pieslice([wx - 160, wy - 160, wx + 160, wy + 160], 195, 300, fill=(250, 178, 96))
        d.pieslice([wx - 160, wy - 160, wx + 160, wy + 160], 195, 300, outline=(120, 160, 70), width=12)
        d.arc([wx - 130, wy - 130, wx + 130, wy + 130], 195, 300, fill=(255, 225, 180), width=8)

    elif kind == "canna-zucchero":
        # bundle of jointed sugarcane stalks with leaf blades on top
        for sx, ln in ((-240, 560), (-120, 660), (0, 720), (120, 660), (240, 560)):
            bx = CX + sx
            top = FILL_TOP + 120 + (720 - ln)
            seg = 100
            n = int(ln // seg) + 1
            for s in range(n):
                y0 = top - s * seg
                y1 = max(y0 - seg + 14, FILL_TOP + 300)
                if y1 >= y0:
                    continue
                d.rounded_rectangle(
                    [bx - 36, y1, bx + 36, y0],
                    radius=20,
                    fill=(150, 182, 96) if s % 2 == 0 else (132, 166, 82),
                    outline=(84, 116, 52),
                    width=5,
                )
                d.line([(bx - 36, y0 - 14), (bx + 36, y0 - 14)], fill=(96, 128, 60), width=7)
            d.polygon([(bx, top), (bx + 70, top - 100), (bx + 12, top - 8)], fill=(90, 140, 60))
            d.polygon([(bx, top), (bx - 64, top - 96), (bx - 10, top - 8)], fill=(76, 124, 52))

    elif kind == "rambutan":
        # cluster of red fruits covered in soft spines
        spots = [(-200, FILL_TOP + 260, 120), (-40, FILL_TOP + 190, 135), (130, FILL_TOP + 270, 115), (-100, FILL_TOP + 420, 100), (80, FILL_TOP + 430, 95)]
        for sx, sy, r in spots:
            cx_, cy_ = CX + sx, sy
            blob(cx_, cy_, r, (206, 32, 42))
            blob(cx_ - r // 5, cy_ - r // 5, int(r * 0.72), (226, 58, 60))
            for a in range(0, 360, 12):
                ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
                ex, ey = cx_ + int((r + 26) * ca), cy_ + int((r + 26) * sa)
                d.line([(cx_ + int(r * 0.5 * ca), cy_ + int(r * 0.5 * sa)), (ex, ey)], fill=(150, 18, 26), width=9)
                blob(ex, ey, 7, (224, 120, 40))
        d.polygon([(CX + 4, FILL_TOP + 70), (CX + 90, FILL_TOP - 14), (CX + 22, FILL_TOP + 96)], fill=(70, 118, 52))

    elif kind == "frutta-drago":
        # magenta oval with recurved green scales + smaller companion fruit
        cx_, cy_ = CX - 70, FILL_TOP + 280
        d.ellipse([cx_ - 140, cy_ - 230, cx_ + 140, cy_ + 230], fill=(228, 44, 108), outline=(170, 16, 72), width=7)
        d.ellipse([cx_ - 90, cy_ - 170, cx_ + 70, cy_ + 150], fill=(240, 86, 138))
        for ang, ln in ((-125, 140), (-65, 150), (0, 140), (65, 150), (125, 140)):
            px = cx_ + int(132 * math.cos(math.radians(ang)))
            py = cy_ + int(220 * math.sin(math.radians(ang)))
            tx = px + int(ln * math.cos(math.radians(ang - 42)))
            ty = py + int(ln * math.sin(math.radians(ang - 42)))
            qx = px + int(34 * math.cos(math.radians(ang + 55)))
            qy = py + int(34 * math.sin(math.radians(ang + 55)))
            d.polygon([(px, py), (tx, ty), (qx, qy)], fill=(104, 168, 72))
        cx2, cy2 = CX + 190, FILL_TOP + 420
        d.ellipse([cx2 - 88, cy2 - 130, cx2 + 88, cy2 + 130], fill=(214, 32, 96))
        for ang in (-110, -50, 10, 70, 130):
            px = cx2 + int(82 * math.cos(math.radians(ang)))
            py = cy2 + int(122 * math.sin(math.radians(ang)))
            d.polygon(
                [
                    (px, py),
                    (px + int(56 * math.cos(math.radians(ang - 45))), py + int(56 * math.sin(math.radians(ang - 45)))),
                    (px + 16, py + 16),
                ],
                fill=(96, 160, 66),
            )


def paste_masked(base, layer, mask):
    out = base.copy()
    out.paste(layer.convert("RGB"), (0, 0), mask)
    return out


def build(kind, out_path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # --- fruit content, clipped to the glass belly ---
    fruit = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_fruit(ImageDraw.Draw(fruit), kind)
    fruit = fruit.filter(ImageFilter.GaussianBlur(2))
    fa = ImageChops.multiply(fruit.split()[3], CMASK)
    img = paste_masked(img, fruit, fa)

    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([0, JAR_BOTTOM - 170, W, H], fill=(30, 10, 0, 70))
    img = paste_masked(img, sh, ImageChops.multiply(sh.split()[3], CMASK))

    # --- glass tint + silhouette edge ---
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gl)
    gd.polygon(PATH, fill=(236, 244, 248, 64))
    outline = PATH + [PATH[0]]
    gd.line(outline, fill=(110, 132, 144, 200), width=9, joint="curve")
    gd.line(outline, fill=(250, 252, 253, 120), width=3, joint="curve")
    img = Image.alpha_composite(img, gl)

    hl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hl)
    hd.rounded_rectangle([CX - BODY_W + 50, SHOULDER_Y + 90, CX - BODY_W + 110, JAR_BOTTOM - 90], radius=55, fill=(255, 255, 255, 110))
    hd.rounded_rectangle([CX + BODY_W - 100, SHOULDER_Y + 140, CX + BODY_W - 64, JAR_BOTTOM - 150], radius=34, fill=(255, 255, 255, 64))
    hlm = hl.copy()
    hlm.putalpha(ImageChops.multiply(hl.split()[3], CMASK))
    img = Image.alpha_composite(img, hlm)

    # --- metal screw band + lid ---
    mt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(mt)
    bt, bb = JAR_TOP, JAR_TOP + 120
    md.rounded_rectangle([CX - NECK_W - 14, bt, CX + NECK_W + 14, bb], radius=26, fill=(196, 198, 202))
    md.rounded_rectangle([CX - NECK_W - 14, bt, CX + NECK_W + 14, bb - 64], radius=26, fill=(224, 226, 230))
    for x in range(CX - NECK_W, CX + NECK_W + 1, 34):
        md.line([(x, bt + 10), (x, bb - 10)], fill=(168, 170, 176), width=7)
    md.rounded_rectangle([CX - NECK_W + 30, bt - 30, CX + NECK_W - 30, bt + 16], radius=16, fill=(240, 242, 244))
    img = Image.alpha_composite(img, mt)

    # --- coloured shrink band on the neck (product accent colour) ---
    nb = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(nb)
    c1, _ = FRUIT_COL[kind]
    nd.rounded_rectangle([CX - NECK_W - 4, bb - 14, CX + NECK_W + 4, SHOULDER_Y - 90], radius=34, fill=c1 + (255,))
    nd.rounded_rectangle(
        [CX - NECK_W - 4, bb - 14, CX + NECK_W + 4, bb + 40],
        radius=34,
        fill=tuple(min(255, v + 30) for v in c1) + (255,),
    )
    img = Image.alpha_composite(img, nb)

    # --- ground shadow ---
    ds = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ds).ellipse([CX - 330, JAR_BOTTOM - 8, CX + 330, JAR_BOTTOM + 58], fill=(0, 0, 0, 45))
    ds = ds.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(ds, img)

    img.save(out_path, "WEBP", quality=92)
    print("wrote", out_path)


if __name__ == "__main__":
    import os

    for k in FRUIT_COL:
        build(k, os.path.join(OUT_DIR, f"jar-{k}.webp"))
