"""Export the Conexus logo as flat CMYK vector PDFs for print.

usage: make_print_logos.py <logo.svg> <out_dir>

Approved print colour: C70 M90 Y0 K5 (option G on the test sheet), used flat
for the whole logo. The RGB gradient is for screen only.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

from reportlab.lib.colors import CMYKColor
from reportlab.pdfgen import canvas

SVG_PATH, OUT_DIR = sys.argv[1], sys.argv[2]

OUTPUTS = [
    ("Conexus-logo-print-cmyk.pdf", (70, 90, 0, 5), "Print colour C70 M90 Y0 K5"),
    ("Conexus-logo-print-black.pdf", (0, 0, 0, 100), "Single colour K100"),
]

TOKEN = re.compile(r"[MLHVCZ]|-?(?:\d+\.?\d*|\.\d+)(?:e-?\d+)?", re.I)


def parse_d(d):
    """Parse absolute M/L/H/V/C/Z path data into a list of (op, coords)."""
    toks = TOKEN.findall(d)
    out, i, cmd, cx, cy = [], 0, None, 0.0, 0.0
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            if t.islower():
                raise ValueError("relative path commands not supported: " + t)
            cmd = t
            i += 1
            if cmd == "Z":
                out.append(("Z", ()))
            continue
        n = lambda k: [float(x) for x in toks[i:i + k]]
        if cmd == "M":
            cx, cy = n(2); out.append(("M", (cx, cy))); i += 2; cmd = "L"
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


root = ET.parse(SVG_PATH).getroot()
_, _, W, H = (float(v) for v in root.get("viewBox").split())
PATHS = [(parse_d(p.get("d")), p.get("fill-rule") == "evenodd")
         for p in root.findall("{http://www.w3.org/2000/svg}path")]

for name, value, subject in OUTPUTS:
    out = os.path.join(OUT_DIR, name)
    # 1 SVG unit = 1 pt; the artwork is vector, so it scales to any size.
    c = canvas.Canvas(out, pagesize=(W, H))
    c.setTitle("Conexus Wealth logo")
    c.setSubject(subject)
    c.setFillColor(CMYKColor(*(v / 100 for v in value)))
    for ops, evenodd in PATHS:
        path = c.beginPath()
        for op, co in ops:
            if op == "M":
                path.moveTo(co[0], H - co[1])
            elif op == "L":
                path.lineTo(co[0], H - co[1])
            elif op == "C":
                path.curveTo(co[0], H - co[1], co[2], H - co[3], co[4], H - co[5])
            else:
                path.close()
        c.drawPath(path, stroke=0, fill=1, fillMode=0 if evenodd else 1)
    c.showPage()
    c.save()
    print("wrote", out)
