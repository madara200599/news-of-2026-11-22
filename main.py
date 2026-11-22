#!/usr/bin/env python3
"""news-image-20261122: the world news of Sunday 22 November 2026 in one image.

Draws a 1024x1024 newspaper front page with Python 3.13 standard library
only (zlib + struct for the PNG encoder, a 5x7 bitmap font, all geometry
drawn in code). No network, no randomness, no timestamps: two runs write
byte-identical output to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font: 5x7
# Each glyph is 7 rows of 5 pixels ('#' = on). Uppercase + digits + punctuation.
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
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
}

# ---------------------------------------------------------------- palette
INK = (18, 18, 18)
PAPER = (255, 255, 255)
RED = (176, 30, 30)
NAVY = (16, 48, 84)
BLUE = (28, 102, 158)
SKY = (168, 208, 232)
SEA = (24, 88, 140)
SEALIGHT = (120, 180, 220)
GREY = (96, 96, 96)
LIGHT = (243, 243, 238)
GOLD = (198, 158, 42)
GOLDDARK = (150, 110, 10)
GREEN = (34, 120, 70)
ORANGE = (230, 110, 20)
SMOKE = (150, 150, 150)

# ---------------------------------------------------------------- canvas
canvas = bytearray(PAPER * (W * H))


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        canvas[i], canvas[i + 1], canvas[i + 2] = c


def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        base = (yy * W + x) * 3
        for xx in range(w):
            i = base + xx * 3
            canvas[i], canvas[i + 1], canvas[i + 2] = c


def hline(x, y, w, c):
    rect(x, y, w, 1, c)


def vline(x, y, h, c):
    rect(x, y, 1, h, c)


def frame(x, y, w, h, c, t=2):
    rect(x, y, w, t, c)
    rect(x, y + h - t, w, t, c)
    rect(x, y, t, h, c)
    rect(x + w - t, y, t, h, c)


def circle(cx, cy, r, c):
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        for xx in range(cx - dx, cx + dx + 1):
            px(xx, cy + dy, c)


def line(x0, y0, x1, y1, c):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        px(x0, y0, c)
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def text(s, x, y, scale, c, bold=False):
    """Draw text; returns the x position just past the last character."""
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    rect(cx + col * scale, y + row * scale, scale, scale, c)
                    if bold:
                        rect(cx + col * scale + 1, y + row * scale, scale, scale, c)
        cx += 6 * scale
    return cx


def text_w(s, scale):
    return len(s) * 6 * scale


def center(s, y, scale, c, bold=False):
    x = (W - text_w(s, scale)) // 2
    text(s, x, y, scale, c, bold)
    return x


def wrap(s, max_chars):
    """Greedy word wrap into lines of at most max_chars characters."""
    lines = []
    for para in s.split("\n"):
        words = para.split(" ")
        cur = ""
        for w in words:
            if cur == "":
                cur = w
            elif len(cur) + 1 + len(w) <= max_chars:
                cur = cur + " " + w
            else:
                lines.append(cur)
                cur = w
        if cur != "":
            lines.append(cur)
    return lines


def draw_lines(lines, x, y, scale, c, leading, bold=False):
    for ln in lines:
        text(ln, x, y, scale, c, bold)
        y += leading
    return y

# ---------------------------------------------------------------- PNG encoder
def chunk(typ, data):
    return struct.pack(">I", len(data)) + typ + data + struct.pack(
        ">I", zlib.crc32(typ + data) & 0xFFFFFFFF
    )


def encode_png():
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw += canvas[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )


# ---------------------------------------------------------------- illustration
def draw_drone(x, y, s=1):
    # small quadcopter: body + two rotor bars
    rect(x, y + 3, 14 * s, 5 * s, INK)
    rect(x + 5 * s, y + 8 * s, 4 * s, 3 * s, INK)
    hline(x - 4 * s, y, 22 * s, INK)
    hline(x - 4 * s, y + 1, 22 * s, INK)
    hline(x - 4 * s, y + 12 * s, 22 * s, INK)


def draw_ship_scene(x, y, w, h):
    """Gulf of Finland: burning cargo ship, drones overhead, Finnish coast."""
    # sky
    rect(x, y, w, 118, SKY)
    # sun
    circle(x + w - 52, y + 30, 24, GOLD)
    # clouds
    rect(x + 24, y + 22, 92, 14, PAPER)
    rect(x + 48, y + 38, 64, 12, PAPER)
    rect(x + w - 190, y + 14, 84, 12, PAPER)
    # drones in the sky
    draw_drone(x + 60, y + 66)
    draw_drone(x + 150, y + 44)
    draw_drone(x + 250, y + 78)
    # distant shore (Finland) on the right
    rect(x + w - 108, y + 100, 108, 18, GREEN)
    rect(x + w - 96, y + 82, 6, 18, GREEN)
    rect(x + w - 78, y + 76, 6, 24, GREEN)
    rect(x + w - 58, y + 84, 6, 16, GREEN)
    # sea
    rect(x, y + 118, w, h - 118, SEA)
    # waves
    for wy in (y + 138, y + 168, y + 198, y + 228):
        for wx in range(x + 12, x + w - 12, 46):
            hline(wx, wy, 28, SEALIGHT)
    # ship hull (dark, listing slightly): trapezoid built from rows
    hull_top = y + 158
    for i in range(26):
        yy = hull_top + i
        left = x + 96 + i // 2
        right = x + 96 + 268 - i
        hline(left, yy, right - left, NAVY)
    # bow mast
    vline(x + 340, y + 118, 40, INK)
    hline(x + 330, y + 118, 20, INK)
    # containers on deck
    rect(x + 118, y + 132, 52, 26, RED)
    rect(x + 176, y + 132, 52, 26, GOLD)
    rect(x + 234, y + 132, 52, 26, GREEN)
    # bridge tower
    rect(x + 296, y + 122, 34, 36, PAPER)
    rect(x + 300, y + 128, 26, 8, NAVY)
    rect(x + 300, y + 140, 26, 8, NAVY)
    # funnel with smoke rising
    rect(x + 286, y + 138, 10, 20, INK)
    circle(x + 250, y + 112, 12, SMOKE)
    circle(x + 238, y + 92, 15, SMOKE)
    circle(x + 224, y + 70, 18, SMOKE)
    circle(x + 208, y + 48, 14, SMOKE)
    # flames over the containers
    circle(x + 202, y + 124, 10, ORANGE)
    circle(x + 214, y + 118, 8, GOLD)
    circle(x + 190, y + 118, 7, ORANGE)
    # red cross marker on the hull
    rect(x + 150, y + 168, 8, 8, RED)

# ---------------------------------------------------------------- page layout
LEAD_SUMMARY = (
    "THE SANCTIONED RUSSIAN CARGO SHIP SPARTA II, BOUND FOR KALININGRAD, "
    "WAS HIT BY SUSPECTED UKRAINIAN DRONES IN THE GULF OF FINLAND ON "
    "SATURDAY. THE SHIP CAUGHT FIRE AND DRIFTED INTO FINNISH WATERS. ITS "
    "CREW WAS TAKEN OFF BY ANOTHER VESSEL. FINLAND'S PRIME MINISTER SAID "
    "UKRAINE HAS THE RIGHT TO RETALIATE."
)

# (tag, tag colour, headline, summary)
STORIES = [
    ("GULF", RED,
     "TANKERS HIT OFF OMAN AS GULF STANDOFF GROWS",
     "MORE SHIPS STRUCK NEAR HORMUZ; BAHRAIN PROBES A PATRIOT CRASH."),
    ("EUROPE", NAVY,
     "ESTONIA TO SHUT ITS BORDER WITH RUSSIA",
     "TALLINN PLANS TO CLOSE THE ROAD CROSSING; MOSCOW CRIES IRON CURTAIN."),
    ("AFRICA", GREEN,
     "ANC FALLS TO 31% IN WORST RESULT SINCE 1994",
     "SOUTH AFRICA'S RULING PARTY LOSES MOST BIG CITIES; TALKS RACE TO 27 NOVEMBER."),
    ("CLIMATE", BLUE,
     "COP31 TALKS DEADLOCK OVER FOSSIL FUELS",
     "NEGOTIATORS IN TURKEY RUN INTO OVERTIME WITH NO DEAL ON OIL AND GAS."),
    ("N. AMERICA", NAVY,
     "PENTAGON CURBS US-CANADA MILITARY TIES",
     "DEFENCE CHIEF HEGSETH SETS FRESH LIMITS ON CONTACT BETWEEN THE ALLIES' FORCES."),
    ("SPACE", GOLDDARK,
     "BEPICOLOMBO REACHES MERCURY AFTER 8 YEARS",
     "THE EUROPEAN-JAPANESE PROBE ENTERS ORBIT AROUND THE SUN'S CLOSEST PLANET."),
]


def draw_cell(x, y, w, h, tag, tag_c, headline, summary):
    rect(x, y, w, h, LIGHT)
    frame(x, y, w, h, GREY, 1)
    chip_w = text_w(tag, 2) + 16
    rect(x + 10, y + 8, chip_w, 22, tag_c)
    text(tag, x + 18, y + 12, 2, PAPER)
    head_lines = wrap(headline, 38)[:2]
    draw_lines(head_lines, x + 10, y + 36, 2, INK, 16, bold=True)
    sum_lines = wrap(summary, 38)[:2]
    draw_lines(sum_lines, x + 10, y + 70, 2, INK, 15)


def build_page():
    frame(8, 8, 1008, 1008, INK, 3)
    # masthead
    center("THE WORLD IN ONE PAGE", 30, 6, NAVY, bold=True)
    rect(24, 84, 976, 3, INK)
    center("SUNDAY 22 NOVEMBER 2026", 94, 5, RED, bold=True)
    rect(24, 140, 976, 3, INK)
    rect(24, 146, 976, 1, INK)
    center("THE DAY'S WORLD NEWS, IN ONE IMAGE", 156, 2, GREY)
    # lead story
    text("LEAD STORY - THE BALTIC SEA", 24, 184, 2, RED, bold=True)
    draw_lines(["DRONES HIT RUSSIAN CARGO SHIP", "IN THE BALTIC"],
               24, 204, 4, INK, 32, bold=True)
    text("SANCTIONED VESSEL SPARTA II BURNS OFF FINLAND - CREW EVACUATED",
         24, 276, 2, INK, bold=True)
    rect(24, 300, 976, 2, GREY)
    # lead illustration + caption
    frame(24, 312, 470, 252, INK, 2)
    draw_ship_scene(26, 314, 466, 248)
    text("THE SPARTA II, BOUND FOR KALININGRAD, AFTER THE STRIKE",
         24, 570, 2, GREY)
    # lead summary + callout
    draw_lines(wrap(LEAD_SUMMARY, 40), 518, 312, 2, INK, 20)
    rect(518, 506, 482, 50, LIGHT)
    frame(518, 506, 482, 50, RED, 1)
    draw_lines(["FINLAND TIGHTENS SECURITY IN THE",
                "EASTERN GULF; ESTONIA WARNS OF DRONES"],
               530, 514, 2, RED, 16, bold=True)
    # divider + section header
    rect(24, 592, 976, 3, INK)
    text("ALSO MAKING NEWS", 24, 604, 3, NAVY, bold=True)
    right = "SIX STORIES, SIX REGIONS"
    text(right, 1000 - text_w(right, 2), 608, 2, GREY)
    # story grid: 2 columns x 3 rows
    for i, (tag, tag_c, headline, summary) in enumerate(STORIES):
        cx = 24 + (i % 2) * 500
        cy = 634 + (i // 2) * 104
        draw_cell(cx, cy, 476, 100, tag, tag_c, headline, summary)
    # ticker strip
    rect(24, 950, 976, 42, NAVY)
    center("ALSO TODAY: DENMARK SAYS RUSSIA PLOTTED TO KILL A US-UKRAINIAN RAPPER",
           956, 2, PAPER)
    center("FBI PROBES HACK OF ITS CRIME DATABASE - MODI OPENS A NEW BRIDGE IN BIHAR",
           974, 2, PAPER)
    # footer
    center("SOURCES: REUTERS, AP, BBC, YLE, TIMES OF INDIA - DRAWN FROM THE DAY'S REPORTS",
           998, 2, GREY)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    build_page()
    data = encode_png()
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
