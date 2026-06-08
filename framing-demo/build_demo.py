"""Demo: generate framing drawings (DXF + PDF) and a cut list (CSV) for an
8' x 10' shed with a 36" door (front) and a 36"x24" window (right wall).

Run:  python build_demo.py
"""
import csv
from framecad import Shed, Opening, build, optimize, hardware, render_dxf, render_pdf

shed = Shed(
    width=96, depth=120, height=96,
    openings=[
        Opening(wall="front", kind="door", width=38, height=82, offset=29),
        Opening(wall="right", kind="window", width=38, height=26,
                sill=40, offset=51),
    ],
)

drawings, members = build(shed)
cutplans, summary = optimize(members)
hw = hardware(members, shed)

OUT = "out"
import os
os.makedirs(OUT, exist_ok=True)

render_dxf.export(drawings, f"{OUT}/shed_framing.dxf")
render_pdf.export(drawings, cutplans, summary, hw, shed, f"{OUT}/shed_framing.pdf")

with open(f"{OUT}/cut_list.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["category", "size", "length_in", "qty"])
    for m in members:
        w.writerow([m.category, m.size, m.length, m.qty])
    w.writerow([])
    w.writerow(["--- OPTIMIZED STOCK ---"])
    w.writerow(["size", "stock_ft", "count", "drop_in"])
    for p in cutplans:
        w.writerow([p.size, int(p.stock_length / 12), p.count, p.drop])
    w.writerow([])
    w.writerow(["board_feet", summary["board_feet"]])
    w.writerow(["stock_count", summary["stock_count"]])
    w.writerow(["waste_pct", summary["waste_pct"]])

print("=== FRAMING TAKEOFF: 8' x 10' SHED ===")
print(f"{'CATEGORY':22} {'SIZE':5} {'LEN(in)':>8} {'QTY':>4}")
for m in members:
    print(f"{m.category:22} {m.size:5} {m.length:8.2f} {m.qty:>4}")
print("\n=== OPTIMIZED STOCK ===")
for p in cutplans:
    pat = " + ".join(f"{v:.1f}" for v in p.pattern)
    print(f"{p.size}  {int(p.stock_length/12)}ft  x{p.count}  [{pat}]  drop {p.drop}\"")
print(f"\nTotals: {summary['stock_count']} sticks | "
      f"{summary['board_feet']} bd-ft | {summary['waste_pct']}% waste")
print("\n=== HARDWARE ===")
for name, unit, qty in hw:
    print(f"{name:26} {qty} {unit}")
print(f"\nWrote: {OUT}/shed_framing.dxf, {OUT}/shed_framing.pdf, {OUT}/cut_list.csv")
