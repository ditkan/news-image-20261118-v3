#!/usr/bin/env python3
"""Render the front page for news-image-20261118 (v3).

Draws a clean, airy broadsheet -- "THE WORLD IN A DAY" -- that sums up
Wednesday 18 November 2026 in 28 complete stories across six continents.
Rendered at 2x (2048x2048) and downscaled to 1024x1024 for smooth type.
All text is drawn programmatically with Pillow; the map is a dot grid
computed from hand-written continent polygons below.
"""
import os

from PIL import Image, ImageDraw, ImageFont

W = 2048                   # canvas (2x of 1024)
H = 2048
MX = 46                    # side margin (2x px)
CW = W - 2 * MX            # content width = 1956

PAPER = (248, 243, 230)
INK = (24, 20, 14)
RED = (158, 27, 35)
GREY = (104, 94, 78)
LIGHT = (226, 216, 192)
WHITE = (255, 253, 247)

FDIR = "/usr/share/fonts/truetype"
DISPLAY = f"{FDIR}/noto/NotoSerifDisplay-Black.ttf"
SERIF = f"{FDIR}/noto/NotoSerif-Regular.ttf"
SERIF_B = f"{FDIR}/noto/NotoSerif-Bold.ttf"
SANS = f"{FDIR}/noto/NotoSans-Regular.ttf"
SANS_B = f"{FDIR}/noto/NotoSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def draw_spaced(draw, cx, y, s, f, fill, spacing=4):
    """Draw letter-spaced text centred on cx."""
    widths = [text_w(draw, ch, f) for ch in s]
    total = sum(widths) + spacing * (len(s) - 1)
    x = cx - total / 2
    for ch, w in zip(s, widths):
        draw.text((x, y), ch, font=f, fill=fill)
        x += w + spacing
    return total


def wrap(draw, s, f, max_w):
    words = s.split()
    lines, cur = [], ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if text_w(draw, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, s, f, max_w, lh, fill=INK):
    """Draw a wrapped paragraph; returns y after the last line."""
    for line in wrap(draw, s, f, max_w):
        draw.text((x, y), line, font=f, fill=fill)
        y += lh
    return y


def para_h(draw, s, f, max_w, lh):
    """Height a wrapped paragraph would take, without drawing."""
    return len(wrap(draw, s, f, max_w)) * lh


# ---------------------------------------------------------------- map
# Hand-written simplified continent polygons in (lon, lat).
EURASIA = [
    (-9, 37), (-9, 43), (-2, 48), (-4, 49), (0, 51), (5, 53), (8, 57),
    (7, 58), (12, 56), (18, 56), (21, 60), (25, 60), (24, 66), (32, 70),
    (50, 68), (70, 72), (95, 76), (120, 73), (150, 71), (170, 67),
    (178, 65), (170, 60), (158, 53), (150, 45), (142, 42), (135, 35),
    (129, 33), (122, 31), (120, 25), (113, 22), (108, 17), (106, 9),
    (104, 6), (100, 7), (98, 10), (97, 15), (93, 17), (91, 22), (88, 22),
    (86, 19), (80, 15), (77, 8), (75, 12), (72, 19), (68, 23), (61, 25),
    (57, 26), (54, 26), (51, 28), (48, 30), (50, 29), (48, 26), (52, 25),
    (55, 24), (59, 22), (55, 17), (52, 15), (45, 12), (43, 12), (40, 15),
    (38, 20), (35, 28), (34, 31), (36, 36), (30, 36), (27, 37), (23, 36),
    (19, 40), (15, 38), (12, 42), (10, 44), (8, 44), (3, 42), (0, 39),
    (-2, 37),
]
NORTH_AMERICA = [
    (-168, 66), (-150, 70), (-135, 69), (-125, 71), (-110, 73),
    (-95, 79), (-88, 71), (-82, 73), (-78, 68), (-76, 62), (-68, 58),
    (-60, 55), (-55, 52), (-60, 48), (-66, 45), (-70, 42), (-74, 39),
    (-76, 35), (-79, 33), (-80, 28), (-80, 25), (-82, 23), (-84, 22),
    (-87, 21), (-90, 20), (-94, 18), (-97, 16), (-96, 15), (-92, 14),
    (-86, 13), (-83, 9), (-79, 9), (-81, 13), (-86, 15), (-90, 14),
    (-95, 16), (-100, 18), (-105, 22), (-110, 24), (-113, 28),
    (-117, 33), (-122, 37), (-124, 42), (-124, 47), (-128, 51),
    (-133, 56), (-140, 60), (-152, 59), (-162, 61), (-168, 66),
]
GREENLAND = [
    (-45, 60), (-32, 68), (-22, 70), (-19, 76), (-28, 82), (-50, 80),
    (-58, 74), (-56, 66), (-53, 61),
]
SOUTH_AMERICA = [
    (-79, 9), (-71, 12), (-64, 10), (-55, 6), (-50, 0), (-44, -3),
    (-35, -8), (-39, -13), (-40, -20), (-48, -25), (-52, -33),
    (-57, -38), (-62, -41), (-65, -45), (-67, -50), (-69, -54),
    (-71, -54), (-73, -50), (-73, -44), (-73, -37), (-71, -30),
    (-70, -20), (-75, -15), (-79, -8), (-80, -4), (-80, 1), (-77, 4),
    (-79, 9),
]
AFRICA = [
    (-6, 35), (0, 36), (10, 37), (11, 34), (20, 32), (30, 31), (32, 31),
    (34, 28), (35, 24), (38, 22), (40, 15), (43, 12), (48, 11), (51, 12),
    (48, 5), (42, -2), (40, -8), (40, -15), (37, -20), (35, -24),
    (32, -29), (28, -33), (20, -35), (17, -32), (15, -27), (13, -18),
    (12, -12), (13, -6), (9, -1), (9, 4), (4, 6), (-3, 5), (-8, 4),
    (-13, 8), (-17, 12), (-17, 20), (-16, 27), (-13, 28), (-9, 31),
]
AUSTRALIA = [
    (113, -22), (114, -28), (115, -34), (118, -35), (124, -33),
    (129, -32), (132, -32), (135, -35), (138, -36), (140, -38),
    (145, -38), (150, -37), (153, -30), (153, -25), (150, -22),
    (146, -19), (142, -11), (142, -15), (140, -18), (136, -15),
    (136, -12), (132, -11), (130, -13), (126, -14), (122, -17),
    (118, -20),
]
# Island blobs: (lon, lat, radius_deg)
BLOBS = [
    (-2, 53, 3.2),      # Britain
    (133, 34, 3.0), (137, 35, 2.6), (140, 37, 2.6), (141, 41, 2.6),
    (142, 44, 2.2),     # Japan arc
    (100, 1, 4.5), (103, -2, 3.4),  # Sumatra
    (114, 1, 5.0),      # Borneo
    (108, -7, 4.6),     # Java
    (120, -2, 3.2),     # Sulawesi
    (131, -3, 3.6), (138, -4, 4.6), (144, -6, 3.6),  # New Guinea
    (122, 13, 3.4), (121, 16, 2.6),  # Philippines
    (47, -19, 3.4),     # Madagascar
    (172, -41, 2.6), (174, -37, 2.2),  # New Zealand
    (-78, 21, 3.4),     # Cuba
    (127, 39, 2.6),     # Korea
    (80, 7, 1.8),       # Sri Lanka
    (-17, 65, 2.4),     # Iceland
    (121, 24, 1.6),     # Taiwan
]
POLYS = [EURASIA, NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, AFRICA, AUSTRALIA]


def in_poly(lon, lat, poly):
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > lat) != (y2 > lat):
            xin = (x2 - x1) * (lat - y1) / (y2 - y1) + x1
            if lon < xin:
                inside = not inside
    return inside


def on_land(lon, lat):
    for poly in POLYS:
        if in_poly(lon, lat, poly):
            return True
    for clon, clat, r in BLOBS:
        if (lon - clon) ** 2 + (lat - clat) ** 2 <= r * r:
            return True
    return False


def draw_map(draw, x0, y0, w, h, markers):
    """Dot-grid world map in the box (x0, y0, w, h); markers = [(lon, lat, n)]."""
    dot_r = max(2, int(w / 260))
    lon_min, lon_max = -170.0, 190.0
    lat_min, lat_max = -58.0, 84.0
    lon = lon_min
    while lon <= lon_max:
        lat = lat_min
        while lat <= lat_max:
            if on_land(lon if lon <= 180 else lon - 360, lat):
                px = x0 + (lon - lon_min) / (lon_max - lon_min) * w
                py = y0 + (lat_max - lat) / (lat_max - lat_min) * h
                draw.ellipse([px - dot_r, py - dot_r, px + dot_r, py + dot_r],
                             fill=(96, 88, 72))
            lat += 2.35
        lon += 2.35
    mf = font(SANS_B, 25)
    for mlon, mlat, num in markers:
        px = x0 + (mlon - lon_min) / (lon_max - lon_min) * w
        py = y0 + (lat_max - mlat) / (lat_max - lat_min) * h
        r = 19
        draw.ellipse([px - r, py - r, px + r, py + r], fill=RED)
        tw = text_w(draw, num, mf)
        draw.text((px - tw / 2, py - 14), num, font=mf, fill=WHITE)


# ---------------------------------------------------------------- content
LEAD = {
    "kicker": "No. 1 · THE LEAD · ASIA",
    "headline": "Iran and America trade blows across the Gulf",
    "body": (
        "Iran's Revolutionary Guards sent attack drones at a US radar at "
        "Bahrain's Sheikh Isa air base — the third such attack in five "
        "days. Central Command said the drones were intercepted with no "
        "damage. Within hours, US jets struck a Guards missile site on "
        "Qeshm Island, and tankers burned in Hormuz."
    ),
}

# Digest items: (number, headline, summary, feature?) -- features lead
# their continent group in larger type. Summaries are kept to ~85 chars
# (two lines) so the page stays airy and legible.
DIGEST = [
    ("EUROPE", [
        ("2", "Ukraine fells a span of the Kerch Bridge",
         "A second day of strikes collapsed the road arch of Russia's "
         "bridge to Crimea. Moscow claims a record 1,441 drones downed.", True),
        ("3", "France's unions stage a strike day",
         "146,000 marched by the official count; the CGT claimed over "
         "500,000 on the streets.", False),
        ("4", "Britain sanctions settlement builders",
         "Asset freezes hit eight West Bank firms and Tzav 9, days before "
         "the E1 tender deadline.", False),
        ("5", "UN: 372 civilians killed in Ukraine",
         "UN monitors counted October's civilian toll in Ukraine at 372 "
         "killed as strikes grew.", False),
    ]),
    ("ASIA", [
        ("6", "Trump opens Asia tour; leaders converge",
         "A Quad summit in Manila, a Thai trade deal — and Putin in China "
         "for a first Trump–Xi–Putin meeting at APEC.", True),
        ("7", "Modi proposes free e-visas at ASEAN",
         "In Manila, India's leader pitched free e-visas and a peaceful, "
         "open Indo-Pacific.", False),
        ("8", "Canada and China extend trade deals",
         "Xi met Canada's Carney before APEC, and the two capitals "
         "extended their trade cooperation.", False),
        ("9", "COP31 draft urges fossil phase-out",
         "The Antalya text seeks adaptation finance tripled to $120bn a "
         "year by 2035.", False),
        ("10", "Cyclone Akvan grows in Bay of Bengal",
         "India's weather office warns the storm is strengthening; "
         "flights were cancelled.", False),
        ("11", "India condemns strike on Tara Gas",
         "Delhi condemned the hit on the Hormuz LPG tanker; 21 of 24 "
         "Indian crew are ashore.", False),
    ]),
    ("NORTH AMERICA", [
        ("12", "Nvidia's revenue doubles: $115.8bn",
         "Sales rose 103% in a year; guidance points to $130bn next "
         "quarter. First results since Huang resigned.", True),
        ("13", "America is no longer measles-free",
         "PAHO stripped a status held since 2000 after 5,412 cases; "
         "Bolivia and Mexico fell too.", False),
        ("14", "Dow drops 849 points, fourth fall",
         "The S&P 500 hit its lowest since July as software slid; Nvidia "
         "jumped after hours.", False),
        ("15", "27 years for the plot to kill Trump",
         "A Brooklyn court gave Pakistan's Asif Merchant 330 months for "
         "the Iran-backed plot.", False),
        ("16", "US seeks $50.1bn for air traffic control",
         "The administration's request to rebuild the system now goes to "
         "Congress.", False),
    ]),
    ("SOUTH AMERICA", [
        ("17", "Ecuador crew sue US over drone strike",
         "Fishermen say US drones sank their boat; the suit cites 71 "
         "strikes and 235 dead.", False),
        ("18", "Brazil's real sinks to 19-month low",
         "The activity gauge fell 0.2% in September and 0.9% across the "
         "third quarter.", False),
        ("19", "Lula: trade beat the tariffs",
         "Brazil's president told ASEAN that wider markets after US "
         "duties lifted his surplus.", False),
    ]),
    ("AFRICA", [
        ("20", "Ebola passes 11,300 cases in Congo",
         "WHO counts over 5,500 deaths from the Bundibugyo strain, cases "
         "doubling in three months.", True),
        ("21", "Drones are Sudan's deadliest weapon",
         "The UN confirms 2,230 civilians killed this year, over 1,630 "
         "of them by drones.", False),
        ("22", "Congo peace tracks fail to stop war",
         "Parallel mediation efforts have not halted the fighting in the "
         "country's east.", False),
        ("23", "Nigeria inflation eases to 14.06%",
         "October's rate was a six-year low — though food prices still "
         "rose 19.13% in a year.", False),
    ]),
    ("OCEANIA", [
        ("24", "Australia sanctions West Bank settlers",
         "Three people and four groups targeted, incl. Daniella Weiss; a "
         "first builder sanction.", False),
        ("25", "One Nation vows 90% refugee cut",
         "Pauline Hanson's party pitched a near-total cut to refugee "
         "intake, and curbs on parents.", False),
    ]),
    ("SCIENCE & THE WORLD", [
        ("26", "Voyager 1: one light-day from Earth",
         "At 10:16 UTC the 1977 probe passed 25.9 billion km out; signals "
         "now take a day.", False),
        ("27", "Chemical exposure starts before birth",
         "A new review finds endocrine-disrupting chemicals can harm "
         "babies in the womb, UN reports.", False),
    ]),
    ("SPORT", [
        ("28", "India edge Pakistan for 10th SAFF title",
         "Mandi's 88th-minute header sealed a 2–1 comeback in Dhaka and "
         "a third straight crown.", False),
    ]),
]

NUMBERS = [
    ("$115.8bn", "Nvidia revenue, +103%"),
    ("11,300+", "Ebola cases, DR Congo"),
    ("5,412", "US measles cases, 2026"),
    ("25.9bn km", "Voyager: one light-day"),
    ("–849", "Dow points lost"),
    ("$120bn", "COP31 adaptation / yr"),
]

TICKER = ("Gaza truce board warns the ceasefire may collapse · WFP cuts Gaza "
          "hot meals · Fed minutes due Wednesday · "
          "SpaceX catches a falling Starship")
SOURCES = ("Sources: Reuters · AP · AFP · BBC · Al Jazeera · The Guardian · "
           "UN News · WHO · NASA · PAHO · OHCHR — reporting of Wednesday "
           "18 November 2026. Drawn entirely by program; no photographs.")

# type ladder (2x px)
F_KICK = (SANS_B, 25)
F_LEAD_H = (SERIF_B, 64)
F_LEAD_B = (SERIF, 34)
F_FEAT_H = (SERIF_B, 34)
F_FEAT_B = (SERIF, 27)
F_DH = (SERIF_B, 28)
F_DB = (SERIF, 24)
F_GRP = (SANS_B, 25)


def item_h(draw, item, col_wd):
    num, head, summ, feat = item
    if feat:
        hf, bf, hlh, blh = font(*F_FEAT_H), font(*F_FEAT_B), 40, 34
    else:
        hf, bf, hlh, blh = font(*F_DH), font(*F_DB), 32, 29
    h = para_h(draw, f"{num}.  {head}", hf, col_wd, hlh)
    h += 2 + para_h(draw, summ, bf, col_wd, blh)
    return h + 8


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    right = W - MX

    # --- masthead ---------------------------------------------------------
    y = 16
    draw_spaced(d, W / 2, y, "GLOBAL EDITION · EVERY CONTINENT · ONE PAGE",
                font(SANS_B, 21), GREY, spacing=4)
    y += 34
    d.line([MX, y, right, y], fill=INK, width=5)
    y += 9
    f_mast = font(DISPLAY, 96)
    mast = "THE WORLD IN A DAY"
    d.text(((W - text_w(d, mast, f_mast)) / 2, y), mast, font=f_mast, fill=INK)
    y += 112
    d.line([MX, y, right, y], fill=INK, width=2)
    y += 5
    d.line([MX, y, right, y], fill=INK, width=5)
    y += 12

    # --- red date band ------------------------------------------------------
    band_h = 62
    d.rectangle([MX, y, right, y + band_h], fill=RED)
    d.text((MX + 24, y + 12), "WEDNESDAY 18 NOVEMBER 2026",
           font=font(SANS_B, 38), fill=WHITE)
    cnt = "28 STORIES · 6 CONTINENTS"
    f_cnt = font(SANS_B, 32)
    d.text((right - 24 - text_w(d, cnt, f_cnt), y + 14), cnt, font=f_cnt, fill=WHITE)
    y += band_h + 14

    # --- lead (left) + map & numbers (right) --------------------------------
    lead_w = 1090
    f_kick = font(*F_KICK)
    d.text((MX, y), LEAD["kicker"], font=f_kick, fill=RED)
    hy = para(d, MX, y + 34, LEAD["headline"], font(*F_LEAD_H), lead_w, 76)
    lead_end = para(d, MX, hy + 6, LEAD["body"], font(*F_LEAD_B), lead_w, 48)

    rx = MX + lead_w + 48
    rw = right - rx
    d.text((rx, y), "THE DAY ON ONE MAP", font=f_kick, fill=INK)
    draw_map(d, rx, y + 34, rw, 200,
             [(51, 26, "1"), (37, 45, "2"), (121, 14, "6"),
              (-122, 37, "12"), (23, -3, "20")])
    cap_y = y + 34 + 200 + 5
    d.text((rx, cap_y), "Markers: the five front-page stories.",
           font=font(SANS, 22), fill=GREY)
    ny = cap_y + 28
    d.text((rx, ny), "THE DAY IN NUMBERS", font=f_kick, fill=RED)
    ny += 32
    cell_w = rw / 3
    f_num = font(SERIF_B, 34)
    f_lab = font(SANS, 20)
    for i, (num, lab) in enumerate(NUMBERS):
        cx = rx + (i % 3) * cell_w
        cy = ny + (i // 3) * 78
        d.text((cx, cy), num, font=f_num, fill=INK)
        para(d, cx, cy + 42, lab, f_lab, cell_w - 14, 26, fill=GREY)
    right_end = ny + 2 * 78
    y = max(lead_end, right_end) + 14
    d.line([MX, y, right, y], fill=INK, width=3)
    y += 10

    # --- story river ----------------------------------------------------------
    d.rectangle([MX, y, right, y + 40], fill=INK)
    d.text((MX + 20, y + 8), "THE FRONT PAGE — AND THE REST OF THE DAY, IN FULL",
           font=font(SANS_B, 27), fill=WHITE)
    y += 40 + 10

    col_wd = (CW - 2 * 38) / 3
    scratch = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    cols = [[], [], []]
    heights = [0, 0, 0]
    for gname, items in DIGEST:
        gh = 36 + sum(item_h(scratch, it, col_wd) for it in items) + 2
        j = heights.index(min(heights))
        cols[j].append((gname, items))
        heights[j] += gh
    print("column heights:", heights)
    f_grp = font(*F_GRP)
    dig_end = y
    for ci, groups in enumerate(cols):
        cx = MX + ci * (col_wd + 38)
        cy = y
        for gname, items in groups:
            d.text((cx, cy), gname, font=f_grp, fill=RED)
            d.line([cx, cy + 28, cx + col_wd, cy + 28], fill=RED, width=2)
            cy += 36
            for item in items:
                num, head, summ, feat = item
                if feat:
                    hf, bf, hlh, blh = font(*F_FEAT_H), font(*F_FEAT_B), 40, 34
                else:
                    hf, bf, hlh, blh = font(*F_DH), font(*F_DB), 32, 29
                hy2 = para(d, cx, cy, f"{num}.  {head}", hf, col_wd, hlh)
                cy = para(d, cx, hy2 + 2, summ, bf, col_wd, blh) + 8
            cy += 2
        dig_end = max(dig_end, cy)
        if ci:
            d.line([cx - 19, y, cx - 19, dig_end - 8], fill=LIGHT, width=2)
    y = dig_end + 2

    # --- ticker + sources ---------------------------------------------------------
    d.rectangle([MX, y, right, y + 44], fill=INK)
    f_tick = font(SANS_B, 23)
    tick = "ON THE WIRE — " + TICKER
    while text_w(d, tick, f_tick) > CW - 36 and len(tick) > 10:
        tick = tick[:-2]
    d.text((MX + 18, y + 10), tick, font=f_tick, fill=WHITE)
    y += 44 + 9
    f_src = font(SANS, 21)
    sw = text_w(d, SOURCES, f_src)
    d.text(((W - sw) / 2, y), SOURCES, font=f_src, fill=GREY)
    y += 26
    print("final y:", y, "of", H)

    img = img.resize((1024, 1024), Image.LANCZOS)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
