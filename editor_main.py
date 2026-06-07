import argparse
import os
import sys

import pygame

from map_model import load_map, save_map
from presets import ensure_presets_on_disk
from editor_game_render import draw_world


SCREEN_W = 1280
SCREEN_H = 720
BG_TOP = (18, 22, 28)


def clamp(v, a, b):
    return max(a, min(b, v))


def get_mouse_world(mouse_pos, cam_x, cam_y):
    mx, my = mouse_pos
    return mx + cam_x, my + cam_y


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", default="maps/example_139x189.json")
    args = parser.parse_args()

    ensure_presets_on_disk()

    map_path = args.map
    if not os.path.exists(map_path):
        print(f"Map not found: {map_path}")
        sys.exit(1)

    map_data = load_map(map_path)

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("RTS Strategy Editor (preview)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 18)

    cam = pygame.Vector2(0, 0)

    # Editor state
    current_tool = "landscape"  # class to place
    # placement mode: click to place
    place_radius = 10

    frontline_state = {"control_a": 10, "control_b": 10}

    dragging = False

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_1:
                    current_tool = "юниты"
                elif event.key == pygame.K_2:
                    current_tool = "ландшафт"
                elif event.key == pygame.K_3:
                    current_tool = "перграды"
                elif event.key == pygame.K_4:
                    current_tool = "стены"
                elif event.key == pygame.K_5:
                    current_tool = "здания"

                elif event.key == pygame.K_s:
                    # save to same file
                    save_map(map_data, map_path)
                elif event.key == pygame.K_g:
                    # spawn example frontline controls
                    frontline_state = {"control_a": 10, "control_b": 10}

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    dragging = True

                if event.button == 1:
                    # left click place
                    wx, wy = get_mouse_world(event.pos, cam.x, cam.y)

                    if current_tool == "ландшафт":
                        map_data.landscapes.append(
                            {"id": f"l_{len(map_data.landscapes)}", "x": wx, "y": wy, "w": 16, "h": 16, "kind": "grass"}
                        )
                    elif current_tool == "перграды":
                        map_data.barriers.append(
                            {"id": f"b_{len(map_data.barriers)}", "x": wx - 25, "y": wy - 5, "w": 50, "h": 10, "kind": "barrier"}
                        )
                    elif current_tool == "стены":
                        map_data.walls.append(
                            {"id": f"w_{len(map_data.walls)}", "x": wx - 40, "y": wy - 6, "w": 80, "h": 12, "angle": 0}
                        )
                    elif current_tool == "здания":
                        map_data.buildings.append(
                            {"id": f"bd_{len(map_data.buildings)}", "team": "A", "x": wx - 20, "y": wy - 20, "w": 40, "h": 40}
                        )
                    elif current_tool == "юниты":
                        map_data.units.append(
                            {
                                "id": f"u_{len(map_data.units)}",
                                "team": "A",
                                "unit_type": "infantry",
                                "x": wx,
                                "y": wy,
                                "r": 8,
                                "speed": 55,
                                "score": 5,
                            }
                        )

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    dragging = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            cam.x -= 400 * dt
        if keys[pygame.K_d]:
            cam.x += 400 * dt
        if keys[pygame.K_w]:
            cam.y -= 400 * dt
        if keys[pygame.K_s]:
            cam.y += 400 * dt

        if dragging:
            mx, my = pygame.mouse.get_pos()
            # Use relative motion
            rel = pygame.mouse.get_rel()
            cam.x -= rel[0]
            cam.y -= rel[1]

        # render
        draw_world(screen, map_data, frontline_state, cam, show_grid=True)

        # UI overlay
        hud = [
            "Editor controls:",
            "LMB: place object",
            "RMB drag camera",
            "WASD: move camera",
            "1: Юниты | 2: Ландшафт | 3: Перграды | 4: Стены | 5: Здания",
            "S: save map",
            f"Tool: {current_tool}",
            f"Map: {map_path}",
            f"Sizes: {map_data.width}x{map_data.height} tiles",
            "(Frontline preview is static; in game it updates dynamically.)",
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

