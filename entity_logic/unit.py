import arcade


class Unit(arcade.Sprite):
    def __init__(self, filename, scale, type, name, chars):
        super().__init__(filename, scale, type, name, chars)
        self.texture = arcade.load_texture(filename)
        self.scale = scale
        self.type = type
        self.name = name
        self.chars = chars


    def update(self, delta_time):
        # unit logic update
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time
