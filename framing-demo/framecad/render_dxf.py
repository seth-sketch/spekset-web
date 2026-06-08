"""Render a list of Drawings into a single DXF file (CAD/CNC ready)."""
from __future__ import annotations
import ezdxf
from .draw import Drawing

LAYER_COLORS = {        # ACI color indices
    "FRAMING": 7,       # white/black
    "PLATE": 5,         # blue
    "OPENING": 1,       # red
    "DIM": 3,           # green
    "TEXT": 2,          # yellow
}
HALIGN = {"left": 0, "center": 1, "right": 2}
VALIGN = {"bottom": 1, "middle": 2, "top": 3}


def export(drawings, path, gap=36):
    doc = ezdxf.new("R2010", setup=True)
    msp = doc.modelspace()
    for name, color in LAYER_COLORS.items():
        if name not in doc.layers:
            doc.layers.add(name, color=color)

    # lay views left-to-right with a gap, aligned on a common baseline
    ox = 0.0
    for dr in drawings:
        minx, miny, maxx, maxy = dr.bbox()
        dx, dy = ox - minx, -miny
        for l in dr.lines:
            msp.add_line((l.x1 + dx, l.y1 + dy), (l.x2 + dx, l.y2 + dy),
                         dxfattribs={"layer": l.layer})
        for t in dr.texts:
            e = msp.add_text(t.s, height=t.h, rotation=t.rotation,
                             dxfattribs={"layer": t.layer})
            e.set_placement((t.x + dx, t.y + dy),
                            align=_align(t.halign, t.valign))
        ox += (maxx - minx) + gap

    doc.saveas(path)
    return path


def _align(h, v):
    from ezdxf.enums import TextEntityAlignment as A
    table = {
        ("left", "bottom"): A.BOTTOM_LEFT, ("center", "bottom"): A.BOTTOM_CENTER,
        ("right", "bottom"): A.BOTTOM_RIGHT, ("left", "middle"): A.MIDDLE_LEFT,
        ("center", "middle"): A.MIDDLE_CENTER, ("right", "middle"): A.MIDDLE_RIGHT,
        ("left", "top"): A.TOP_LEFT, ("center", "top"): A.TOP_CENTER,
        ("right", "top"): A.TOP_RIGHT,
    }
    return table.get((h, v), A.BOTTOM_LEFT)
