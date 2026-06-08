"""Measured drawing set + engineered cut list for the well house.

Controlling dimensions (field-measured, reconciled):
    width (end walls)   W = 36.5"
    length (long walls) L = 45.25"
    eave / wall height  E = 26.75"
    ridge height        R = 38.5"
    flat ridge cap      CAP = 6"
    roof slope          ~19.25" (measured ~20")
    well ring           36" dia concrete
    drum                6" dia, on 3/4" SS shaft + pillow blocks
    lid                 house-side roof plane, ~18" wide x L, piano hinge

"Bulletproof" rebuild: galvanized 1-5/8" strut-channel skeleton, clad with
T&G PVC walls and a standing-seam / aluminum roof. Materials are swappable;
the frame is what makes it strong.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import List
from .draw import Drawing

W = 36.5
L = 45.25
E = 26.75
R = 38.5
CAP = 6.0
RIDGE_L = (W - CAP) / 2          # 15.25  left edge of flat ridge
RIDGE_R = (W + CAP) / 2          # 21.25
RISE = R - E                     # 11.75
SLOPE = math.hypot((W - CAP) / 2, RISE)   # ~19.25
RING_DIA = 36.0
RING_WALL = 3.0
DRUM_DIA = 6.0
DRUM_AXIS_Y = 31.0
CRANK_DIA = 4.0
OH = 0.75                        # roof overhang (eaves + rake)
_DROP = OH * RISE / ((W - CAP) / 2)   # vertical drop of roof over the overhang


@dataclass
class Part:
    category: str
    material: str
    length: float    # inches (0 = area/count item)
    qty: int
    note: str = ""


# ----------------------------------------------------------------------
#  Drawings
# ----------------------------------------------------------------------
def _gable_outline(d: Drawing, layer="FRAMING", oh=0.0):
    drop = oh * RISE / ((W - CAP) / 2)
    le, re = (-oh, E - drop), (W + oh, E - drop)   # roof eave edges
    # walls
    d.line(0, 0, W, 0, layer)
    d.line(0, 0, 0, E, layer)
    d.line(W, 0, W, E, layer)
    d.line(0, E, W, E, layer)                       # eave / wall-top line
    # roof (with optional overhang)
    pts = [le, (RIDGE_L, R), (RIDGE_R, R), re]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        d.line(x1, y1, x2, y2, layer)
    if oh:                                          # fascia returns
        d.line(le[0], le[1], le[0], le[1] - 2, layer)
        d.line(re[0], re[1], re[0], re[1] - 2, layer)


def end_elevation():
    d = Drawing("End Elevation - Crank Side")
    _gable_outline(d, "PLATE", oh=OH)
    # horizontal cladding lines on the wall portion
    y = 6.0
    while y < E:
        d.line(0, y, W, y, "FRAMING")
        y += 6.0
    d.line(0, E, W, E, "FRAMING")            # eave line
    # ridge cap
    d.line(RIDGE_L, R, RIDGE_R, R, "OPENING")
    # drum end (6" dia) + crank hole (4" dia) on this end
    _circle(d, W / 2, DRUM_AXIS_Y, DRUM_DIA / 2, "OPENING")
    _circle(d, W / 2, DRUM_AXIS_Y, CRANK_DIA / 2, "OPENING")
    d.line(W / 2, DRUM_AXIS_Y, W / 2 + 7, DRUM_AXIS_Y - 7, "OPENING")  # crank arm
    d.text(W / 2, DRUM_AXIS_Y - 9, 3, "CRANK / DRUM AXIS", "TEXT",
           halign="center", valign="top")
    # dimensions
    d.dim_h(0, W, -7, label='36-1/2"')
    d.dim_v(0, E, -7, label='26-3/4"')
    d.dim_v(0, R, W + 7, label='38-1/2"')
    d.dim_h(RIDGE_L, RIDGE_R, R + 6, label='6"')
    # slope callout + overhang note
    mx, my = (W + RIDGE_R) / 2, (E + R) / 2
    d.text(mx + 2, my, 3, '~20" slope (9:12)', "DIM", halign="left",
           valign="middle")
    d.text(W + OH, E - _DROP - 3, 2.5, '3/4" overhang typ.', "DIM",
           halign="right", valign="top")
    d.text(W / 2, R + 12, 4, "END ELEVATION (CRANK SIDE)", "TEXT",
           halign="center", valign="bottom")
    return d


def side_elevation():
    d = Drawing("Side Elevation")
    # long wall rectangle
    d.rect(0, 0, L, E, "PLATE")
    y = 6.0
    while y < E:
        d.line(0, y, L, y, "FRAMING")
        y += 6.0
    # roof band (projected): eave line at E, ridge cap line at R,
    # extended by the 3/4" rake overhang at both ends
    d.line(0, E, L, E, "FRAMING")
    d.line(-OH, R, L + OH, R, "OPENING")     # ridge cap (projected) + overhang
    d.line(-OH, E, -OH, R, "FRAMING")
    d.line(L + OH, E, L + OH, R, "FRAMING")
    d.text(L + OH, R + 2, 2.5, '3/4" overhang', "DIM",
           halign="right", valign="bottom")
    d.text(L / 2, (E + R) / 2, 3,
           "ROOF SLOPES TOWARD VIEWER (lid = house-side plane)",
           "DIM", halign="center", valign="middle")
    # hinge + lid-open arc
    d.line(0, R, -1, R, "OPENING")
    _arc(d, 3, R, 14, 90, 150, "DIM")
    d.text(8, R + 10, 3, 'LID LIFTS (18" panel, gas struts)', "TEXT",
           halign="left", valign="bottom")
    # dimensions
    d.dim_h(0, L, -7, label='45-1/4"')
    d.dim_v(0, E, -7, label='26-3/4"')
    d.dim_v(0, R, L + 7, label='38-1/2"')
    d.text(L / 2, R + 14, 4, "SIDE ELEVATION", "TEXT",
           halign="center", valign="bottom")
    return d


def roof_plan():
    d = Drawing("Roof Plan")
    # plan: x = width (36.5), y = length (45.25)
    d.rect(-OH, -OH, W + 2 * OH, L + 2 * OH, "PLATE")   # roof edge w/ overhang
    d.rect(0, 0, W, L, "DIM")                           # wall footprint below
    # ridge band
    d.line(RIDGE_L, 0, RIDGE_L, L, "OPENING")
    d.line(RIDGE_R, 0, RIDGE_R, L, "OPENING")
    # standing-seam lines on each plane
    for x in _seq(2.5, RIDGE_L - 1, 4):
        d.line(x, 0, x, L, "FRAMING")
    for x in _seq(RIDGE_R + 1.5, W - 2, 4):
        d.line(x, 0, x, L, "FRAMING")
    # lid = right-hand (house side) plane, hinge at RIDGE_R
    d.line(RIDGE_R, 0, RIDGE_R, L, "OPENING")
    d.text((RIDGE_R + W) / 2, L / 2, 3, "LIFTING LID", "TEXT",
           halign="center", valign="middle", rotation=90)
    d.text((0 + RIDGE_L) / 2, L / 2, 3, "FIXED ROOF", "TEXT",
           halign="center", valign="middle", rotation=90)
    # hinge ticks along RIDGE_R
    for y in _seq(4, L - 2, 9):
        d.line(RIDGE_R - 1, y, RIDGE_R + 1, y, "DIM")
    # dimensions
    d.dim_h(0, W, -7, label='36-1/2"')
    d.dim_v(0, L, -7, label='45-1/4"')
    d.dim_h(RIDGE_L, RIDGE_R, L + 6, label='6" ridge')
    d.dim_h(RIDGE_R, W, L + 12, label='~18" lid')
    d.text(W + OH, -OH - 2, 2.5, '3/4" overhang typ.', "DIM",
           halign="right", valign="top")
    d.text(W / 2, L + 18, 4, "ROOF PLAN", "TEXT",
           halign="center", valign="bottom")
    return d


def cross_section():
    d = Drawing("Cross Section")
    xc = W / 2
    # ground line
    d.line(-6, 0, W + 6, 0, "DIM")
    # house end profile (section)
    _gable_outline(d, "PLATE")
    d.line(RIDGE_L, R, RIDGE_R, R, "OPENING")
    # well ring (concrete) section: two walls, top 4" above grade
    ro, ri = RING_DIA / 2, RING_DIA / 2 - RING_WALL
    top, bot = 4, -20
    for s in (-1, 1):
        d.line(xc + s * ro, bot, xc + s * ro, top, "FRAMING")
        d.line(xc + s * ri, bot, xc + s * ri, top, "FRAMING")
        d.line(xc + s * ro, top, xc + s * ri, top, "FRAMING")
    d.text(xc, bot - 2, 3, 'WELL RING 36" DIA CONCRETE', "TEXT",
           halign="center", valign="top")
    # drum (6") on axis + shaft
    _circle(d, xc, DRUM_AXIS_Y, DRUM_DIA / 2, "OPENING")
    d.line(0, DRUM_AXIS_Y, W, DRUM_AXIS_Y, "DIM")
    d.text(xc + 5, DRUM_AXIS_Y + 4, 3, '6" DRUM on 3/4" SS shaft',
           "TEXT", halign="left", valign="bottom")
    # rope from drum into well
    d.line(xc - 1, DRUM_AXIS_Y - DRUM_DIA / 2, xc - 1, top - 14, "DIM")
    d.text(xc - 2, (DRUM_AXIS_Y + top) / 2, 2.5, "rope", "DIM",
           halign="right", valign="middle", rotation=90)
    # pillow-block note
    d.text(2, DRUM_AXIS_Y + 4, 2.5, "pillow blocks @ end walls", "TEXT",
           halign="left", valign="bottom")
    # dimensions
    d.dim_h(xc - ro, xc + ro, bot - 8, label='36" ring')
    d.dim_v(0, R, W + 8, label='38-1/2"')
    d.text(W / 2, R + 10, 4, "CROSS SECTION", "TEXT",
           halign="center", valign="bottom")
    return d


STRUT = 1.625        # strut channel width/height (1-5/8")
GAUGE = 0.13         # drawn wall thickness for sections


def _strut_member(d, x1, y1, x2, y2, layer="OPENING", w=STRUT):
    """Draw a strut member to true width as a rectangle around its centerline."""
    dx, dy = x2 - x1, y2 - y1
    ln = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / ln * w / 2, dx / ln * w / 2
    c = [(x1 + nx, y1 + ny), (x2 + nx, y2 + ny),
         (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)]
    for a, b in zip(c, c[1:] + c[:1]):
        d.line(a[0], a[1], b[0], b[1], layer)


def _strut_square(d, cx, cy, layer, s=STRUT):
    d.rect(cx - s / 2, cy - s / 2, s, s, layer)


def _hatch(d, x0, y0, x1, y1, layer="DIM", step=2.0):
    """45-degree hatch clipped to a rectangle (concrete symbol)."""
    b = y0 - x1
    bmax = y1 - x0
    while b <= bmax:
        xa, ya = x0, x0 + b
        if ya < y0:
            ya, xa = y0, y0 - b
        if ya > y1:
            ya, xa = y1, y1 - b
        xb, yb = x1, x1 + b
        if yb < y0:
            yb, xb = y0, y0 - b
        if yb > y1:
            yb, xb = y1, y1 - b
        if x0 - 0.01 <= xa <= x1 + 0.01 and x0 - 0.01 <= xb <= x1 + 0.01:
            d.line(xa, ya, xb, yb, layer)
        b += step


def _strut_section(d, ox, oy, sc, layer="PLATE"):
    """Draw a true 1-5/8" C-channel cross-section at (ox,oy), scaled by sc."""
    s, t = STRUT, GAUGE
    sl, sr, lip = 0.53, 1.095, 0.32      # slot edges, lip depth

    def P(x, y):
        return (ox + x * sc, oy + y * sc)

    def L(x1, y1, x2, y2, lay=layer):
        a, b = P(x1, y1), P(x2, y2)
        d.line(a[0], a[1], b[0], b[1], lay)

    # outer outline with inturned lips
    L(0, 0, s, 0); L(0, 0, 0, s); L(s, 0, s, s)
    L(0, s, sl, s); L(s, s, sr, s)
    L(sl, s, sl, s - lip); L(sl, s - lip, sl + 0.12, s - lip)
    L(sr, s, sr, s - lip); L(sr, s - lip, sr - 0.12, s - lip)
    # inner faces (shows gauge/thickness)
    L(t, t, s - t, t, "FRAMING"); L(t, t, t, s - t, "FRAMING")
    L(s - t, t, s - t, s - t, "FRAMING")
    L(t, s - t, sl, s - t, "FRAMING"); L(s - t, s - t, sr, s - t, "FRAMING")
    # dims (small absolute ticks; section is ~8" as drawn)
    tk, tx = 0.6, 1.4
    da, db = P(0, 0), P(s, 0)
    d.dim_h(da[0], db[0], oy - 0.5 * sc, label='1-5/8"', tick=tk, txt=tx)
    d.dim_v(P(0, 0)[1], P(0, s)[1], ox - 0.5 * sc, label='1-5/8"',
            tick=tk, txt=tx)
    ga, gb = P(sl, s), P(sr, s)
    d.dim_h(ga[0], gb[0], oy + (s + 0.5) * sc, label='9/16"', tick=tk, txt=tx)


def frame_diagram():
    """Strut-channel skeleton drawn to true member thickness."""
    d = Drawing("Structural Frame - Strut Channel")
    # ---------- END FRAME (left) ----------
    _strut_member(d, 0, 0, W, 0)                  # base rail
    _strut_member(d, 0, 0, 0, E)                  # corner post L
    _strut_member(d, W, 0, W, E)                  # corner post R
    _strut_member(d, 0, E, W, E)                  # eave rail
    _strut_member(d, 0, E, RIDGE_L, R)           # rafter L
    _strut_member(d, W, E, RIDGE_R, R)           # rafter R
    _strut_square(d, RIDGE_L, R, "OPENING")      # ridge rail (end-on)
    _strut_square(d, RIDGE_R, R, "OPENING")
    d.text(W / 2, -5, 3, "END FRAME", "TEXT", halign="center", valign="top")
    d.text(W / 2, R + 4, 2.3, '6" ridge = 2 rails (shown end-on)', "DIM",
           halign="center", valign="bottom")
    d.text(-3, E / 2, 2.3, "corner post", "DIM", halign="right",
           valign="middle")
    d.dim_v(0, E, -7, label='26-3/4"')
    d.dim_v(0, R, W + 7, label='38-1/2"')
    d.dim_h(0, W, -13, label='36-1/2"')

    # ---------- SIDE FRAME (right) ----------  wall to eave, roof above
    ox = W + 20
    _strut_member(d, ox + 0, 0, ox + L, 0)        # base rail
    _strut_member(d, ox + 0, E, ox + L, E)        # eave rail (top of wall)
    for x in (0, L / 2, L):
        _strut_member(d, ox + x, 0, ox + x, E)    # wall posts
        _strut_member(d, ox + x, E, ox + x, R)    # rafters, edge-on
    _strut_member(d, ox + 0, R, ox + L, R)        # ridge rail
    d.text(ox + L / 2, -5, 3, "SIDE FRAME", "TEXT",
           halign="center", valign="top")
    d.text(ox + L / 2, R + 4, 2.3, 'ridge rail (2 @ 6" apart, overlap in view)',
           "DIM", halign="center", valign="bottom")
    d.text(ox + L / 2, (E + R) / 2, 2.1, "rafters shown edge-on", "DIM",
           halign="center", valign="middle")
    d.dim_v(0, E, ox - 4, label='wall 26-3/4"')
    d.dim_h(ox + 0, ox + L / 2, -7, label='22-5/8" (mid post)')
    d.dim_h(ox + 0, ox + L, -13, label='45-1/4"')

    d.text((W + ox + L) / 2 - 3, R + 12, 3.5,
           'STRUCTURAL FRAME — 1-5/8" STRUT CHANNEL (drawn to thickness)',
           "TEXT", halign="center", valign="bottom")
    return d


def strut_detail():
    """True strut cross-section + a typical bolted corner connection."""
    d = Drawing("Strut Section + Connection")
    sc = 5.0
    _strut_section(d, 0, 0, sc)
    sa = STRUT * sc
    d.text(sa / 2, -1.6 * sc, 0.42 * sc,
           "SECTION — 12 ga galv. (Unistrut P1000 / equiv.)", "TEXT",
           halign="center", valign="top")

    # ---- typical corner connection (post + rail + gusset + bolts) ----
    bx = sa + 10
    _strut_member(d, bx, 0, bx, 9 * 1.0 * 1, "PLATE")  # vertical post
    _strut_member(d, bx, 8, bx + 10, 8, "PLATE")       # horizontal rail
    d.rect(bx - 1.0, 1.3, 6.2, 6.4, "DIM")             # gusset plate outline
    for hx, hy in [(bx, 3), (bx, 5.6), (bx + 2.4, 8), (bx + 4.8, 8)]:
        _circle(d, hx, hy, 0.32, "OPENING")            # bolts
    # spring-nut symbol inside channel (small turned bar)
    d.rect(bx - 0.55, 2.6, 1.1, 0.8, "FRAMING")
    d.text(bx - 1.2, 3.0, 1.0, "spring nut (turns into channel)", "DIM",
           halign="right", valign="middle")
    d.text(bx + 3.5, 9.6, 1.0, '3/8" SS bolts (x4)', "TEXT",
           halign="center", valign="bottom")
    d.text(bx + 5, 1.1, 1.0, "90-deg corner gusset", "TEXT",
           halign="center", valign="top")
    d.text((sa + bx + 10) / 2, 13, 1.4,
           "STRUT SECTION + TYPICAL CONNECTION", "TEXT",
           halign="center", valign="bottom")
    return d


def foundation_detail():
    """Section: strut base anchored to a concrete collar / pad."""
    d = Drawing("Foundation / Anchoring Detail")
    # concrete pad + grade
    _hatch(d, -2, -8, 16, 0, "DIM", step=2.0)
    d.rect(-2, -8, 18, 8, "PLATE")
    d.line(-5, 0, 19, 0, "FRAMING")                      # grade line
    d.text(19, 0, 1.0, "grade", "DIM", halign="left", valign="bottom")
    d.text(7, -8.9, 1.1, "CONCRETE COLLAR / PAD (or existing well ring)",
           "TEXT", halign="center", valign="top")
    # base rail lying on concrete (runs along the wall)
    _strut_member(d, 2, STRUT / 2, 12, STRUT / 2, "OPENING")
    d.text(12.3, STRUT / 2, 1.0, "strut base rail", "TEXT",
           halign="left", valign="middle")
    # post rising off the base rail
    _strut_member(d, 7, STRUT, 7, 14, "PLATE")
    d.text(7, 14.4, 1.0, "corner post (strut)", "TEXT",
           halign="center", valign="bottom")
    # wedge anchor beside post, through base into concrete
    ax = 5.0
    d.line(ax, 1.9, ax, -6, "OPENING")                  # shank
    for ty in range(0, 12):                              # thread ticks
        yy = -6 + ty * 0.5
        if yy < 0.2:
            d.line(ax - 0.18, yy, ax + 0.18, yy + 0.12, "OPENING")
    d.rect(ax - 0.6, 1.55, 1.2, 0.35, "OPENING")        # washer
    d.rect(ax - 0.45, 1.9, 0.9, 0.5, "OPENING")         # nut
    d.line(ax - 0.3, -6, ax - 0.7, -5.2, "OPENING")     # expansion clip
    d.line(ax + 0.3, -6, ax + 0.7, -5.2, "OPENING")
    d.dim_v(-6, 0, -3.5, label='~5" embed')
    d.text(ax - 1.0, 2.6, 1.0, '3/8-1/2" SS wedge anchor', "TEXT",
           halign="right", valign="bottom")
    d.text(7, 16, 1.4, "FOUNDATION / ANCHORING DETAIL", "TEXT",
           halign="center", valign="bottom")
    return d


def bearing_detail():
    """Drum + shaft on pillow blocks, plus a pillow-block end view."""
    d = Drawing("Drum + Bearing Mount Detail")
    cy = 0.0
    ro = DRUM_DIA / 2
    wall = 0.28
    d0, d1 = 5, L - 5                                     # drum ends
    # drum body with wall thickness
    d.rect(d0, cy - ro, d1 - d0, DRUM_DIA, "PLATE")
    d.line(d0, cy - ro + wall, d1, cy - ro + wall, "FRAMING")
    d.line(d0, cy + ro - wall, d1, cy + ro - wall, "FRAMING")
    d.text((d0 + d1) / 2, cy, 2.2, '6" Sch-40 PVC drum (or log)', "TEXT",
           halign="center", valign="middle")
    # HDPE end disks
    for ex in (d0, d1):
        d.rect(ex - 0.6, cy - ro, 0.6, DRUM_DIA, "OPENING")
    # shaft through it
    d.line(-5, cy + 0.375, L + 5, cy + 0.375, "OPENING")
    d.line(-5, cy - 0.375, L + 5, cy - 0.375, "OPENING")
    d.text(L / 2, cy - ro - 2, 1.8, '3/4" 316 SS shaft', "DIM",
           halign="center", valign="top")
    # pillow blocks just outside the drum
    for px in (1.5, L - 1.5):
        _pillow_block(d, px, cy)
    # end-frame strut (eave rail) the blocks bolt to
    for ex in (-1, L + 1):
        _strut_square(d, ex, cy - ro - 4, "FRAMING")
    d.text(L + 1, cy - ro - 6, 1.4, "bolts to end-frame rail", "DIM",
           halign="center", valign="top")
    # crank at left end
    d.line(-5, cy, -5, cy - 4, "OPENING")
    d.line(-5, cy - 4, -3, cy - 4, "OPENING")
    d.text(-5, cy + 2, 1.6, "crank", "TEXT", halign="center", valign="bottom")

    # ---- pillow-block END VIEW (below) ----
    ex0, ey0 = L / 2, cy - ro - 22
    d.rect(ex0 - 3, ey0 - 1, 6, 1.2, "PLATE")            # base flange
    _circle(d, ex0 - 2.2, ey0 - 0.4, 0.4, "OPENING")     # bolt slot
    _circle(d, ex0 + 2.2, ey0 - 0.4, 0.4, "OPENING")
    _circle(d, ex0, ey0 + 1.7, 1.9, "PLATE")             # housing OD
    _circle(d, ex0, ey0 + 1.7, 0.5, "OPENING")           # shaft 3/4"
    d.line(ex0 - 1.9, ey0 + 0.2, ex0 - 1.9, ey0 + 1.7, "PLATE")
    d.line(ex0 + 1.9, ey0 + 0.2, ex0 + 1.9, ey0 + 1.7, "PLATE")
    d.text(ex0 + 4, ey0 + 1.7, 1.4, "pillow block (end view)", "TEXT",
           halign="left", valign="middle")
    d.text(ex0, ey0 - 2.5, 1.2, "sealed 3/4\" bore + 2 mounting bolts",
           "DIM", halign="center", valign="top")

    d.text(L / 2, cy + ro + 4, 2.0, "DRUM + BEARING MOUNT DETAIL", "TEXT",
           halign="center", valign="bottom")
    return d


def _pillow_block(d, px, cy):
    ro = DRUM_DIA / 2
    base_y = cy - ro - 3
    d.rect(px - 2.5, base_y, 5, 1.0, "PLATE")            # base
    _circle(d, px - 1.8, base_y + 0.5, 0.3, "OPENING")
    _circle(d, px + 1.8, base_y + 0.5, 0.3, "OPENING")
    _circle(d, px, cy, 1.6, "PLATE")                     # housing
    d.line(px - 1.6, cy, px - 2.0, base_y + 1.0, "PLATE")
    d.line(px + 1.6, cy, px + 2.0, base_y + 1.0, "PLATE")


# ----------------------------------------------------------------------
#  Lid hinge + gas-strut detail (2D section through the ridge)
# ----------------------------------------------------------------------
def lid_detail():
    d = Drawing("Lid Hinge + Gas Strut Detail")
    hinge = (RIDGE_R, R)
    eave = (W + OH, E - _DROP)
    vx, vy = eave[0] - hinge[0], eave[1] - hinge[1]

    # fixed roof + ridge cap
    d.line(0, E, RIDGE_L, R, "PLATE")
    d.line(RIDGE_L, R, RIDGE_R, R, "PLATE")
    d.line(0, E, 0, E - 8, "PLATE")            # wall stub
    # lid closed
    d.line(hinge[0], hinge[1], eave[0], eave[1], "OPENING")
    _circle(d, hinge[0], hinge[1], 0.9, "OPENING")
    _circle(d, hinge[0], hinge[1], 0.4, "OPENING")
    d.text(hinge[0] - 2, hinge[1] + 3, 2.5,
           "piano hinge 316 SS (full length)", "TEXT",
           halign="right", valign="bottom")

    # lid open ~75 deg about hinge
    ang = math.radians(75)
    ox = hinge[0] + vx * math.cos(ang) - vy * math.sin(ang)
    oy = hinge[1] + vx * math.sin(ang) + vy * math.cos(ang)
    _dash2(d, hinge[0], hinge[1], ox, oy, "DIM")
    d.text(ox, oy + 2, 2.5, "lid open ~75 deg", "DIM",
           halign="center", valign="bottom")
    a0 = math.degrees(math.atan2(vy, vx))
    _arc(d, hinge[0], hinge[1], 9, a0, a0 + 75, "DIM")

    # gas strut: lower mount on eave rail, upper mount mid-lid
    Lm = (W - 1.5, E - 9)
    f = 0.5
    up_c = (hinge[0] + vx * f, hinge[1] + vy * f)
    up_o = (hinge[0] + (vx * f) * math.cos(ang) - (vy * f) * math.sin(ang),
            hinge[1] + (vx * f) * math.sin(ang) + (vy * f) * math.cos(ang))
    for p in (Lm, up_c, up_o):
        _circle(d, p[0], p[1], 0.5, "FRAMING")
    d.line(Lm[0], Lm[1], up_c[0], up_c[1], "FRAMING")      # strut closed
    _dash2(d, Lm[0], Lm[1], up_o[0], up_o[1], "FRAMING")   # strut open
    d.text(Lm[0] - 1, Lm[1] - 2, 2.5, "lower mount on eave rail",
           "TEXT", halign="right", valign="top")
    midx, midy = (Lm[0] + up_o[0]) / 2, (Lm[1] + up_o[1]) / 2
    d.text(midx + 1, midy, 2.5, "gas strut 20-30 lb (1 per end)",
           "TEXT", halign="left", valign="middle")

    # dims
    d.dim_v(0, R, -6, label='38-1/2"')
    d.text(W / 2, R + 12, 4, "LID HINGE + GAS-STRUT DETAIL", "TEXT",
           halign="center", valign="bottom")
    return d


# ----------------------------------------------------------------------
#  Exploded isometric assembly
# ----------------------------------------------------------------------
def _iso(x, y, z):
    return ((x - y) * 0.866, (x + y) * 0.5 + z)


def _iso_line(d, p1, p2, layer):
    a, b = _iso(*p1), _iso(*p2)
    d.line(a[0], a[1], b[0], b[1], layer)


def _poly3(d, pts, layer):
    for p1, p2 in zip(pts, pts[1:] + pts[:1]):
        _iso_line(d, p1, p2, layer)


def _iso_dash(d, p1, p2, layer, n=40):
    a, b = _iso(*p1), _iso(*p2)
    for i in range(n):
        if i % 2:
            continue
        t0, t1 = i / n, (i + 1) / n
        d.line(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0,
               a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1, layer)


def _iso_circle(d, cx, cy, cz, r, plane, layer, seg=24):
    pts = []
    for i in range(seg + 1):
        a = 2 * math.pi * i / seg
        if plane == "xy":
            p = (cx + r * math.cos(a), cy + r * math.sin(a), cz)
        else:  # 'xz', a ring facing along y
            p = (cx + r * math.cos(a), cy, cz + r * math.sin(a))
        pts.append(_iso(*p))
    for q1, q2 in zip(pts, pts[1:]):
        d.line(q1[0], q1[1], q2[0], q2[1], layer)


def _label_iso(d, x, y, z, s):
    p = _iso(x, y, z)
    d.text(p[0] + 3, p[1], 3, s, "TEXT", halign="left", valign="middle")


def _box_frame(d, z):
    layer = "OPENING"
    base = [(0, 0), (W, 0), (W, L), (0, L)]
    for (x1, y1), (x2, y2) in zip(base, base[1:] + base[:1]):
        _iso_line(d, (x1, y1, z), (x2, y2, z), layer)
        _iso_line(d, (x1, y1, z + E), (x2, y2, z + E), layer)
        _iso_line(d, (x1, y1, z), (x1, y1, z + E), layer)
    for y in (0, L / 2, L):
        _iso_line(d, (0, y, z + E), (RIDGE_L, y, z + R), layer)
        _iso_line(d, (W, y, z + E), (RIDGE_R, y, z + R), layer)
        _iso_line(d, (RIDGE_L, y, z + R), (RIDGE_R, y, z + R), layer)
    _iso_line(d, (RIDGE_L, 0, z + R), (RIDGE_L, L, z + R), layer)
    _iso_line(d, (RIDGE_R, 0, z + R), (RIDGE_R, L, z + R), layer)


def _wall_shell(d, z):
    layer = "PLATE"
    for x in (0, W):
        _iso_line(d, (x, 0, z), (x, L, z), layer)
        _iso_line(d, (x, 0, z + E), (x, L, z + E), layer)
        _iso_line(d, (x, 0, z), (x, 0, z + E), layer)
        _iso_line(d, (x, L, z), (x, L, z + E), layer)
    for y in (0, L):
        _iso_line(d, (0, y, z), (W, y, z), layer)
        _iso_line(d, (0, y, z + E), (W, y, z + E), layer)
        _iso_line(d, (0, y, z), (0, y, z + E), layer)
        _iso_line(d, (W, y, z), (W, y, z + E), layer)
        _iso_line(d, (0, y, z + E), (RIDGE_L, y, z + R), layer)
        _iso_line(d, (RIDGE_L, y, z + R), (RIDGE_R, y, z + R), layer)
        _iso_line(d, (RIDGE_R, y, z + R), (W, y, z + E), layer)


def _drum_iso(d, z):
    layer = "OPENING"
    r, cx = DRUM_DIA / 2, W / 2
    y0, y1 = 4, L - 4
    _iso_circle(d, cx, y0, z, r, "xz", layer)
    _iso_circle(d, cx, y1, z, r, "xz", layer)
    for a in (0, 90, 180, 270):
        ax = cx + r * math.cos(math.radians(a))
        az = z + r * math.sin(math.radians(a))
        _iso_line(d, (ax, y0, az), (ax, y1, az), layer)
    _iso_line(d, (cx, y0, z), (cx, -4, z), layer)        # shaft + crank end
    _iso_line(d, (cx, y1, z), (cx, L + 4, z), layer)


def _roof_iso(d, z):
    fp = [(0, 0, z), (RIDGE_L, 0, z + RISE),
          (RIDGE_L, L, z + RISE), (0, L, z)]
    lp = [(RIDGE_R, 0, z + RISE), (W, 0, z),
          (W, L, z), (RIDGE_R, L, z + RISE)]
    _poly3(d, fp, "PLATE")
    _poly3(d, lp, "OPENING")
    _iso_line(d, (RIDGE_L, 0, z + RISE), (RIDGE_R, 0, z + RISE), "OPENING")
    _iso_line(d, (RIDGE_L, L, z + RISE), (RIDGE_R, L, z + RISE), "OPENING")
    _label_iso(d, RIDGE_R, L / 2, z + RISE, "LID (lifts)")


def exploded_iso():
    d = Drawing("Exploded Assembly")
    cx, cy = W / 2, L / 2
    # 1. concrete ring
    _iso_circle(d, cx, cy, 0, RING_DIA / 2, "xy", "FRAMING")
    _iso_circle(d, cx, cy, 8, RING_DIA / 2, "xy", "FRAMING")
    for a in (0, 90, 180, 270):
        ax = cx + RING_DIA / 2 * math.cos(math.radians(a))
        ay = cy + RING_DIA / 2 * math.sin(math.radians(a))
        _iso_line(d, (ax, ay, 0), (ax, ay, 8), "FRAMING")
    _label_iso(d, cx + RING_DIA / 2, cy, 4, '36" CONCRETE RING')
    # 2. strut frame
    _box_frame(d, 55)
    _label_iso(d, W, 0, 55 + E / 2, "STRUT-CHANNEL FRAME")
    # 3. wall cladding
    _wall_shell(d, 110)
    _label_iso(d, W, 0, 110 + E / 2, "WALL CLADDING")
    # 4. drum + shaft
    _drum_iso(d, 160)
    _label_iso(d, cx, L, 160, '6" DRUM + 3/4" SS SHAFT')
    # 5. roof + lid
    _roof_iso(d, 200)
    # explode centerline
    _iso_dash(d, (0, 0, 0), (0, 0, 235), "DIM")
    t = _iso(cx, cy, 250)
    d.text(t[0], t[1] + 4, 5, "EXPLODED ASSEMBLY (build order, bottom-up)",
           "TEXT", halign="center", valign="bottom")
    return d


def _dash2(d, x1, y1, x2, y2, layer, n=16):
    for i in range(n):
        if i % 2:
            continue
        t0, t1 = i / n, (i + 1) / n
        d.line(x1 + (x2 - x1) * t0, y1 + (y2 - y1) * t0,
               x1 + (x2 - x1) * t1, y1 + (y2 - y1) * t1, layer)


# ----------------------------------------------------------------------
#  Engineered material take-off
# ----------------------------------------------------------------------
def parts() -> List[Part]:
    return [
        # --- strut-channel skeleton ---
        Part("Base perimeter (long)", "Strut 1-5/8\"", L, 2),
        Part("Base perimeter (end)", "Strut 1-5/8\"", W, 2),
        Part("Top/eave rail (long)", "Strut 1-5/8\"", L, 2),
        Part("Top/eave rail (end)", "Strut 1-5/8\"", W, 2),
        Part("Corner post", "Strut 1-5/8\"", E, 4),
        Part("Mid gable post", "Strut 1-5/8\"", E, 2),
        Part("Rafter (sloped)", "Strut 1-5/8\"", round(SLOPE), 6),
        Part("Ridge rail", "Strut 1-5/8\"", L, 2),
        Part("Ridge spacer (6\" cap)", "Strut 1-5/8\"", CAP, 3),
    ]


def cladding():
    """Area-based materials (sqft incl. ~15% waste)."""
    walls = (2 * L * E + 2 * (W * E + (W + CAP) / 2 * RISE)) / 144
    # roof planes carry the 3/4" overhang on the eave (down-slope) and rake
    roof = 2 * (L + 2 * OH) * (SLOPE + OH) / 144
    return [
        ("Wall cladding — T&G PVC (AZEK-type)", "sqft", round(walls * 1.15, 1)),
        ("Roof — standing-seam aluminum panel", "sqft", round(roof * 1.15, 1)),
        ("Roof substrate — 1/2\" PVC sheet (under lid)", "sqft",
         round((L + 2 * OH) * (SLOPE + OH) / 144 * 1.15, 1)),
    ]


def hardware():
    return [
        ("Pillow block bearing, 3/4\" 316 SS", "ea", 2),
        ("Shaft, 3/4\" 316 SS x 50\"", "ea", 1),
        ("Drum: 6\" Sch-40 PVC x 42\" (or keep log)", "ea", 1),
        ("HDPE/PVC drum end disk", "ea", 2),
        ("Piano hinge, 316 SS x 45\"", "ea", 1),
        ("Gas strut, 20-30 lb + ball mounts", "set", 2),
        ("Strut 90-deg corner gusset", "ea", 16),
        ("Strut spring nut + 3/8\" SS bolt", "set", 48),
        ("Strut end cap", "ea", 8),
        ("316 SS cladding screws (#8 x 1-5/8\")", "box", 2),
        ("Crank handle assembly (reuse/rebuild)", "ea", 1),
    ]


# ----------------------------------------------------------------------
#  geometry helpers
# ----------------------------------------------------------------------
def _circle(d: Drawing, cx, cy, r, layer, seg=36):
    pts = [(cx + r * math.cos(2 * math.pi * i / seg),
            cy + r * math.sin(2 * math.pi * i / seg)) for i in range(seg + 1)]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        d.line(x1, y1, x2, y2, layer)


def _arc(d: Drawing, cx, cy, r, a0, a1, layer, seg=18):
    pts = []
    for i in range(seg + 1):
        a = math.radians(a0 + (a1 - a0) * i / seg)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        d.line(x1, y1, x2, y2, layer)


def _seq(start, end, step):
    v = start
    while v <= end:
        yield v
        v += step


def all_drawings():
    return [end_elevation(), side_elevation(), roof_plan(),
            cross_section(), frame_diagram(), strut_detail(),
            foundation_detail(), bearing_detail(),
            exploded_iso(), lid_detail()]
