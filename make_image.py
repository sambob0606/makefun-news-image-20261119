"""Draw the 19 November 2026 world-news infographic (1024x1024 PNG).

Stories verified 2026-11-20 from Reuters / WSJ / Le Monde / NPR reporting of
Thursday 19 November 2026. Deterministic: fixed text, colours, fonts and
layout, no randomness, no network, no timestamp in the image.
Run: python3 make_image.py  -> writes entry.png and entry_image.b64
(next to this file).
"""
import base64
import hashlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
W, H = 1024, 1024
BG = (12, 21, 38)
CARD = (22, 35, 61)
WHITE = (255, 255, 255)
BODY = (199, 210, 232)
MUTED = (143, 163, 200)
GOLD = (242, 193, 78)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def wrap_first(draw, text, fnt, first_w, rest_w):
    """Wrap with a narrower first line (the number badge sits top-right)."""
    words = text.split()
    lines, cur, limit = [], "", first_w
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= limit:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
            limit = rest_w
    if cur:
        lines.append(cur)
    return lines


STORIES = [
    ("SUMMIT", (46, 134, 228),
     "Trump, Xi and Putin hold first trilateral summit",
     "The three leaders met in Shenzhen on the APEC sidelines and issued a 'peace declaration'."),
    ("JUSTICE", (228, 177, 46),
     "World court: Myanmar committed genocide",
     "The ICJ ruled 9-6 that the 2017 crackdown on the Rohingya was genocide, a first for the court."),
    ("MARKETS", (46, 184, 166),
     "Anthropic's $81bn IPO is the biggest ever",
     "The Claude maker sold 980m shares at $83; shares closed at $97 on their Nasdaq debut, topping SpaceX's record."),
    ("MIDDLE EAST", (228, 87, 46),
     "Houthi missile hits Riyadh tower",
     "A strike on 19 November hit a tower housing Saudi Arabia's sovereign wealth fund; debris and damage were reported."),
    ("US POLITICS", (155, 107, 228),
     "Senate backs Trump on Iran war powers",
     "Senators voted 51-48 to reject a resolution curbing the president's Iran war powers."),
    ("MIGRATION", (228, 107, 155),
     "Migrant boat capsizes off Senegal",
     "About 50 people were aboard when the Europe-bound boat sank off Yenne; dozens are missing."),
]


def draw_image():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # Header
    d.text((36, 30), "WORLD NEWS  \u2022  THE DAY IN SIX STORIES",
           font=font(FONT_BOLD, 22), fill=MUTED)
    d.text((36, 62), "THURSDAY", font=font(FONT_BOLD, 34), fill=GOLD)
    d.text((36, 98), "19 NOVEMBER 2026", font=font(FONT_BOLD, 72), fill=WHITE)
    d.rectangle([36, 176, 988, 180], fill=GOLD)
    # Cards: 2 columns x 3 rows
    cw, ch, gap = 466, 238, 18
    x0, y0 = 36, 198
    for i, (tag, accent, head, body) in enumerate(STORIES):
        cx = x0 + (i % 2) * (cw + gap)
        cy = y0 + (i // 2) * (ch + gap)
        d.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=14, fill=CARD)
        d.rectangle([cx, cy + 14, cx + 8, cy + ch - 14], fill=accent)
        # Number badge, top right
        bx, by = cx + cw - 62, cy + 16
        d.ellipse([bx, by, bx + 44, by + 44], fill=accent)
        num = str(i + 1)
        nw = d.textlength(num, font=font(FONT_BOLD, 24))
        d.text((bx + (44 - nw) / 2, by + 8), num,
               font=font(FONT_BOLD, 24), fill=WHITE)
        # Tag
        d.text((cx + 26, cy + 18), tag, font=font(FONT_BOLD, 19), fill=accent)
        # Headline, up to 2 lines (first line clears the number badge)
        head_lines = wrap_first(d, head, font(FONT_BOLD, 27), 350, cw - 52)
        hy = cy + 48
        for line in head_lines[:2]:
            d.text((cx + 26, hy), line, font=font(FONT_BOLD, 27), fill=WHITE)
            hy += 34
        # Body, up to 3 lines
        body_lines = wrap(d, body, font(FONT_REG, 20), cw - 52)
        byy = cy + 48 + 2 * 34 + 10
        for line in body_lines[:3]:
            d.text((cx + 26, byy), line, font=font(FONT_REG, 20), fill=BODY)
            byy += 27
    # Footer
    d.text((36, 962), "Sources: Reuters  \u2022  WSJ  \u2022  Le Monde  \u2022  NPR  \u2014  Reported 19 November 2026",
           font=font(FONT_REG, 18), fill=MUTED)
    return img


def main():
    img = draw_image()
    png = HERE / "entry.png"
    img.save(png, format="PNG", optimize=True)
    data = png.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    (HERE / "entry_image.b64").write_text(b64 + "\n", encoding="ascii")
    print("entry.png", len(data), "bytes",
          "sha256", hashlib.sha256(data).hexdigest()[:16],
          "b64 lines", b64.count("\n") + 1)


if __name__ == "__main__":
    main()
