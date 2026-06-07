import math
from typing import Dict, List, Tuple

import pygame


def rect_from_item(item: Dict) -> pygame.Rect:
    x = float(item.get("x", 0))
    y = float(item.get("y", 0))
    w = float(item.get("w", 0))
    h = float(item.get("h", 0))
    return pygame.Rect(int(x), int(y), int(w), int(h))


def draw_layer(screen: pygame.Surface, layer: List[Dict], color: Tuple[int, int, int]) -> None:
    for it in layer:
        r = rect_from_item(it)
        pygame.draw.rect(screen, color, r, width=2)


def draw_frontline(screen: pygame.Surface, frontline: Dict, control_a: float, control_b: float, x0: float, y0: float) -> None:
    """Simple frontline rendering: a vertical-ish segment at x = default_x + shift.

    shift: powered by user rule: each side has up to score_cap points contributions; if ratio > 2 => move opposite.
    """
    physics = frontline.get("physics", {})
    default_x = float(frontline.get("default_x", x0))
    max_shift = float(physics.get("max_shift_px", 200.0))

    # control values in [0..score_cap] roughly; we convert to pressure
    # ratio logic: if one side is more than 2x => push away (reverse shift)
    a = max(control_a, 0.0)
    b = max(control_b, 0.0)
    eps = 1e-6

    ratio_ab = (b + eps) / (a + eps)
    ratio_ba = (a + eps) / (b + eps)

    # baseline shift from delta
    delta = a - b
    shift = delta

    # apply reverse rule
    if a > 0 and b > 0:
        if b > 2 * a:
            # b dominates => shift should move toward side B (i.e. reverse from delta sign)
            shift = -(delta)
        elif a > 2 * b:
            shift = -(delta)

    # normalize by expected range (score_cap)
    score_cap = float(physics.get("score_cap", 10))
    shift_norm = shift / (2 * score_cap)
    shift_px = max(-1.0, min(1.0, shift_norm)) * max_shift

    x = int(default_x + shift_px)
    x = max(0, min(screen.get_width() - 1, x))

    col_a = pygame.Color(frontline.get("side_a", {}).get("color", "#2ecc71"))
    col_b = pygame.Color(frontline.get("side_b", {}).get("color", "#e74c3c"))

    pygame.draw.line(screen, col_a, (x, 0), (x, screen.get_height()), width=3)
    pygame.draw.line(screen, col_b, (x + 1, 0), (x + 1, screen.get_height()), width=1)


def draw_world(
    screen: pygame.Surface,
    map_data,
    frontline_state: Dict,
    cam: pygame.Vector2,
    show_grid: bool = True,
) -> None:
    w, h = int(map_data.width * map_data.tile_size), int(map_data.height * map_data.tile_size)

    screen.fill((18, 22, 28))

    if show_grid:
        ts = map_data.tile_size
        grid_col = (35, 42, 54)
        for gx in range(0, w, ts):
            sx = gx - cam.x
            pygame.draw.line(screen, grid_col, (sx, 0), (sx, screen.get_height()))
        for gy in range(0, h, ts):
            sy = gy - cam.y
            pygame.draw.line(screen, grid_col, (0, sy), (screen.get_width(), sy))

    # landscapes (simple flat)
    pygame.draw.rect(screen, (30, 120, 60), pygame.Rect(-cam.x, -cam.y, w, h), width=0)

    # barriers/walls
    for wall in map_data.walls:
        r = rect_from_item(wall)
        r.topleft = (r.x - cam.x, r.y - cam.y)
        pygame.draw.rect(screen, (200, 200, 210), r, width=2)

    for b in map_data.barriers:
        r = rect_from_item(b)
        r.topleft = (r.x - cam.x, r.y - cam.y)
        pygame.draw.rect(screen, (230, 150, 0), r, width=2)

    for bd in map_data.buildings:
        r = rect_from_item(bd)
        r.topleft = (r.x - cam.x, r.y - cam.y)
        team = bd.get("team", "A")
        col = (60, 220, 120) if team == "A" else (230, 80, 80)
        pygame.draw.rect(screen, col, r, width=0)
        pygame.draw.rect(screen, (10, 10, 10), r, width=2)

    # units
    for u in map_data.units:
        x = float(u.get("x", 0)) - cam.x
        y = float(u.get("y", 0)) - cam.y
        r = int(float(u.get("r", 8)))
        team = u.get("team", "A")
        col = (60, 220, 120) if team == "A" else (230, 80, 80)
        pygame.draw.circle(screen, col, (int(x), int(y)), r)

    # frontline render based on control points passed in
    draw_frontline(screen, map_data.frontline, frontline_state.get("control_a", 0), frontline_state.get("control_b", 0), x0=0, y0=0)

    # border
    pygame.draw.rect(screen, (80, 90, 110), pygame.Rect(-cam.x, -cam.y, w, h), width=2)

