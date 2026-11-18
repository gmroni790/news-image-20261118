#!/usr/bin/env python3
"""Render the entry image for make.fun news-image-20261118.

Draws a one-page newspaper front page summing up the world's news of
Wednesday 18 November 2026, and writes it to entry.png (1024x1024, under
1 MiB). Everything is drawn in code with PIL: no photographs, no network,
no copied artwork. The entry program (main.py) ships the rendered PNG;
this script documents exactly how the image was made.

Run:  python3 render.py
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 28  # page margin

PAPER = (246, 241, 229)
INK = (20, 20, 20)
WHITE = (255, 255, 255)
RED = (178, 34, 34)
NAVY = (30, 58, 95)
GOLD = (176, 141, 58)
GRAY = (96, 96, 96)
FAINT = (208, 200, 180)
LIGHT_GOLD = (238, 228, 200)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    path = name if os.path.isabs(name) else os.path.join(FONT_DIR, name)
    return ImageFont.truetype(path, size)


SERIF_B = "DejaVuSerif-Bold.ttf"
SERIF = "DejaVuSerif.ttf"
# DejaVu ships no serif italic here; Noto Serif's italic matches the face.
SERIF_I = "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf"
SANS_B = "DejaVuSans-Bold.ttf"
SANS = "DejaVuSans.ttf"


def wrap(draw, text, fname, size, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    f = font(fname, size)
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def center(draw, cx, y, text, fname, size, fill):
    f = font(fname, size)
    w = draw.textlength(text, font=f)
    draw.text((cx - w / 2, y), text, font=f, fill=fill)
    return y + size + 6


def star(draw, cx, cy, r, fill):
    """Five-pointed star centred at (cx, cy) with outer radius r."""
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.382
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def flag_usa(draw, x, y, w, h):
    """Stylised US flag: stripes and a canton of stars."""
    stripes = 7
    sh = h / stripes
    for i in range(stripes):
        if i % 2 == 0:
            draw.rectangle([x, y + i * sh, x + w, y + (i + 1) * sh],
                           fill=(178, 34, 34))
        else:
            draw.rectangle([x, y + i * sh, x + w, y + (i + 1) * sh],
                           fill=WHITE)
    cw, ch = w * 0.4, sh * 4
    draw.rectangle([x, y, x + cw, y + ch], fill=NAVY)
    for r in range(3):
        for c in range(4):
            sx = x + cw * (0.14 + 0.24 * c)
            sy = y + ch * (0.18 + 0.32 * r)
            draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=WHITE)


def flag_china(draw, x, y, w, h):
    """Stylised Chinese flag: red field, five yellow stars."""
    draw.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    star(draw, x + w * 0.22, y + h * 0.30, h * 0.20, (255, 222, 0))
    for dx, dy in [(0.42, 0.18), (0.50, 0.32), (0.46, 0.50), (0.36, 0.58)]:
        star(draw, x + w * dx, y + h * dy, h * 0.08, (255, 222, 0))


def flag_russia(draw, x, y, w, h):
    """Stylised Russian flag: white, blue and red bands."""
    draw.rectangle([x, y, x + w, y + h / 3], fill=WHITE)
    draw.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(0, 87, 183))
    draw.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(216, 0, 39))


def icon_drone(draw, x, y, s, color):
    """Quadcopter drone, top view."""
    cx, cy = x + s / 2, y + s / 2
    arm = s * 0.34
    for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        draw.line([cx, cy, cx + dx * arm, cy + dy * arm], fill=color, width=3)
        rx, ry = cx + dx * arm, cy + dy * arm
        draw.ellipse([rx - 5, ry - 5, rx + 5, ry + 5], outline=color, width=2)
    draw.rounded_rectangle([cx - 8, cy - 6, cx + 8, cy + 6], radius=3, fill=color)


def icon_bridge(draw, x, y, s, color):
    """Bridge with a broken span over water."""
    deck = y + s * 0.42
    draw.line([x + 2, deck, x + s * 0.42, deck], fill=color, width=4)
    draw.line([x + s * 0.58, deck, x + s - 2, deck], fill=color, width=4)
    draw.arc([x + 4, y + 2, x + s - 4, y + s * 0.75], start=180, end=360,
             fill=color, width=3)
    draw.line([x + 6, deck, x + 6, y + s * 0.78], fill=color, width=3)
    draw.line([x + s - 6, deck, x + s - 6, y + s * 0.78], fill=color, width=3)
    for i, wx in enumerate([0.12, 0.42, 0.72]):
        wy = y + s * (0.86 + 0.05 * (i % 2))
        draw.line([x + s * wx, wy, x + s * wx + 12, wy], fill=color, width=2)


def icon_virus(draw, x, y, s, color):
    """Spiked virus particle."""
    cx, cy = x + s / 2, y + s / 2
    for i in range(8):
        ang = i * math.pi / 4
        x1 = cx + math.cos(ang) * s * 0.22
        y1 = cy + math.sin(ang) * s * 0.22
        x2 = cx + math.cos(ang) * s * 0.46
        y2 = cy + math.sin(ang) * s * 0.46
        draw.line([x1, y1, x2, y2], fill=color, width=3)
        draw.ellipse([x2 - 3, y2 - 3, x2 + 3, y2 + 3], fill=color)
    draw.ellipse([cx - s * 0.22, cy - s * 0.22, cx + s * 0.22, cy + s * 0.22],
                 fill=color)
    draw.ellipse([cx - s * 0.08, cy - s * 0.08, cx + s * 0.02, cy + s * 0.02],
                 fill=WHITE)


def icon_cross(draw, x, y, s, color):
    """Medical cross in a ring."""
    draw.ellipse([x + 2, y + 2, x + s - 2, y + s - 2], outline=color, width=3)
    t = s * 0.20
    cx, cy = x + s / 2, y + s / 2
    draw.rectangle([cx - t / 2, cy - t * 1.4, cx + t / 2, cy + t * 1.4],
                   fill=color)
    draw.rectangle([cx - t * 1.4, cy - t / 2, cx + t * 1.4, cy + t / 2],
                   fill=color)


def icon_chip(draw, x, y, s, color):
    """Computer chip."""
    draw.rectangle([x + 8, y + 8, x + s - 8, y + s - 8], outline=color, width=3)
    draw.rectangle([x + 15, y + 15, x + s - 15, y + s - 15], fill=color)
    for i in range(3):
        px = x + 12 + i * (s - 24) / 2
        draw.line([px, y + 2, px, y + 8], fill=color, width=2)
        draw.line([px, y + s - 8, px, y + s - 2], fill=color, width=2)
        py = y + 12 + i * (s - 24) / 2
        draw.line([x + 2, py, x + 8, py], fill=color, width=2)
        draw.line([x + s - 8, py, x + s - 2, py], fill=color, width=2)


def icon_hash(draw, x, y, s, color):
    f = font(SANS_B, int(s * 0.85))
    draw.text((x + s * 0.16, y - s * 0.04), "#", font=f, fill=color)


PANELS = [
    {
        "kicker": "MIDDLE EAST  •  GULF WAR",
        "color": (139, 30, 30),
        "icon": icon_drone,
        "headline": "Iran strikes US base in Kuwait",
        "deck": "US jets hit Qeshm Island; Iran's drones answered at "
                "Ali Al Salem.",
    },
    {
        "kicker": "UKRAINE WAR",
        "color": NAVY,
        "icon": icon_bridge,
        "headline": "Ukraine cripples Crimea bridge",
        "deck": "Road span falls into the Kerch Strait; rail line "
                "damaged.",
    },
    {
        "kicker": "HEALTH  •  USA",
        "color": (180, 95, 6),
        "icon": icon_virus,
        "headline": "US loses measles-free status",
        "deck": "5,400+ cases, the worst in 30 years; elimination "
                "status lost.",
    },
    {
        "kicker": "HEALTH  •  CONGO",
        "color": (39, 103, 56),
        "icon": icon_cross,
        "headline": "Ebola still out of control in Congo",
        "deck": "5,500 dead in six months; seven in ten young "
                "children die.",
    },
    {
        "kicker": "BUSINESS  •  TECH",
        "color": (63, 122, 31),
        "icon": icon_chip,
        "headline": "Nvidia tops $100bn in a quarter",
        "deck": "Sales double to a record; ousted founder Huang "
                "will not return.",
    },
]

NUMBERS = [
    ("19", "killed as a Russian military plane crashes in Siberia"),
    ("6.0", "magnitude quake strikes Papua New Guinea"),
    ("1,441", "drones Russia says it shot down overnight"),
]

TICKER_ITEMS = [
    "Knesset elects speaker opposed to Netanyahu",
    "Cyclone Akvan strengthens",
    "William and Kate meet Modi in Delhi",
    "Rubio: no sign US outages were an attack",
]


def draw_panel(draw, x, y, w, h, panel):
    draw.rectangle([x, y, x + w, y + h], fill=WHITE, outline=INK, width=2)
    color = panel["color"]
    draw.rectangle([x, y, x + w, y + 6], fill=color)
    panel["icon"](draw, x + w - 46, y + 12, 36, color)
    f_kick = font(SANS_B, 14)
    draw.text((x + 14, y + 14), panel["kicker"], font=f_kick, fill=color)
    lines = wrap(draw, panel["headline"], SERIF_B, 23, w - 28)
    yy = y + 40
    f_head = font(SERIF_B, 23)
    for line in lines[:3]:
        draw.text((x + 14, yy), line, font=f_head, fill=INK)
        yy += 26
    # Deck starts just below the headline, however many lines it took,
    # so the two can never overlap; it is clipped to the space left.
    deck_lines = wrap(draw, panel["deck"], SANS, 16, w - 28)
    yy += 2
    max_lines = max(0, (y + h - 8 - yy) // 19)
    f_deck = font(SANS, 16)
    for line in deck_lines[:max_lines]:
        draw.text((x + 14, yy), line, font=f_deck, fill=(60, 60, 60))
        yy += 19


def draw_numbers_panel(draw, x, y, w, h):
    color = (91, 74, 138)
    draw.rectangle([x, y, x + w, y + h], fill=WHITE, outline=INK, width=2)
    draw.rectangle([x, y, x + w, y + 6], fill=color)
    icon_hash(draw, x + w - 46, y + 12, 36, color)
    draw.text((x + 14, y + 14), "BY THE NUMBERS", font=font(SANS_B, 14),
              fill=color)
    yy = y + 40
    for num, label in NUMBERS:
        f_num = font(SANS_B, 24)
        draw.text((x + 14, yy), num, font=f_num, fill=NAVY)
        nw = draw.textlength(num, font=f_num)
        lines = wrap(draw, label, SANS, 15, w - 28 - nw - 12)
        f_lab = font(SANS, 15)
        ly = yy + 4
        for line in lines[:2]:
            draw.text((x + 26 + nw, ly), line, font=f_lab, fill=(60, 60, 60))
            ly += 18
        yy += 40


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # Double newspaper frame.
    draw.rectangle([10, 10, W - 11, H - 11], outline=INK, width=2)
    draw.rectangle([18, 18, W - 19, H - 19], outline=INK, width=1)

    # Top strip.
    f_small = font(SANS_B, 15)
    draw.text((M, 30), "ONE DAY  •  ONE IMAGE  •  THE WORLD", font=f_small,
              fill=GRAY)
    tag = "MAKE.FUN WORLD DESK"
    draw.text((W - M - draw.textlength(tag, font=f_small), 30), tag,
              font=f_small, fill=GRAY)
    draw.line([M, 54, W - M, 54], fill=INK, width=2)

    # Masthead.
    center(draw, W // 2, 62, "THE WORLD TODAY", SERIF_B, 84, INK)
    draw.line([M, 158, W - M, 158], fill=RED, width=3)
    center(draw, W // 2, 168, "WEDNESDAY, 18 NOVEMBER 2026", SANS_B, 30, INK)
    center(draw, W // 2, 204,
           "Six stories that defined the day — from Shenzhen to the Gulf, "
           "Kyiv to Kinshasa.", SERIF_I, 19, (70, 70, 70))

    # Lead story.
    lx, ly, lw, lh = M, 236, W - 2 * M, 262
    draw.rectangle([lx, ly, lx + lw, ly + lh], fill=WHITE, outline=INK,
                   width=2)
    draw.rectangle([lx, ly, lx + lw, ly + 6], fill=RED)
    draw.text((lx + 20, ly + 18), "APEC SUMMIT  •  SHENZHEN, CHINA",
              font=font(SANS_B, 18), fill=RED)
    f_lead = font(SERIF_B, 46)
    draw.text((lx + 20, ly + 46), "TRUMP LANDS", font=f_lead, fill=INK)
    draw.text((lx + 20, ly + 96), "IN SHENZHEN", font=f_lead, fill=INK)
    deck = ("Xi Jinping greets him at the airport as the APEC summit "
            "opens. A first-ever trilateral with Putin follows on "
            "Thursday — nuclear arms, Ukraine and Iran on the table.")
    yy = ly + 158
    for line in wrap(draw, deck, SANS, 20, 560):
        draw.text((lx + 20, yy), line, font=font(SANS, 20),
                  fill=(50, 50, 50))
        yy += 26

    # Right column: three flags, one per leader.
    fx = lx + 612
    fw = lx + lw - 20 - fx
    flag_h = 46
    flags = [(flag_usa, "USA", NAVY), (flag_china, "CHINA", (255, 222, 0)),
             (flag_russia, "RUSSIA", NAVY)]
    fy = ly + 18
    for fn, label, tcol in flags:
        fn(draw, fx, fy, fw, flag_h)
        draw.rectangle([fx, fy, fx + fw, fy + flag_h], outline=INK, width=1)
        # White chip behind the label so it reads on any band.
        f_lab = font(SANS_B, 16)
        tw = draw.textlength(label, font=f_lab)
        chip_x = fx + fw - tw - 22
        draw.rectangle([chip_x, fy + 11, fx + fw - 6, fy + 35],
                       fill=WHITE, outline=INK, width=1)
        draw.text((chip_x + 6, fy + 12), label, font=f_lab, fill=NAVY)
        fy += flag_h + 10
    # Tag box under the flags.
    draw.rectangle([fx, fy + 2, fx + fw, fy + 52], fill=LIGHT_GOLD,
                   outline=GOLD, width=1)
    center(draw, fx + fw // 2, fy + 8, "FIRST-EVER TRILATERAL", SANS_B, 18,
           NAVY)
    center(draw, fx + fw // 2, fy + 30, "THURSDAY 19 NOV", SANS_B, 15, INK)

    # Story grid: 2 rows x 3 columns.
    gx, gy = M, 512
    cw, chh, gap = 312, 164, 16
    positions = [(gx + (cw + gap) * c, gy + (chh + gap) * r)
                 for r in range(2) for c in range(3)]
    for pos, panel in zip(positions[:5], PANELS):
        draw_panel(draw, pos[0], pos[1], cw, chh, panel)
    draw_numbers_panel(draw, positions[5][0], positions[5][1], cw, chh)

    # Ticker.
    ty = 864
    draw.rectangle([M, ty, W - M, ty + 72], fill=NAVY)
    draw.rectangle([M, ty, M + 168, ty + 72], fill=RED)
    f_tick = font(SANS_B, 20)
    label = "ALSO TODAY"
    tw = draw.textlength(label, font=f_tick)
    draw.text((M + (168 - tw) / 2, ty + 24), label, font=f_tick, fill=WHITE)
    ticker = "   •   ".join(TICKER_ITEMS)
    lines = wrap(draw, ticker, SANS, 17, W - 2 * M - 168 - 24)
    yy = ty + 6
    for line in lines[:3]:
        draw.text((M + 184, yy), line, font=font(SANS, 17), fill=WHITE)
        yy += 21

    # Footer.
    center(draw, W // 2, 948,
           "Every event above happened, or was first reported, on "
           "Wednesday 18 November 2026.", SANS, 15, GRAY)
    center(draw, W // 2, 970,
           "Sources: Reuters, AP, AFP, BBC, NDTV, Gulf News. "
           "Image drawn in code; no photographs.", SANS, 15, GRAY)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img.save(out, optimize=True)
    print(f"wrote {out} ({os.path.getsize(out)} bytes)")


if __name__ == "__main__":
    main()
