"""Render Drawings + cut/parts tables into a printable multi-page PDF."""
from __future__ import annotations
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

PAGE = landscape(letter)          # 11 x 8.5 in
PW, PH = PAGE
MARGIN = 0.5 * inch
LINEW = {"FRAMING": 0.8, "PLATE": 1.4, "OPENING": 1.2, "DIM": 0.4, "TEXT": 0.4}
GRAY = {"FRAMING": 0.15, "PLATE": 0.0, "OPENING": 0.0, "DIM": 0.45, "TEXT": 0.0}


def export(drawings, cutplans, summary, hardware, shed, path,
           project="SAMPLE SHED 8' x 10'"):
    c = canvas.Canvas(path, pagesize=PAGE)

    # one drawing per page, fitted to the sheet
    for dr in drawings:
        _title_block(c, project, dr.name)
        _draw_fitted(c, dr,
                     MARGIN, MARGIN + 0.4 * inch,
                     PW - 2 * MARGIN, PH - 2 * MARGIN - 0.9 * inch)
        c.showPage()

    _tables_page(c, cutplans, summary, hardware, project)
    c.showPage()
    c.save()
    return path


def _draw_fitted(c, dr, bx, by, bw, bh):
    minx, miny, maxx, maxy = dr.bbox()
    mw, mh = max(maxx - minx, 1), max(maxy - miny, 1)
    scale = min(bw / mw, bh / mh) * 0.92
    # center within box
    offx = bx + (bw - mw * scale) / 2 - minx * scale
    offy = by + (bh - mh * scale) / 2 - miny * scale

    def X(x):
        return offx + x * scale

    def Y(y):
        return offy + y * scale

    for l in dr.lines:
        c.setLineWidth(LINEW.get(l.layer, 0.6))
        g = GRAY.get(l.layer, 0.1)
        c.setStrokeColorRGB(g, g, g)
        c.line(X(l.x1), Y(l.y1), X(l.x2), Y(l.y2))

    c.setFillColorRGB(0, 0, 0)
    for t in dr.texts:
        fs = max(5, min(9, t.h * scale))
        c.setFont("Helvetica", fs)
        c.saveState()
        c.translate(X(t.x), Y(t.y))
        if t.rotation:
            c.rotate(t.rotation)
        dy = {"bottom": 0, "middle": -fs * 0.35, "top": -fs * 0.7}[t.valign]
        if t.halign == "center":
            c.drawCentredString(0, dy, t.s)
        elif t.halign == "right":
            c.drawRightString(0, dy, t.s)
        else:
            c.drawString(0, dy, t.s)
        c.restoreState()


def _title_block(c, project, sheet):
    c.setLineWidth(1)
    c.setStrokeColorRGB(0, 0, 0)
    c.rect(MARGIN, MARGIN, PW - 2 * MARGIN, PH - 2 * MARGIN)
    y = PH - MARGIN - 0.32 * inch
    c.line(MARGIN, y, PW - MARGIN, y)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN + 6, y + 8, f"{project}")
    c.setFont("Helvetica", 9)
    c.drawRightString(PW - MARGIN - 6, y + 8,
                      f"{sheet}    |    FrameCAD demo    |    NTS-fit, dims in ft-in")


def _tables_page(c, cutplans, summary, hardware, project):
    _title_block(c, project, "CUT LIST & PARTS LIST")
    x = MARGIN + 10
    y = PH - MARGIN - 0.7 * inch

    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, y, "LUMBER CUT LIST (stock-length optimized)")
    y -= 16
    c.setFont("Helvetica-Bold", 8)
    cols = [(x, "SIZE"), (x + 55, "STOCK"), (x + 110, "QTY"),
            (x + 150, "CUT PATTERN (per stick)"), (x + 430, "DROP")]
    for cx, label in cols:
        c.drawString(cx, y, label)
    y -= 3
    c.line(x, y, PW - MARGIN - 10, y)
    y -= 12
    c.setFont("Helvetica", 8)
    for p in cutplans:
        pat = " + ".join(f'{_q(v)}' for v in p.pattern)
        if len(pat) > 60:
            pat = pat[:57] + "..."
        row = [(x, p.size), (x + 55, f"{int(p.stock_length/12)}'"),
               (x + 110, f"x{p.count}"), (x + 150, pat),
               (x + 430, f'{_q(p.drop)}')]
        for cx, val in row:
            c.drawString(cx, y, val)
        y -= 12
        if y < MARGIN + 120:
            break

    y -= 8
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x, y, f"Totals:  {summary['stock_count']} sticks   |   "
                       f"{summary['board_feet']} board-ft   |   "
                       f"{summary['waste_pct']}% offcut waste")

    # hardware table stacked below the cut list
    hy = y - 28
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, hy, "PARTS / HARDWARE LIST")
    hy -= 16
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x, hy, "ITEM")
    c.drawString(x + 200, hy, "UNIT")
    c.drawString(x + 250, hy, "QTY")
    hy -= 3
    c.line(x, hy, x + 320, hy)
    hy -= 12
    c.setFont("Helvetica", 8)
    for name, unit, qty in hardware:
        c.drawString(x, hy, name)
        c.drawString(x + 200, hy, unit)
        c.drawString(x + 250, hy, str(qty))
        hy -= 12


def _q(inches):
    """Inches -> compact ft-in with eighths."""
    whole = int(inches)
    frac = inches - whole
    eighths = round(frac * 8)
    ft, rem = divmod(whole, 12)
    s = ""
    if ft:
        s += f"{ft}'"
    s += f"{rem}" if not ft else f"-{rem}"
    if eighths:
        s += f"-{eighths}/8"
    return s + '"'
