"""Framing engine for a simple rectangular gable shed.

Given exterior dimensions + openings, it lays out floor joists and wall studs
(16" on-center), generates the structural member list (for the cut list /
hardware list), and builds dimensioned elevation + plan Drawings.

Lumber actual sizes (inches):
    2x4 -> 1.5 x 3.5     2x6 -> 1.5 x 5.5
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict
from .draw import Drawing

T = 1.5          # actual thickness of dimensional lumber
W2x4 = 3.5
W2x6 = 5.5
OC = 16.0        # on-center stud / joist spacing


@dataclass
class Opening:
    wall: str          # "front" | "back" | "left" | "right"
    kind: str          # "door" | "window"
    width: float       # rough-opening width (in)
    height: float      # rough-opening height (in)
    sill: float = 0.0  # height of bottom of RO above subfloor (0 for door)
    offset: float = 0.0  # left edge of RO from wall's left end


@dataclass
class Shed:
    width: float = 96.0     # front/back wall length (ft*12)
    depth: float = 120.0    # side wall length
    height: float = 96.0    # wall height (subfloor to top of top plate)
    openings: List[Opening] = field(default_factory=list)


@dataclass
class Member:
    category: str   # e.g. "Wall stud", "Floor joist", "Header"
    size: str       # "2x4" | "2x6"
    length: float   # inches
    qty: int


# ----------------------------------------------------------------------
#  Floor framing
# ----------------------------------------------------------------------
def floor_plan(shed: Shed):
    """Joists run across `width`; rim joists run along `depth`."""
    members: List[Member] = []
    d = Drawing("Floor Framing Plan")

    joist_len = shed.width - 2 * T
    # joist lines along depth at 16" OC (inclusive of both ends)
    n = int(shed.depth // OC)
    ys = [i * OC for i in range(n + 1)]
    if ys[-1] != shed.depth:
        ys.append(shed.depth)

    # rim joists (long sides)
    d.rect(0, 0, shed.width, shed.depth, "PLATE")
    members.append(Member("Rim joist", "2x6", shed.depth, 2))

    # transverse joists
    for y in ys:
        yy = min(max(y, T / 2), shed.depth - T / 2)
        d.line(T, yy, shed.width - T, yy, "FRAMING")
    members.append(Member("Floor joist", "2x6", joist_len, len(ys)))

    # dimensions
    d.dim_h(0, shed.width, shed.depth + 8)
    d.dim_v(0, shed.depth, -8)
    d.dim_h(0, OC, -14, label='16" O.C.')
    d.text(shed.width / 2, shed.depth / 2, 5,
           f"FLOOR: {len(ys)} joists @ 2x6", "TEXT",
           halign="center", valign="middle")
    return d, members


# ----------------------------------------------------------------------
#  Wall framing
# ----------------------------------------------------------------------
def _stud_positions(length: float):
    """Left-face x of each common stud: ends + 16" OC centers."""
    xs = [0.0]
    c = OC
    while c < length - T:
        xs.append(c - T / 2)
        c += OC
    xs.append(length - T)
    return xs


def wall_elevation(shed: Shed, wall: str, length: float):
    d = Drawing(f"{wall.title()} Wall Framing")
    members: List[Member] = []
    H = shed.height
    stud_len = H - T - 2 * T          # bottom plate + double top plate
    top_of_studs = T + stud_len

    # plates
    d.rect(0, 0, length, T, "PLATE")                       # bottom plate
    d.rect(0, H - 2 * T, length, T, "PLATE")              # top plate 1
    d.rect(0, H - T, length, T, "PLATE")                  # top plate 2
    members.append(Member("Bottom plate", "2x4", length, 1))
    members.append(Member("Top plate (dbl)", "2x4", length, 2))

    openings = [o for o in shed.openings if o.wall == wall]

    def opening_overlaps(x):
        for o in openings:
            k_l = o.offset - T          # king studs bracket the RO
            k_r = o.offset + o.width + T
            if k_l - T <= x <= k_r:
                return True
        return False

    # common studs (skip those inside an opening zone)
    common = 0
    for x in _stud_positions(length):
        if opening_overlaps(x):
            continue
        d.rect(x, T, T, stud_len, "FRAMING")
        common += 1
    if common:
        members.append(Member("Wall stud", "2x4", stud_len, common))

    # opening framing
    for o in openings:
        ro_l, ro_r = o.offset, o.offset + o.width
        header_h = W2x6
        header_bot = T + o.sill + o.height
        # king studs (full height) just outside the jacks
        for kx in (ro_l - 2 * T, ro_r + T):
            d.rect(kx, T, T, stud_len, "OPENING")
        members.append(Member("King stud", "2x4", stud_len, 2))
        # jack studs (support header) flanking the RO
        jack_len = o.sill + o.height
        for jx in (ro_l - T, ro_r):
            d.rect(jx, T, T, jack_len, "OPENING")
        members.append(Member("Jack stud", "2x4", jack_len, 2))
        # header (2-ply 2x6) across the opening
        d.rect(ro_l - T, header_bot, o.width + 2 * T, header_h, "OPENING")
        members.append(Member("Header", "2x6", o.width + 2 * T, 2))
        # sill + cripples under window
        if o.kind == "window" and o.sill > 0:
            d.rect(ro_l - T, T + o.sill - T, o.width + 2 * T, T, "OPENING")
            members.append(Member("Rough sill", "2x4", o.width + 2 * T, 1))
            ncrip = max(0, int(o.width // OC))
            if ncrip:
                d.rect(ro_l + o.width / 2 - T / 2, T, T, o.sill - T, "OPENING")
                members.append(Member("Cripple (under sill)", "2x4",
                                      o.sill - T, ncrip + 1))
        # cripples above header to top plate
        crip_len = top_of_studs - (header_bot + header_h)
        if crip_len > 1:
            ncrip = max(1, int(o.width // OC))
            d.rect(ro_l + o.width / 2 - T / 2, header_bot + header_h, T,
                   crip_len, "OPENING")
            members.append(Member("Cripple (above header)", "2x4",
                                  crip_len, ncrip + 1))
        # opening RO outline + label
        d.text(o.offset + o.width / 2, header_bot - 6, 4,
               f"{o.kind.upper()} R.O. {_in(o.width)}x{_in(o.height)}",
               "TEXT", halign="center", valign="top")

    # dimensions
    d.dim_h(0, length, -8)
    d.dim_v(0, H, -8)
    d.text(length / 2, H + 8, 5, d.name.upper(), "TEXT",
           halign="center", valign="bottom")
    return d, members


def _in(v):
    return f'{round(v)}"'


# ----------------------------------------------------------------------
#  Assemble the whole shed
# ----------------------------------------------------------------------
def build(shed: Shed):
    drawings = []
    members: List[Member] = []

    fp, fm = floor_plan(shed)
    drawings.append(fp)
    members += fm

    walls = [
        ("front", shed.width),
        ("back", shed.width),
        ("left", shed.depth),
        ("right", shed.depth),
    ]
    for name, length in walls:
        d, m = wall_elevation(shed, name, length)
        drawings.append(d)
        members += m

    return drawings, _merge(members)


def _merge(members: List[Member]) -> List[Member]:
    """Combine identical (category,size,length) rows."""
    bucket: Dict[tuple, Member] = {}
    for m in members:
        key = (m.category, m.size, round(m.length, 3))
        if key in bucket:
            bucket[key].qty += m.qty
        else:
            bucket[key] = Member(m.category, m.size, round(m.length, 3), m.qty)
    return sorted(bucket.values(), key=lambda m: (m.size, -m.length, m.category))
