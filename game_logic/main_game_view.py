import json
import arcade
from entity_logic.unit import Unit

class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        with open("config", mode="r", encoding='utf-8') as file:
            self.config_data = json.load(file)


    def setup(self):
        map_name = "data/level1.tmx"
        arcade.set_background_color(arcade.color.WHITE)
        try:
            self.tile_map = arcade.load_tilemap(map_name, self.config_data.get("TILE_SCALING"))
            self.scene = arcade.Scene.from_tilemap(self.tile_map)
        except Exception as e:
            print(e)
            self.scene = None
        self.unit = Unit("data/sprite/solder", self.config_data.get("UNIT_SCALING"), "solder", "Советский солдат", {"hp": 70, "dmg": 10, "speed": 5})


    def on_draw(self):
        # game render
        self.clear()



    def on_update(self, delta_time):
        # game update
        pass