"""Draw the 19 November 2026 world-news poster, pure stdlib.

Renders a 1024x1024 newspaper-style front page with six verified stories
from Thursday 19 November 2026, using only the Python standard library:
a hand-built 5x7 bitmap font, primitive shape drawing, and a minimal PNG
encoder (zlib + struct). No network, no external files, deterministic.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (246, 241, 231)
NAVY = (22, 35, 63)
GOLD = (201, 162, 39)
INK = (28, 28, 28)
MUTED = (96, 92, 84)
CARD = (255, 255, 255)
BORDER = (216, 210, 196)
WHITE = (255, 255, 255)
SOFT_WHITE = (232, 236, 242)


# ---------------------------------------------------------------- font
# A 5x7 bitmap font, caps / digits / punctuation only. Every string is
# rendered in upper case, so no lower-case glyphs are needed.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    "~": ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
}

BLANK = ("00000",) * 7


def text_width(text, scale):
    """Pixel width of text at the given scale (no trailing gap)."""
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def wrap_words(text, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    current = ""
    for word in text.split(" "):
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set_px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = color[0]
            self.buf[i + 1] = color[1]
            self.buf[i + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        r, g, b = color
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i] = r
                self.buf[i + 1] = g
                self.buf[i + 2] = b

    def hline(self, x0, x1, y, color, thick=1):
        for t in range(thick):
            self.fill_rect(x0, y + t, x1 - x0, 1, color)

    def vline(self, x, y0, y1, color, thick=1):
        for t in range(thick):
            self.fill_rect(x + t, y0, 1, y1 - y0, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        """Bresenham line; thickness drawn as filled squares."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        half = thick // 2
        while True:
            self.fill_rect(x0 - half, y0 - half, thick, thick, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = math.isqrt(max(0, r * r - dy * dy))
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def dome(self, cx, base_y, r, color):
        """Filled upper half-disc sitting on base_y."""
        for dy in range(-r, 1):
            dx = math.isqrt(max(0, r * r - dy * dy))
            self.fill_rect(cx - dx, base_y + dy, 2 * dx + 1, 1, color)

    def polygon(self, points, color):
        """Scanline fill of a simple polygon."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if y0 == y1:
                    continue
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self.fill_rect(int(round(xs[j])), y,
                               int(round(xs[j + 1])) - int(round(xs[j])) + 1,
                               1, color)

    def draw_text(self, x, y, text, scale, color):
        cx = x
        for ch in text.upper():
            glyph = FONT.get(ch, BLANK)
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, color)
            cx += 6 * scale

    def draw_centered(self, cx, y, text, scale, color):
        self.draw_text(cx - text_width(text, scale) // 2, y, text, scale,
                       color)


def mix(a, b, t):
    """Blend colour a toward b by fraction t (0..1)."""
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ---------------------------------------------------------------- icons
def icon_summit(cv, cx, cy, c):
    """Three leaders around a table: three heads, three shoulders."""
    for dx, dy, r in ((-32, -10, 13), (0, -24, 15), (32, -10, 13)):
        cv.disc(cx + dx, cy + dy, r, c)
    for dx in (-32, 0, 32):
        cv.fill_rect(cx + dx - 15, cy + 8, 30, 16, c)
    cv.fill_rect(cx - 50, cy + 30, 100, 5, c)


def icon_scales(cv, cx, cy, c):
    """Scales of justice."""
    cv.disc(cx, cy - 44, 6, c)
    cv.vline(cx, cy - 40, cy + 34, c, 5)
    cv.hline(cx - 40, cx + 40, cy - 28, c, 5)
    cv.polygon([(cx - 40, cy - 26), (cx - 58, cy + 4), (cx - 22, cy + 4)], c)
    cv.polygon([(cx + 40, cy - 26), (cx + 58, cy + 4), (cx + 22, cy + 4)], c)
    cv.fill_rect(cx - 24, cy + 34, 48, 6, c)


def icon_chart(cv, cx, cy, c):
    """Rising bars and an arrow climbing past them."""
    cv.fill_rect(cx - 44, cy + 6, 16, 26, c)
    cv.fill_rect(cx - 18, cy - 8, 16, 40, c)
    cv.fill_rect(cx + 8, cy - 22, 16, 54, c)
    cv.line(cx - 44, cy + 22, cx - 16, cy - 2, c, 5)
    cv.line(cx - 16, cy - 2, cx + 4, cy + 8, c, 5)
    cv.line(cx + 4, cy + 8, cx + 44, cy - 32, c, 5)
    cv.polygon([(cx + 44, cy - 32), (cx + 22, cy - 32), (cx + 44, cy - 10)],
               c)


def icon_tower(cv, cx, cy, c):
    """A tower struck at its crown, with a burst of impact lines."""
    cv.fill_rect(cx - 16, cy - 42, 32, 84, c)
    cv.fill_rect(cx - 24, cy + 42, 48, 6, c)
    for wy in (-28, -12, 4, 20):
        cv.fill_rect(cx - 8, cy + wy, 16, 6, PAPER)
    bx, by = cx + 30, cy - 46
    for dx, dy in ((-16, 0), (16, 0), (0, -14), (0, 14),
                   (-11, -11), (11, -11), (-11, 11), (11, 11)):
        cv.line(bx, by, bx + dx, by + dy, c, 4)
    cv.disc(bx, by, 6, c)


def icon_capitol(cv, cx, cy, c):
    """A domed capitol building."""
    cv.dome(cx, cy + 4, 30, c)
    cv.vline(cx, cy - 40, cy - 26, c, 3)
    cv.polygon([(cx, cy - 40), (cx + 14, cy - 36), (cx, cy - 32)], c)
    cv.fill_rect(cx - 36, cy + 4, 72, 8, c)
    cv.fill_rect(cx - 32, cy + 12, 64, 26, c)
    for dx in (-24, -6, 12):
        cv.fill_rect(cx + dx, cy + 14, 6, 24, PAPER)
    cv.fill_rect(cx - 40, cy + 38, 80, 6, c)


def icon_boat(cv, cx, cy, c):
    """A small boat on waves, listing after a capsize."""
    cv.line(cx - 6, cy - 36, cx - 6, cy + 4, c, 4)
    cv.polygon([(cx - 6, cy - 36), (cx - 6, cy + 0), (cx + 24, cy + 0)], c)
    cv.polygon([(cx - 42, cy + 4), (cx + 42, cy + 4),
                (cx + 28, cy + 26), (cx - 28, cy + 26)], c)
    for wy in (36, 48):
        for k in range(4):
            cv.line(cx - 46 + k * 23, cy + wy,
                    cx - 46 + k * 23 + 11, cy + wy - 6, c, 3)
        cv.line(cx - 46, cy + wy, cx + 46, cy + wy, c, 3)


ICONS = {
    "summit": icon_summit,
    "scales": icon_scales,
    "chart": icon_chart,
    "tower": icon_tower,
    "capitol": icon_capitol,
    "boat": icon_boat,
}


# ---------------------------------------------------------------- stories
# The six verified stories of Thursday 19 November 2026.
STORIES = [
    {
        "tag": "SUMMIT",
        "headline": "TRUMP, XI AND PUTIN MEET",
        "detail": "First trilateral summit in Shenzhen",
        "accent": (31, 97, 141),
        "icon": "summit",
    },
    {
        "tag": "COURTS",
        "headline": "ICJ: MYANMAR COMMITTED GENOCIDE",
        "detail": "9-6: first state ever held responsible",
        "accent": (125, 60, 152),
        "icon": "scales",
    },
    {
        "tag": "MARKETS",
        "headline": "ANTHROPIC IPO IS THE BIGGEST EVER",
        "detail": "$81bn, 980m shares at $83, closed $97",
        "accent": (30, 132, 73),
        "icon": "chart",
    },
    {
        "tag": "CONFLICT",
        "headline": "HOUTHI MISSILE HITS RIYADH TOWER",
        "detail": "Strike on the PIF sovereign-fund tower",
        "accent": (176, 58, 46),
        "icon": "tower",
    },
    {
        "tag": "POLITICS",
        "headline": "SENATE BACKS TRUMP ON IRAN",
        "detail": "51-48 vote rejects war-powers curbs",
        "accent": (20, 143, 119),
        "icon": "capitol",
    },
    {
        "tag": "MIGRATION",
        "headline": "MIGRANT BOAT CAPSIZES OFF SENEGAL",
        "detail": "~50 aboard off Yenne, dozens missing",
        "accent": (202, 111, 30),
        "icon": "boat",
    },
]


# ---------------------------------------------------------------- layout
def draw_card(cv, px, py, story, idx):
    pw, ph = 496, 262
    accent = story["accent"]
    # Card body and border.
    cv.fill_rect(px, py, pw, ph, CARD)
    cv.fill_rect(px, py, pw, 2, BORDER)
    cv.fill_rect(px, py + ph - 2, pw, 2, BORDER)
    cv.fill_rect(px, py, 2, ph, BORDER)
    cv.fill_rect(px + pw - 2, py, 2, ph, BORDER)
    # Accent bar across the top.
    cv.fill_rect(px, py, pw, 10, accent)
    # Tinted icon column on the left.
    tint = mix(accent, WHITE, 0.86)
    cv.fill_rect(px + 2, py + 10, 118, ph - 12, tint)
    ICONS[story["icon"]](cv, px + 61, py + 122, accent)
    # Large story number at the foot of the icon column.
    num_color = mix(accent, WHITE, 0.45)
    cv.draw_centered(px + 61, py + 204, "%02d" % (idx + 1), 5, num_color)
    # Tag, headline, divider, detail on the right.
    tx = px + 138
    tw = pw - 138 - 16
    cv.draw_text(tx, py + 30, story["tag"], 2, accent)
    lines = wrap_words(story["headline"], tw, 4)
    hy = py + 54
    for line in lines:
        cv.draw_text(tx, hy, line, 4, INK)
        hy += 32
    dy = hy + 8
    cv.hline(tx, px + pw - 16, dy, BORDER, 2)
    dlines = wrap_words(story["detail"], tw, 3)
    dyy = dy + 14
    for line in dlines:
        cv.draw_text(tx, dyy, line, 3, MUTED)
        dyy += 24


def build_canvas():
    cv = Canvas(W, H, PAPER)
    # Masthead.
    cv.fill_rect(0, 0, W, 140, NAVY)
    cv.fill_rect(0, 140, W, 4, GOLD)
    cv.draw_centered(W // 2, 20, "THE WORLD IN ONE IMAGE", 2, GOLD)
    cv.draw_centered(W // 2, 46, "THURSDAY 19 NOVEMBER 2026", 6, WHITE)
    cv.draw_centered(W // 2, 102, "SIX STORIES THAT DEFINED THE DAY", 2,
                     SOFT_WHITE)
    # Six cards, two columns by three rows.
    xs = (16, 528)
    ys = (156, 434, 712)
    for i, story in enumerate(STORIES):
        draw_card(cv, xs[i % 2], ys[i // 2], story, i)
    # Footer.
    cv.draw_centered(W // 2, 988, "SIX STORIES . ONE DAY . 19 NOVEMBER 2026",
                     2, MUTED)
    return cv


# ---------------------------------------------------------------- png
def png_bytes(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.buf[y * stride:(y + 1) * stride]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    body = b"\x89PNG\r\n\x1a\n"
    body += chunk(b"IHDR", ihdr)
    body += chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    body += chunk(b"IEND", b"")
    return body


def build_entry(path):
    cv = build_canvas()
    data = png_bytes(cv)
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


if __name__ == "__main__":
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    size = build_entry(os.path.join(out, "entry.png"))
    print("wrote entry.png (%d bytes)" % size)
