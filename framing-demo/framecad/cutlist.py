"""Cut-list optimization: pack required member lengths into standard stock
lengths using first-fit-decreasing, accounting for saw kerf."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict
from .framing import Member

STOCK_IN = [96, 120, 144, 192]   # 8', 10', 12', 16'
KERF = 0.125
NOMINAL = {"2x4": (2, 4), "2x6": (2, 6)}


@dataclass
class Stock:
    size: str
    length: float
    cuts: List[float] = field(default_factory=list)
    used: float = 0.0   # consumed incl. kerf

    @property
    def remaining(self):
        return self.length - self.used


@dataclass
class CutPlan:
    size: str
    stock_length: float
    count: int
    pattern: List[float]   # representative cut pattern (one stick)
    drop: float            # waste on that representative stick


def optimize(members: List[Member]):
    """Return (per-size list of CutPlan, summary dict)."""
    by_size: Dict[str, List[float]] = {}
    for m in members:
        by_size.setdefault(m.size, []).extend([m.length] * m.qty)

    plans: List[CutPlan] = []
    summary = {"board_feet": 0.0, "stock_count": 0, "waste_pct": 0.0}
    total_needed = 0.0
    total_stock = 0.0

    for size, pieces in by_size.items():
        pieces.sort(reverse=True)
        sticks: List[Stock] = []
        for p in pieces:
            placed = False
            for s in sticks:
                if s.remaining >= p + (KERF if s.cuts else 0):
                    s.used += p + (KERF if s.cuts else 0)
                    s.cuts.append(p)
                    placed = True
                    break
            if not placed:
                stock_len = next((L for L in STOCK_IN if L >= p), STOCK_IN[-1])
                s = Stock(size, stock_len)
                s.used = p
                s.cuts.append(p)
                sticks.append(s)

        # group identical sticks into CutPlans
        grouped: Dict[tuple, List[Stock]] = {}
        for s in sticks:
            key = (s.length, tuple(sorted(s.cuts, reverse=True)))
            grouped.setdefault(key, []).append(s)
        for (length, pattern), group in sorted(grouped.items(),
                                               key=lambda kv: -kv[0][0]):
            drop = length - sum(pattern) - KERF * max(0, len(pattern) - 1)
            plans.append(CutPlan(size, length, len(group),
                                 list(pattern), round(drop, 2)))

        t, w = NOMINAL[size]
        for s in sticks:
            total_stock += s.length
            total_needed += sum(s.cuts)
            summary["stock_count"] += 1
            summary["board_feet"] += t * w * (s.length / 12) / 12

    summary["board_feet"] = round(summary["board_feet"], 1)
    summary["waste_pct"] = round(100 * (1 - total_needed / total_stock), 1) \
        if total_stock else 0.0
    plans.sort(key=lambda p: (p.size, -p.stock_length))
    return plans, summary


def hardware(members: List[Member], shed):
    """Rough framing hardware / fastener takeoff."""
    joists = sum(m.qty for m in members if m.category == "Floor joist")
    studs = sum(m.qty for m in members
                if m.category in ("Wall stud", "King stud", "Jack stud"))
    wall_lf = (shed.width * 2 + shed.depth * 2) / 12
    return [
        ("Joist hanger (2x6)", "ea", max(0, (joists - 2) * 2)),
        ("Hanger nails (1.5\")", "lb", round(max(0, (joists - 2) * 2) * 10
                                             / 90, 1)),
        ("16d framing nails", "lb", round((studs * 4 + wall_lf * 6) / 90, 1)),
        ("Sill anchor bolts", "ea", max(2, int(wall_lf / 6))),
        ("Hurricane ties", "ea", studs),
    ]
