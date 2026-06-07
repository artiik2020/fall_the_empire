import os
from typing import Dict

from map_model import MapData


def _example_frontline(width_tiles: int, height_tiles: int) -> Dict:
    return {
        "default_x": (width_tiles * 16) / 2,
        "physics": {"max_shift_px": 220.0, "speed_px_s": 60.0, "score_cap": 10},
        "side_a": {"color": "#2ecc71"},
        "side_b": {"color": "#e74c3c"},
    }


def build_example_139x189() -> MapData:
    ts = 16
    w = 139
    h = 189
    fx = (w * ts) / 2

    # Simple starter map: open field + a few walls/barriers.
    return MapData(
        width=w,
        height=h,
        tile_size=ts,
        frontline=_example_frontline(w, h),
        landscapes=[
            {"id": "grass_1", "x": 0, "y": 0, "w": w * ts, "h": h * ts, "kind": "grass"}
        ],
        walls=[
            {"id": "wall_1", "x": fx - 60, "y": 40 * ts / 4, "w": 120, "h": 12, "angle": 0},
            {"id": "wall_2", "x": fx - 60, "y": 90 * ts / 4, "w": 120, "h": 12, "angle": 0},
        ],
        barriers=[
            {"id": "barrier_1", "x": fx + 10, "y": 140 * ts / 4, "w": 80, "h": 10, "kind": "barrier"}
        ],
        buildings=[
            {"id": "bld_a", "team": "A", "x": fx - 260, "y": 40, "w": 40, "h": 40},
            {"id": "bld_b", "team": "B", "x": fx + 220, "y": h * ts - 120, "w": 40, "h": 40},
        ],
        units=[
            # team, unit_type, continuous coords (px)
            {"id": "u_a1", "team": "A", "unit_type": "infantry", "x": fx - 300, "y": 160, "r": 8, "speed": 55, "score": 10},
            {"id": "u_a2", "team": "A", "unit_type": "infantry", "x": fx - 330, "y": 220, "r": 8, "speed": 55, "score": 6},
            {"id": "u_b1", "team": "B", "unit_type": "infantry", "x": fx + 300, "y": 180, "r": 8, "speed": 55, "score": 10},
            {"id": "u_b2", "team": "B", "unit_type": "infantry", "x": fx + 330, "y": 240, "r": 8, "speed": 55, "score": 6},
        ],
    )


def build_example_167x587() -> MapData:
    ts = 16
    w = 167
    h = 587
    fx = (w * ts) / 2

    return MapData(
        width=w,
        height=h,
        tile_size=ts,
        frontline=_example_frontline(w, h),
        landscapes=[
            {"id": "grass_1", "x": 0, "y": 0, "w": w * ts, "h": h * ts, "kind": "grass"}
        ],
        walls=[
            {"id": "wall_long_1", "x": fx - 140, "y": h * ts / 2 - 8, "w": 280, "h": 12, "angle": 0}
        ],
        barriers=[
            {"id": "barrier_long_1", "x": fx + 20, "y": h * ts / 2 + 70, "w": 160, "h": 10, "kind": "barrier"}
        ],
        buildings=[
            {"id": "bld_a", "team": "A", "x": fx - 320, "y": 100, "w": 48, "h": 48},
            {"id": "bld_b", "team": "B", "x": fx + 272, "y": h * ts - 220, "w": 48, "h": 48},
        ],
        units=[
            {"id": "u_a1", "team": "A", "unit_type": "infantry", "x": fx - 380, "y": 260, "r": 8, "speed": 55, "score": 9},
            {"id": "u_a2", "team": "A", "unit_type": "infantry", "x": fx - 410, "y": 340, "r": 8, "speed": 55, "score": 7},
            {"id": "u_b1", "team": "B", "unit_type": "infantry", "x": fx + 380, "y": 260, "r": 8, "speed": 55, "score": 9},
            {"id": "u_b2", "team": "B", "unit_type": "infantry", "x": fx + 410, "y": 340, "r": 8, "speed": 55, "score": 7},
        ],
    )


def ensure_presets_on_disk() -> None:
    """Optional helper: if maps/example_*.json are missing, generate them."""
    base = os.path.join(os.path.dirname(__file__), "maps")
    os.makedirs(base, exist_ok=True)

    from map_model import save_map

    p1 = os.path.join(base, "example_139x189.json")
    if not os.path.exists(p1):
        save_map(build_example_139x189(), p1)

    p2 = os.path.join(base, "example_167x587.json")
    if not os.path.exists(p2):
        save_map(build_example_167x587(), p2)

