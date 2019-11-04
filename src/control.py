class Control:

    def __init__(self):
        self.enable_nmi = 0
        self.slave_mode = 0
        self.sprite_overflow = 0
        self.pattern_background = 0
        self.pattern_sprite = 0
        self.increment_mode = 0
        self.nametable_y = 0
        self.nametable_x = 0

    def writeControl(self, data):
        if data & 0b10000000:
            self.enable_nmi = 1
        else:
            self.enable_nmi = 0
        if data & 0b01000000:
            self.slave_mode = 1
        else:
            self.slave_mode = 0
        if data & 0b00100000:
            self.sprite_overflow = 1
        else:
            self.sprite_overflow = 0
        if data & 0b00010000:
            self.pattern_background = 1
        else:
            self.pattern_background = 0
        if data & 0b00001000:
            self.pattern_sprite = 1
        else:
            self.pattern_sprite = 0
        if data & 0b00000100:
            self.increment_mode = 1
        else:
            self.increment_mode = 0
        if data & 0b00000010:
            self.nametable_y = 1
        else:
            self.nametable_y = 0
        if data & 0b000000001:
            self.nametable_x = 1
        else:
            self.nametable_x = 0

    def readControl(self):
        control = 0
        control = control | (self.nametable_x << 0)
        control = control | (self.nametable_y << 1)
        control = control | (self.increment_mode << 2)
        control = control | (self.pattern_sprite << 3)
        control = control | (self.pattern_background << 4)
        control = control | (self.sprite_overflow << 5)
        control = control | (self.slave_mode << 6)
        control = control | (self.enable_nmi << 7)

        return control
