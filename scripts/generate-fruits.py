#!/usr/bin/env python3
"""Generate the five real tropical FRUIT models for the Agrumea clone.

No jars, no glass, no lids, no paper labels: each asset is the fruit itself —
papaya, cantaloupe melon, sugarcane, rambutan and dragon fruit — drawn as a
botanically recognisable, softly shaded composition on a transparent canvas.

Output matches the slider's geometry expectations:
  - canvas 1080 x 1737 (aspect = ASPECT constant in jar-slider.tsx)
  - content sits inside a centred box of aspect 630/1013 (the same box the
    original site's jar images used), so slot sizing / parallax stay intact
  - transparent WebP, saved to public/assets/agrumea/fruit-<slug>.webp

Run:  python3 scripts/generate-fruits.py
Requires: pip install pillow
"""
import math
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

W, H = 1080, 1737
CX, CY = W // 2, H // 2
BOX_W, BOX_H = 995, 1600  # centred art box (same footprint as old jar assets)
OUT_DIR = "public/assets/agrumea"

FRUITS = {
    "papaya": ((240, 165, 62), (196, 104, 26)),
    "melone": ((222, 205, 120), (128, 160, 66)),
    "canna-zucchero": ((140, 180, 92), (72, 116, 50)),
    "rambutan": ((216, 44, 54), (142, 16, 26)),
    "frutta-drago": ((232, 46, 110), (152, 12, 62)),
}


def new_canvas():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def shade(d, bbox, hi, lo):
    """Radial highlight + rim shading over an already-filled shape region."""
    pass  # (shading handled per-fruit with layered ellipses)


def draw_papaya(d, rnd):
    c1, c2 = FRUITS["papaya"]
    # whole fruit behind (left), with stem
    wx, wy, rw, rh = CX - 250, CY + 60, 175, 330
    d.ellipse([wx - rw, wy - rh, wx + rw, wy + rh], fill=c2)
    d.ellipse([wx - rw + 26, wy - rh + 30, wx + rw - 34, wy + rh - 40], fill=c1)
    d.ellipse([wx - rw + 60, wy - rh + 70, wx - 20, wy - 40], fill=(252, 205, 110))
    d.polygon([(wx - 14, wy - rh + 6), (wx + 20, wy - rh - 66), (wx + 34, wy - rh - 60), (wx + 6, wy - rh + 12)], fill=(92, 128, 58))

    # front longitudinal half showing seed cavity
    fx, fy, fw, fh = CX + 90, CY + 40, 235, 480
    d.ellipse([fx - fw, fy - fh, fx + fw, fy + fh], fill=(176, 92, 22))
    d.ellipse([fx - fw + 16, fy - fh + 18, fx + fw - 16, fy + fh - 18], fill=c1)
    d.ellipse([fx - fw + 46, fy - fh + 60, fx + fw - 60, fy + fh - 60], fill=(250, 196, 96))
    # seed cavity
    d.ellipse([fx - 110, fy - 300, fx + 110, fy + 330], fill=(206, 128, 40))
    d.ellipse([fx - 92, fy - 278, fx + 92, fy + 308], fill=(226, 158, 62))
    for _ in range(130):
        bx = fx + rnd.uniform(-78, 78)
        by = fy + rnd.uniform(-262, 292)
        if (bx - fx) ** 2 / 82**2 + (by - fy) ** 2 / 280**2 > 1:
            continue
        r = rnd.randint(13, 20)
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=(246, 238, 214))
        d.ellipse([bx - r * 0.45, by - r * 0.55, bx + r * 0.3, by + r * 0.1], fill=(255, 253, 246))
    # leaf
    d.polygon([(fx + 40, fy - fh + 20), (fx + 190, fy - fh - 130), (fx + 120, fy - fh + 46)], fill=(76, 126, 54))


def draw_melone(d, rnd):
    c1, c2 = FRUITS["melone"]
    mx, my, r = CX - 90, CY + 40, 380
    # netted cantaloupe sphere
    d.ellipse([mx - r, my - r, mx + r, my + r], fill=(150, 168, 84))
    d.ellipse([mx - r + 14, my - r + 14, mx + r - 14, my + r - 14], fill=(206, 190, 108))
    d.ellipse([mx - r + 70, my - r + 60, mx + 40, my - 60], fill=(236, 220, 140))
    # netting: crosshatched arcs clipped to the ball
    net = new_canvas()
    nd = ImageDraw.Draw(net)
    for i in range(-6, 7):
        off = i * 62
        nd.arc([mx - r + abs(off), my - r, mx + r + abs(off) * 0, my + r] if False else [mx - r, my - r + off - 40, mx + r, my + r + off - 40], 180, 360, fill=(172, 156, 84), width=6)
        nd.line([(mx - r + 20 + i * 60, my - r + 30), (mx - r + 60 + i * 60, my + r - 30)], fill=(172, 156, 84), width=6)
    for k in range(-8, 9):
        nd.line([(mx - r, my + k * 46), (mx + r, my + k * 46 + 60)], fill=(186, 170, 96), width=5)
        nd.line([(mx + k * 46, my - r), (mx + k * 46 + 60, my + r)], fill=(186, 170, 96), width=5)
    mask = new_canvas()
    ImageDraw.Draw(mask).ellipse([mx - r + 6, my - r + 6, mx + r - 6, my + r - 6], fill=(255, 255, 255, 255))
    net.putalpha(ImageChops.multiply(net.split()[3], mask.split()[3]))
    return net  # composited by caller

def draw_cane_leaf(d, bx, by, ln, ang, col):
    a = math.radians(ang)
    ex, ey = bx + ln * math.cos(a), by - ln * math.sin(a)
    mx1, my1 = bx + ln * 0.5 * math.cos(a) - ln * 0.16 * math.sin(a), by - ln * 0.5 * math.sin(a) - ln * 0.16 * math.cos(a)
    mx2, my2 = bx + ln * 0.5 * math.cos(a) + ln * 0.06 * math.sin(a), by - ln * 0.5 * math.sin(a) + ln * 0.06 * math.cos(a)
    d.polygon([(bx, by), (mx1, my1), (ex, ey), (mx2, my2)], fill=col)


def draw_sugarcane(d, rnd):
    c1, c2 = FRUITS["canna-zucchero"]
    stalks = [(-300, 620, -7), (-160, 760, -3), (0, 830, 0), (160, 740, 4), (300, 600, 8)]
    for sx, ln, tilt in stalks:
        bx = CX + sx
        base_y = CY + 560
        top_y = base_y - ln
        dx = tilt * 9
        seg = 118
        n = max(2, int(ln // seg))
        for s in range(n):
            t0 = s / n
            t1 = (s + 1) / n
            y0 = base_y - ln * t0
            y1 = base_y - ln * t1
            x0 = bx + dx * t0
            x1 = bx + dx * t1
            wcol = (154, 188, 100) if s % 2 == 0 else (128, 164, 82)
            d.polygon([(x0 - 34, y0), (x0 + 34, y0), (x1 + 30, y1), (x1 - 30, y1)], fill=wcol)
            d.line([(x1 - 30, y1), (x1 + 30, y1)], fill=(86, 120, 56), width=9)
            d.polygon([(x1 - 30, y1 - 4), (x1 + 30, y1 - 4), (x1 + 26, y1 - 16), (x1 - 26, y1 - 16)], fill=(196, 214, 140))
        # waxy bloom stripe
        d.line([(bx - 12 + dx * 0.1, base_y - ln * 0.1), (bx - 10 + dx * 0.9, base_y - ln * 0.9)], fill=(214, 232, 168), width=10)
        # crown leaves
        ty = base_y - ln
        tx = bx + dx
        draw_cane_leaf(d, tx, ty, 300, 62, (96, 148, 64))
        draw_cane_leaf(d, tx, ty, 340, 96, (78, 130, 54))
        draw_cane_leaf(d, tx, ty, 260, 128, (110, 160, 74))
    # cut chunk in front
    qx, qy = CX + 40, CY + 470
    d.ellipse([qx - 150, qy - 60, qx + 150, qy + 60], fill=(96, 132, 62))
    d.ellipse([qx - 138, qy - 50, qx + 138, qy + 50], fill=(232, 240, 200))
    d.ellipse([qx - 118, qy - 36, qx + 118, qy + 36], fill=(246, 250, 222))
    for a in range(0, 360, 30):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        d.line([(qx + 20 * ca, qy + 8 * sa), (qx + 110 * ca, qy + 32 * sa)], fill=(206, 216, 166), width=4)


def draw_rambutan(d, rnd):
    c1, c2 = FRUITS["rambutan"]
    spots = [(-235, CY - 250, 150), (60, CY - 330, 165), (255, CY - 40, 140), (-120, CY + 120, 185), (150, CY + 330, 130), (-280, CY + 350, 115)]
    for sx, sy, r in spots:
        cx_, cy_ = CX + sx, sy
        # soft spines first (behind body)
        for a in range(0, 360, 9):
            ca, sa = math.cos(math.radians(a + rnd.randint(-3, 3))), math.sin(math.radians(a))
            bx, by = cx_ + (r - 12) * ca, cy_ + (r - 12) * sa
            ex, ey = cx_ + (r + 46) * ca, cy_ + (r + 46) * sa
            mx, my = cx_ + (r + 20) * ca - 14 * sa, cy_ + (r + 20) * sa + 14 * ca
            d.polygon([(bx - 6 * sa, by + 6 * ca), (mx, my), (bx + 6 * sa, by - 6 * ca), (ex, ey)], fill=(196, 34, 44))
            dr = 8
            d.ellipse([ex - dr, ey - dr, ex + dr, ey + dr], fill=(228, 118, 44))
        d.ellipse([cx_ - r, cy_ - r, cx_ + r, cy_ + r], fill=c2)
        d.ellipse([cx_ - r + 12, cy_ - r + 12, cx_ + r - 12, cy_ + r - 12], fill=c1)
        hl = int(r * 0.42)
        d.ellipse([cx_ - hl - r * 0.3, cy_ - hl - r * 0.35, cx_ + hl * 0.2, cy_ + hl * 0.1], fill=(242, 96, 92))
    # stem branch connecting the cluster
    d.line([(CX - 60, CY - 470), (CX + 120, CY - 520)], fill=(110, 78, 44), width=22)


def draw_dragonfruit(d, rnd):
    c1, c2 = FRUITS["frutta-drago"]
    cx_, cy_, rx, ry = CX - 40, CY + 30, 300, 470
    # recurved green scales (drawn behind + around the body)
    def scale(px, py, ang, ln, col):
        a = math.radians(ang)
        tipx = px + ln * math.cos(a)
        tipy = py - ln * math.sin(a)
        b1 = (px + 52 * math.cos(a + 1.4), py - 52 * math.sin(a + 1.4))
        b2 = (px + 52 * math.cos(a - 1.4), py - 52 * math.sin(a - 1.4))
        ctrl = (px + ln * 0.55 * math.cos(a) - 60 * math.sin(a), py - ln * 0.55 * math.sin(a) - 60 * math.cos(a))
        d.polygon([b1, ctrl, (tipx, tipy), b2], fill=col)

    back = [( -160, -330, 118, 250), (150, -320, 62, 250), (-250, -80, 150, 280), (250, -60, 30, 280),
            (-230, 200, 205, 270), (235, 220, -25, 270), (-120, 400, 235, 240), (130, 410, -55, 240)]
    for sx, sy, ang, ln in back:
        scale(cx_ + sx, cy_ + sy, ang, ln, (88, 148, 60))

    d.ellipse([cx_ - rx, cy_ - ry, cx_ + rx, cy_ + ry], fill=c2)
    d.ellipse([cx_ - rx + 18, cy_ - ry + 18, cx_ + rx - 18, cy_ + ry - 18], fill=c1)
    d.ellipse([cx_ - rx + 60, cy_ - ry + 80, cx_ - 40, cy_ - 40], fill=(244, 96, 148))

    front = [(-200, -210, 128, 230), (190, -230, 52, 230), (-250, 40, 168, 250), (255, 60, 12, 250),
             (-170, 300, 226, 220), (180, 310, -46, 220), (0, -430, 90, 210)]
    for sx, sy, ang, ln in front:
        scale(cx_ + sx, cy_ + sy, ang, ln, (112, 176, 76))
        scale(cx_ + sx * 0.94, cy_ + sy * 0.94, ang, ln * 0.72, (146, 200, 98))
    # small companion fruit
    c2x, c2y = CX + 300, CY + 430
    d.ellipse([c2x - 130, c2y - 200, c2x + 130, c2y + 200], fill=c2)
    d.ellipse([c2x - 112, c2y - 182, c2x + 112, c2y + 182], fill=c1)
    for ang, ln in ((-120, 110), (-40, 120), (40, 120), (120, 110), (180, 100)):
        px = c2x + int(118 * math.cos(math.radians(ang)))
        py = c2y - int(188 * math.sin(math.radians(ang)))
        scale(px, py, ang + 90, ln, (104, 168, 72))


BUILDERS = {
    "papaya": draw_papaya,
    "canna-zucchero": draw_sugarcane,
    "rambutan": draw_rambutan,
    "frutta-drago": draw_dragonfruit,
}


def build(kind, out_path):
    rnd = random.Random(hash(kind) & 0xFFFF)
    img = new_canvas()
    d = ImageDraw.Draw(img)

    if kind == "melone":
        net = draw_melone(d, rnd)  # draws the ball onto d, returns net overlay
        img = Image.alpha_composite(img, net)
        d = ImageDraw.Draw(img)
        # cut wedge in front: rind + flesh + seed hollow
        wx, wy = CX + 250, CY + 330
        d.pieslice([wx - 300, wy - 300, wx + 300, wy + 300], 150, 265, fill=(150, 168, 84))
        d.pieslice([wx - 282, wy - 282, wx + 282, wy + 282], 150, 265, fill=(250, 182, 96))
        d.pieslice([wx - 210, wy - 210, wx + 210, wy + 210], 150, 265, fill=(255, 214, 150))
        d.pieslice([wx - 130, wy - 130, wx + 130, wy + 130], 158, 258, fill=(232, 168, 84))
        for _ in range(46):
            a = rnd.uniform(160, 256)
            rr = rnd.uniform(30, 118)
            bx = wx + rr * math.cos(math.radians(a))
            by = wy - rr * math.sin(math.radians(a))
            br = rnd.randint(9, 13)
            d.ellipse([bx - br, by - br, bx + br, by + br], fill=(250, 238, 208))
    else:
        BUILDERS[kind](d, rnd)

    # soften slightly, then clip everything to the centred art box
    img = img.filter(ImageFilter.GaussianBlur(1.4))
    box_mask = new_canvas()
    ImageDraw.Draw(box_mask).rounded_rectangle(
        [CX - BOX_W // 2, CY - BOX_H // 2, CX + BOX_W // 2, CY + BOX_H // 2], radius=80, fill=(255, 255, 255, 255)
    )
    alpha = ImageChops.multiply(img.split()[3], box_mask.split()[3])
    img.putalpha(alpha)

    # ground shadow
    ds = new_canvas()
    ImageDraw.Draw(ds).ellipse([CX - 360, CY + 690, CX + 360, CY + 770], fill=(0, 0, 0, 42))
    ds = ds.filter(ImageFilter.GaussianBlur(22))
    img = Image.alpha_composite(ds, img)

    img.save(out_path, "WEBP", quality=92)
    print("wrote", out_path)


if __name__ == "__main__":
    import os

    os.makedirs(OUT_DIR, exist_ok=True)
    for k in FRUITS:
        build(k, os.path.join(OUT_DIR, f"fruit-{k}.webp"))
