import arcade
import json
from game_logic.main_game_view import GameView

with open("config", mode="r", encoding='utf-8') as file:
    config_data = json.load(file)

SCREEN_WIDTH = config_data.get("SCREEN_WIDTH")
SCREEN_HEIGHT = config_data.get("SCREEN_HEIGHT")


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Fall the Empire")
    game_view = GameView()
    game_view.setup()
    window.show_view(game_view)
    arcade.run()


if __name__ == "__main__":
    main()
