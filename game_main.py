import argparse
import math
import os
import sys

import pygame

from map_model import load_map
from editor_game_render import draw_world


SCREEN_W = 1280
SCREEN_H = 720


def clamp(v, a, b):
    return max(a, min(b, v))


def normalize(vx, vy):
    l = math.hypot(vx, vy)
    if l < 1e-9:
        return 0.0, 0.0
    return vx / l, vy / l


def unit_collides(map_data, x: float, y: float, r: float) -> bool:
    # simple circle-vs-rect collision for walls/barriers
    for wall in map_data.walls:
        rx, ry, rw, rh = float(wall.get("x", 0)), float(wall.get("y", 0)), float(wall.get("w", 0)), float(wall.get("h", 0))
        cx = clamp(x, rx, rx + rw)
        cy = clamp(y, ry, ry + rh)
        if (x - cx) ** 2 + (y - cy) ** 2 <= r ** 2:
            return True
    for b in map_data.barriers:
        rx, ry, rw, rh = float(b.get("x", 0)), float(b.get("y", 0)), float(b.get("w", 0)), float(b.get("h", 0))
        cx = clamp(x, rx, rx + rw)
        cy = clamp(y, ry, ry + rh)
        if (x - cx) ** 2 + (y - cy) ** 2 <= r ** 2:
            return True
    return False


def compute_frontline_shift(map_data, units_state):
    physics = map_data.frontline.get("physics", {})
    score_cap = float(physics.get("score_cap", 10))

    default_x = float(map_data.frontline.get("default_x", (map_data.width * map_data.tile_size) / 2))

    a = 0.0
    b = 0.0

    for u in units_state:
        team = u.get("team", "A")
        score = float(u.get("score", 5))
        score = min(score, score_cap)

        ux = u.get("x", 0.0)
        if abs(ux - default_x) < 220:
            if team == "A":
                a += score
            else:
                b += score

    return {"control_a": a, "control_b": b}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", default="maps/example_139x189.json")
    args = parser.parse_args()

    map_path = args.map
    if not os.path.exists(map_path):
        print(f"Map not found: {map_path}")
        sys.exit(1)

    map_data = load_map(map_path)

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("RTS (runtime)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 18)

    cam = pygame.Vector2(0, 0)

    selected_ids = set()

    orders = {}  # id -> (tx, ty)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                wx, wy = mx + cam.x, my + cam.y

                if event.button == 1:
                    clicked = None
                    for u in map_data.units:
                        dx = float(u.get("x", 0)) - wx
                        dy = float(u.get("y", 0)) - wy
                        if dx * dx + dy * dy <= float(u.get("r", 8)) ** 2:
                            clicked = u
                            break
                    if clicked:
                        selected_ids = {clicked["id"]}
                    else:
                        selected_ids.clear()

                if event.button == 3:
                    if selected_ids:
                        for u in map_data.units:
                            if u.get("id") in selected_ids:
                                orders[u.get("id")] = (wx, wy)

            elif event.type == pygame.MOUSEBUTTONUP:
                pass

        keys = pygame.key.get_pressed()
        move_speed = 450
        if keys[pygame.K_a]:
            cam.x -= move_speed * dt
        if keys[pygame.K_d]:
            cam.x += move_speed * dt
        if keys[pygame.K_w]:
            cam.y -= move_speed * dt
        if keys[pygame.K_s]:
            cam.y += move_speed * dt

        # update movement (continuous)
        units_state = map_data.units
        for u in units_state:
            uid = u.get("id")
            if uid not in orders:
                continue
            tx, ty = orders[uid]
            ux = float(u.get("x", 0.0))
            uy = float(u.get("y", 0.0))
            r = float(u.get("r", 8.0))
            speed = float(u.get("speed", 55.0))

            vx, vy = tx - ux, ty - uy
            dist = math.hypot(vx, vy)
            if dist < 2.0:
                del orders[uid]
                continue

            dx, dy = normalize(vx, vy)
            nx = ux + dx * speed * dt
            ny = uy + dy * speed * dt

            # collisions
            if not unit_collides(map_data, nx, ny, r):
                u["x"] = nx
                u["y"] = ny
            else:
                # simple steering: stop order if blocked
                # (later we can implement pathing)
                del orders[uid]

        frontline_state = compute_frontline_shift(map_data, units_state)

        # render
        draw_world(screen, map_data, frontline_state, cam, show_grid=True)

        # highlight selection and draw UI
        for u in map_data.units:
            if u.get("id") in selected_ids:
                x = int(float(u.get("x", 0)) - cam.x)
                y = int(float(u.get("y", 0)) - cam.y)
                r = int(float(u.get("r", 8)))
                pygame.draw.circle(screen, (240, 240, 90), (x, y), r + 3, width=2)

        hud = [
            "RTS controls:",
            "LMB select unit",
            "RMB move order",
            "WASD camera",
            "Esc quit",
        ]
        y = 10
        for line in hud:
            surf = font.render(line, True, (220, 230, 240))
            screen.blit(surf, (10, y))
            y += 18

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()

