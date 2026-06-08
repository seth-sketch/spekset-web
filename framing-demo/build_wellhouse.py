"""Generate the well-house measured drawing set + engineered cut/parts list.

Outputs (in out/):
    wellhouse.pdf   measured elevations, roof plan, section, frame, tables
    wellhouse.dxf   all views, CAD/CNC ready
    wellhouse_cutlist.csv
"""
import csv
import os
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

from framecad import wellhouse as wh, render_dxf
from framecad.render_pdf import _title_block, _draw_fitted, MARGIN, PW, PH

PROJECT = "WELL HOUSE — measured rebuild (36-1/2 x 45-1/4)"
STRUT_STOCK = 120.0      # 10 ft strut channel
KERF = 0.0625


def optimize_strut(parts):
    pieces = []
    for p in parts:
        pieces += [p.length] * p.qty
    pieces.sort(reverse=True)
    sticks = []
    for pc in pieces:
        for s in sticks:
            if s["rem"] >= pc + KERF:
                s["rem"] -= pc + KERF
                s["cuts"].append(pc)
                break
        else:
            sticks.append({"rem": STRUT_STOCK - pc, "cuts": [pc]})
    total_used = sum(sum(s["cuts"]) for s in sticks)
    total_stock = len(sticks) * STRUT_STOCK
    waste = round(100 * (1 - total_used / total_stock), 1) if sticks else 0
    return sticks, len(sticks), round(total_stock / 12, 1), waste


def main():
    drawings = wh.all_drawings()
    parts = wh.parts()
    sticks, n_sticks, lf, waste = optimize_strut(parts)
    clad = wh.cladding()
    hw = wh.hardware()

    os.makedirs("out", exist_ok=True)
    render_dxf.export(drawings, "out/wellhouse.dxf")

    c = canvas.Canvas("out/wellhouse.pdf", pagesize=landscape(letter))
    for dr in drawings:
        _title_block(c, PROJECT, dr.name)
        _draw_fitted(c, dr, MARGIN, MARGIN + 0.4 * inch,
                     PW - 2 * MARGIN, PH - 2 * MARGIN - 0.9 * inch)
        c.showPage()
    _report_page(c, parts, sticks, n_sticks, lf, waste, clad, hw)
    c.showPage()
    c.save()

    with open("out/wellhouse_cutlist.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["STRUT CHANNEL CUT LIST"])
        w.writerow(["member", "length_in", "qty"])
        for p in parts:
            w.writerow([p.category, p.length, p.qty])
        w.writerow([])
        w.writerow([f"{n_sticks} sticks of 10ft strut", f"{lf} lin-ft",
                    f"{waste}% waste"])
        w.writerow([])
        w.writerow(["CLADDING / ROOF"])
        for name, unit, qty in clad:
            w.writerow([name, qty, unit])
        w.writerow([])
        w.writerow(["HARDWARE"])
        for name, unit, qty in hw:
            w.writerow([name, qty, unit])

    print("Strut frame:", n_sticks, "x 10ft sticks |", lf, "lin-ft |",
          waste, "% waste")
    print("Wrote out/wellhouse.pdf, out/wellhouse.dxf, out/wellhouse_cutlist.csv")


def _report_page(c, parts, sticks, n_sticks, lf, waste, clad, hw):
    _title_block(c, PROJECT, "CUT LIST / MATERIALS / HARDWARE")
    x = MARGIN + 10
    y = PH - MARGIN - 0.7 * inch

    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, y, "STRUCTURAL FRAME — 1-5/8\" GALV. STRUT CHANNEL")
    y -= 15
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x, y, "MEMBER")
    c.drawString(x + 230, y, "LEN(in)")
    c.drawString(x + 290, y, "QTY")
    y -= 3
    c.line(x, y, x + 330, y)
    y -= 12
    c.setFont("Helvetica", 8)
    for p in parts:
        c.drawString(x, y, p.category)
        c.drawString(x + 230, y, f"{p.length:g}")
        c.drawString(x + 290, y, str(p.qty))
        y -= 12
    y -= 4
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x, y, f"Order {n_sticks} x 10ft strut sticks   "
                       f"({lf} lin-ft, {waste}% offcut waste)")

    # right column: cladding + hardware
    hx = PW / 2 + 30
    hy = PH - MARGIN - 0.7 * inch
    c.setFont("Helvetica-Bold", 11)
    c.drawString(hx, hy, "CLADDING / ROOF")
    hy -= 15
    c.setFont("Helvetica", 8)
    for name, unit, qty in clad:
        c.drawString(hx, hy, f"{name}")
        c.drawRightString(PW - MARGIN - 12, hy, f"{qty} {unit}")
        hy -= 12

    hy -= 10
    c.setFont("Helvetica-Bold", 11)
    c.drawString(hx, hy, "HARDWARE / MECHANISM")
    hy -= 15
    c.setFont("Helvetica", 8)
    for name, unit, qty in hw:
        c.drawString(hx, hy, name)
        c.drawRightString(PW - MARGIN - 12, hy, f"{qty} {unit}")
        hy -= 12

    c.setFont("Helvetica-Oblique", 7)
    c.drawString(x, MARGIN + 14,
                 "Frame = strength. Wall/roof materials are swappable "
                 "(PVC, cedar, metal) without changing the skeleton. "
                 "All hardware 316 SS for the coastal setting.")


if __name__ == "__main__":
    main()
