"""Tiny CAD-neutral drawing model shared by the DXF and PDF renderers.

Everything is in real-world inches. Each view (floor plan, wall elevation) is a
Drawing with its own local origin; the renderers handle layout and scaling.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


@dataclass
class Line:
    x1: float
    y1: float
    x2: float
    y2: float
    layer: str = "FRAMING"


@dataclass
class Text:
    x: float
    y: float
    h: float           # text height, in model inches
    s: str
    layer: str = "TEXT"
    halign: str = "left"     # left | center | right
    valign: str = "bottom"   # bottom | middle | top
    rotation: float = 0.0     # degrees, ccw


@dataclass
class Drawing:
    name: str
    lines: List[Line] = field(default_factory=list)
    texts: List[Text] = field(default_factory=list)

    # --- primitives -----------------------------------------------------
    def line(self, x1, y1, x2, y2, layer="FRAMING"):
        self.lines.append(Line(x1, y1, x2, y2, layer))

    def rect(self, x, y, w, h, layer="FRAMING"):
        self.line(x, y, x + w, y, layer)
        self.line(x + w, y, x + w, y + h, layer)
        self.line(x + w, y + h, x, y + h, layer)
        self.line(x, y + h, x, y, layer)

    def text(self, x, y, h, s, layer="TEXT", halign="left",
             valign="bottom", rotation=0.0):
        self.texts.append(Text(x, y, h, s, layer, halign, valign, rotation))

    # --- dimensions (architectural oblique-tick style) ------------------
    def dim_h(self, x1, x2, y, label=None, tick=2.0, txt=4.0):
        """Horizontal dimension line from x1..x2 at height y."""
        self.line(x1, y, x2, y, "DIM")
        for x in (x1, x2):                       # 45-degree ticks
            self.line(x - tick, y - tick, x + tick, y + tick, "DIM")
        s = label if label is not None else _ftin(abs(x2 - x1))
        self.text((x1 + x2) / 2, y + tick, txt, s, "DIM",
                  halign="center", valign="bottom")

    def dim_v(self, y1, y2, x, label=None, tick=2.0, txt=4.0):
        """Vertical dimension line from y1..y2 at offset x."""
        self.line(x, y1, x, y2, "DIM")
        for y in (y1, y2):
            self.line(x - tick, y - tick, x + tick, y + tick, "DIM")
        s = label if label is not None else _ftin(abs(y2 - y1))
        self.text(x - tick, (y1 + y2) / 2, txt, s, "DIM",
                  halign="right", valign="middle", rotation=90)

    # --- bounds ---------------------------------------------------------
    def bbox(self):
        xs, ys = [], []
        for l in self.lines:
            xs += [l.x1, l.x2]
            ys += [l.y1, l.y2]
        for t in self.texts:
            xs.append(t.x)
            ys.append(t.y)
        if not xs:
            return (0, 0, 1, 1)
        return (min(xs), min(ys), max(xs), max(ys))


def _ftin(inches: float) -> str:
    """Format inches as feet-inches, e.g. 93.0 -> 7'-9\"."""
    inches = round(inches)
    ft, rem = divmod(int(inches), 12)
    if ft and rem:
        return f"{ft}'-{rem}\""
    if ft:
        return f"{ft}'-0\""
    return f"{rem}\""
