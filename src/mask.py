class Mask:

    def __init__(self):
        self.grayscale = 0
        self.render_background_left = 0
        self.render_sprites_left = 0
        self.render_background = 0
        self.render_sprites = 0
        self.enhance_red = 0
        self.enhance_green = 0
        self.enhance_blue = 0
        
    def writeMask(self, data):
        if data & 0b10000000:
            self.enhance_blue = 1
        else:
            self.enhance_blue = 0
        if data & 0b01000000:
            self.enhance_green = 1
        else:
            self.enhance_green = 0
        if data & 0b00100000:
            self.enhance_red = 1
        else:
            self.enhance_red = 0
        if data & 0b00010000:
            self.render_sprites = 1
        else:
            self.render_sprites = 0
        if data & 0b00001000:
            self.render_background = 1
        else:
            self.render_background = 0
        if data & 0b00000100:
            self.render_sprites_left = 1
        else:
            self.render_sprites_left = 0
        if data & 0b00000010:
            self.render_background_left = 1
        else:
            self.render_background_left = 0
        if data & 0b000000001:
            self.grayscale = 1
        else:
            self.grayscale = 0