"""Build a CMYK print test sheet for the Conexus logo.

usage: build_sheet.py <logo.svg> <out.pdf>
"""
import re
import sys
import xml.etree.ElementTree as ET

from reportlab.lib.colors import CMYKColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

SVG_PATH, OUT_PATH = sys.argv[1], sys.argv[2]

STOPS = [0.0685, 0.1645, 0.3181, 0.7389, 0.9998]
SCREEN_HEX = ["#5D4DA2", "#7E7BB7", "#4B3D8B", "#3B306A", "#281F4C"]
GRAD_TOP, GRAD_BOTTOM = 0, 107  # gradient spans the full logo height (SVG units)

# Each variant: label, note, 5 gradient stops (C,M,Y,K %), solid colour for "Wealth" + triangles.
# A flat variant has stops=None and uses the solid colour everywhere.
VARIANTS = [
    ("A", "Baseline: standard automatic conversion",
     "What a normal RGB to CMYK conversion produces (Generic CMYK). Cyan is about equal to magenta, which is why it prints blue.",
     [(76, 73, 0, 0), (54, 47, 1, 0), (84, 84, 2, 2), (87, 89, 8, 15), (88, 89, 17, 37)], (87, 89, 8, 15)),
    ("B", "Suggested print values",
     "Magenta leads cyan at every stop, lighter overall, less black at the X tail.",
     [(60, 75, 0, 0), (40, 50, 0, 0), (70, 85, 0, 0), (80, 95, 5, 15), (85, 100, 10, 35)], (80, 95, 5, 15)),
    ("C", "More magenta",
     "B with about +10 magenta (cyan reduced where magenta is already at 100). Pushes toward red-purple.",
     [(55, 85, 0, 0), (35, 60, 0, 0), (65, 95, 0, 0), (75, 100, 5, 15), (80, 100, 10, 35)], (75, 100, 5, 15)),
    ("D", "Less cyan",
     "B with 10 less cyan. Brighter and warmer without adding ink.",
     [(50, 75, 0, 0), (30, 50, 0, 0), (60, 85, 0, 0), (70, 95, 5, 15), (75, 100, 10, 35)], (70, 95, 5, 15)),
    ("E", "Lighter",
     "B with less black and slightly less cyan/magenta. Best if the thin strokes print too dark.",
     [(55, 70, 0, 0), (35, 45, 0, 0), (65, 80, 0, 0), (75, 90, 0, 8), (80, 95, 5, 20)], (75, 90, 0, 8)),
    ("F", "Flat solid",
     "No gradient. Whole logo in the suggested anchor colour (same as B's 'Wealth').",
     None, (80, 95, 5, 15)),
    ("G", "Flat lighter purple",
     "No gradient. A brighter solid purple, often the best choice for small print.",
     None, (70, 90, 0, 5)),
]

GRID_C = [70, 75, 80, 85]
GRID_M = [85, 90, 95, 100]
GRID_YK = [(5, 15), (0, 5)]

K100 = CMYKColor(0, 0, 0, 1)
K50 = CMYKColor(0, 0, 0, 0.55)
K15 = CMYKColor(0, 0, 0, 0.15)


def cmyk(v):
    return CMYKColor(*(x / 100 for x in v))


def fmt(v):
    return "C{} M{} Y{} K{}".format(*v)


# ---- SVG parsing --------------------------------------------------------------

TOKEN = re.compile(r"[MLHVCZ]|-?(?:\d+\.?\d*|\.\d+)(?:e-?\d+)?", re.I)


def parse_d(d):
    """Parse absolute M/L/H/V/C/Z path data into a list of (op, coords)."""
    toks = TOKEN.findall(d)
    out, i, cmd, cx, cy, sx, sy = [], 0, None, 0.0, 0.0, 0.0, 0.0
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            if t.islower():
                raise ValueError("relative path commands not supported: " + t)
            cmd = t
            i += 1
            if cmd == "Z":
                out.append(("Z", ()))
                cx, cy = sx, sy
            continue
        n = lambda k: [float(x) for x in toks[i:i + k]]
        if cmd == "M":
            cx, cy = n(2); sx, sy = cx, cy; out.append(("M", (cx, cy))); i += 2; cmd = "L"
        elif cmd == "L":
            cx, cy = n(2); out.append(("L", (cx, cy))); i += 2
        elif cmd == "H":
            cx = n(1)[0]; out.append(("L", (cx, cy))); i += 1
        elif cmd == "V":
            cy = n(1)[0]; out.append(("L", (cx, cy))); i += 1
        elif cmd == "C":
            c = n(6); out.append(("C", tuple(c))); cx, cy = c[4], c[5]; i += 6
        else:
            raise ValueError("unexpected token " + t)
    return out


def load_logo(path):
    ns = {"s": "http://www.w3.org/2000/svg"}
    paths = []
    for p in ET.parse(path).getroot().findall("s:path", ns):
        paths.append({
            "ops": parse_d(p.get("d")),
            "evenodd": p.get("fill-rule") == "evenodd",
            "faded": p.get("fill-opacity") is not None,  # the two X triangles
            "bottom": max(c[i] for op, c in parse_d(p.get("d")) for i in range(1, len(c), 2)),
        })
    # Path order in the file: S, C, O, U, N, E, X, then "Wealth" glyphs, then triangles.
    for p in paths:
        top = min(c[i] for op, c in p["ops"] for i in range(1, len(c), 2))
        p["role"] = "solid" if p["faded"] or top > 75 else "gradient"
    return paths


LOGO = load_logo(SVG_PATH)
LOGO_W, LOGO_H = 437, 107


def draw_logo(c, x, y_top, width, variant):
    """Draw the logo with its top-left corner at (x, y_top) in PDF points."""
    _, _, _, stops, solid = variant
    s = width / LOGO_W
    to_pdf = lambda px, py: (x + px * s, y_top - py * s)

    for p in LOGO:
        path = c.beginPath()
        for op, co in p["ops"]:
            if op == "M":
                path.moveTo(*to_pdf(*co))
            elif op == "L":
                path.lineTo(*to_pdf(*co))
            elif op == "C":
                path.curveTo(*to_pdf(co[0], co[1]), *to_pdf(co[2], co[3]), *to_pdf(co[4], co[5]))
            else:
                path.close()
        fill_mode = 0 if p["evenodd"] else 1  # reportlab: 0 = even-odd, 1 = non-zero
        if p["role"] == "solid" or stops is None:
            c.setFillColor(cmyk(solid))
            c.drawPath(path, stroke=0, fill=1, fillMode=fill_mode)
        else:
            c.saveState()
            c.clipPath(path, stroke=0, fill=0, fillMode=fill_mode)
            x0, y0 = to_pdf(0, GRAD_TOP)
            x1, y1 = to_pdf(0, GRAD_BOTTOM)
            c.linearGradient(x0, y0, x1, y1, [cmyk(v) for v in stops], STOPS, extend=True)
            c.restoreState()


# ---- Layout -------------------------------------------------------------------

PAGE_W, PAGE_H = A4
M = 40  # margin
MM = 72 / 25.4


def wrap(c, text, x, y, max_w, font="Helvetica", size=8, leading=10.5, color=K50):
    c.setFont(font, size)
    c.setFillColor(color)
    line = ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if c.stringWidth(trial, font, size) > max_w and line:
            c.drawString(x, y, line)
            y -= leading
            line = word
        else:
            line = trial
    if line:
        c.drawString(x, y, line)
        y -= leading
    return y


def footer(c, page, total):
    c.setFont("Helvetica", 7)
    c.setFillColor(K50)
    c.drawString(M, 24, "Conexus Wealth: logo print colour test sheet. All colours are DeviceCMYK values exactly as labelled.")
    c.drawRightString(PAGE_W - M, 24, "Page {} of {}".format(page, total))


def variant_block(c, y, v):
    key, title, note, stops, solid = v
    c.setFillColor(K100)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(M, y, key)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(M + 18, y, title)
    y = wrap(c, note, M + 18, y - 13, PAGE_W - 2 * M - 18)

    # Large logo (110 mm) and business-card size (45 mm).
    big_w, small_w = 110 * MM, 45 * MM
    logo_top = y - 6
    draw_logo(c, M, logo_top, big_w, v)
    draw_logo(c, M + big_w + 14 * MM, logo_top - (big_w - small_w) * LOGO_H / LOGO_W / 2, small_w, v)
    c.setFont("Helvetica", 6.5)
    c.setFillColor(K50)
    c.drawString(M, logo_top - big_w * LOGO_H / LOGO_W - 9, "110 mm wide")
    c.drawString(M + big_w + 14 * MM, logo_top - big_w * LOGO_H / LOGO_W - 9, "45 mm wide (business card)")

    # Value strip.
    y = logo_top - big_w * LOGO_H / LOGO_W - 26
    sw = 13
    if stops:
        col_w = (PAGE_W - 2 * M) / 6
        for i, (pos, val) in enumerate(zip(STOPS, stops)):
            x = M + i * col_w
            c.setFillColor(cmyk(val))
            c.rect(x, y - sw + 8, sw, sw, stroke=0, fill=1)
            c.setFillColor(K100)
            c.setFont("Helvetica-Bold", 6.5)
            c.drawString(x + sw + 4, y + 3, "{:.2f}%".format(pos * 100))
            c.setFont("Helvetica", 6.5)
            c.drawString(x + sw + 4, y - 4, fmt(val))
        x = M + 5 * col_w
    else:
        x = M
    c.setFillColor(cmyk(solid))
    c.rect(x, y - sw + 8, sw, sw, stroke=0, fill=1)
    c.setFillColor(K100)
    c.setFont("Helvetica-Bold", 6.5)
    c.drawString(x + sw + 4, y + 3, "Solid (Wealth, X)" if stops else "Solid (whole logo)")
    c.setFont("Helvetica", 6.5)
    c.drawString(x + sw + 4, y - 4, fmt(solid))

    y -= 16
    c.setStrokeColor(K15)
    c.setLineWidth(0.5)
    c.line(M, y, PAGE_W - M, y)
    return y - 20


def swatch_grid(c, x, y, yk):
    cell_w, cell_h = 26 * MM, 17 * MM
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(K100)
    for j, m in enumerate(GRID_M):
        c.drawCentredString(x + 34 + j * cell_w + cell_w / 2, y + 4, "M{}".format(m))
    for i, cy_ in enumerate(GRID_C):
        top = y - i * (cell_h + 18)
        c.setFillColor(K100)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(x, top - cell_h / 2, "C{}".format(cy_))
        for j, m in enumerate(GRID_M):
            v = (cy_, m, yk[0], yk[1])
            cx_ = x + 34 + j * cell_w
            c.setFillColor(cmyk(v))
            c.rect(cx_ + 3, top - cell_h, cell_w - 6, cell_h, stroke=0, fill=1)
            c.setFillColor(K100)
            c.setFont("Helvetica", 6)
            c.drawCentredString(cx_ + cell_w / 2, top - cell_h - 8, fmt(v))
    return y - len(GRID_C) * (cell_h + 18)


def intro(c, y):
    c.setFillColor(K100)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(M, y, "Conexus Wealth: logo print colour test")
    y -= 18
    lines = [
        "How to use this sheet",
        "1. Print at 100% / Actual size (not 'Fit to page'), ideally on the same printer or press and paper the client will use.",
        "2. Turn off any printer colour 'enhancement'. If the print dialog offers it, let the application manage colour.",
        "3. Judge the prints in daylight or under a neutral light, not next to a screen. Screens will not match paper.",
        "4. Pick the version that reads as purple (not navy) at both sizes. Then use the grid on the last page to fine-tune the solid colour.",
        "5. Write down the letter (and grid cell, if used). Those CMYK values become the official print colours.",
    ]
    c.setFont("Helvetica-Bold", 9)
    c.drawString(M, y, lines[0])
    y -= 12
    for ln in lines[1:]:
        y = wrap(c, ln, M, y, PAGE_W - 2 * M, size=8, leading=10.5)
    return y - 14


c = canvas.Canvas(OUT_PATH, pagesize=A4)
c.setTitle("Conexus Wealth – logo print colour test")
c.setAuthor("Print colour test sheet")
TOTAL = 3

y = intro(c, PAGE_H - M - 10)
for v in VARIANTS[:3]:
    y = variant_block(c, y, v)
footer(c, 1, TOTAL)
c.showPage()

y = PAGE_H - M - 10
for v in VARIANTS[3:]:
    y = variant_block(c, y, v)
footer(c, 2, TOTAL)
c.showPage()

y = PAGE_H - M - 10
c.setFillColor(K100)
c.setFont("Helvetica-Bold", 14)
c.drawString(M, y, "Solid colour fine-tuning: 'Wealth', the X triangles and the 73.89% stop")
y = wrap(c, "Pick the patch that looks most like the purple the client wants. Use it for 'Wealth', the X triangles "
            "and the 73.89% gradient stop so they match. Top grid: Y5 K15 (deeper). Bottom grid: Y0 K5 (brighter).",
         M, y - 14, PAGE_W - 2 * M, size=8.5, leading=11)
for yk in GRID_YK:
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(K100)
    c.drawString(M, y - 10, "Y{} K{}".format(*yk))
    y = swatch_grid(c, M, y - 30, yk) - 16
footer(c, 3, TOTAL)
c.showPage()
c.save()
print("wrote", OUT_PATH)
