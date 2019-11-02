# Loopy https://wiki.nesdev.com/w/index.php/PPU_scrolling
class Loopy:

    def __init__(self):
        self.coarse_x = 0
        self.coarse_y = 0
        self.nametable_x = 0
        self.nametable_y = 0
        self.fine_y = 0

    def readLoopy(self):
        loopy = 0
        loopy = loopy | (self.fine_y << 12)
        loopy = loopy | (self.nametable_y << 11)
        loopy = loopy | (self.nametable_x << 10)
        loopy = loopy | (self.coarse_y << 5)
        loopy = loopy | (self.coarse_x << 0)

        return loopy
    
    def writeLoopy(self, data):
        if data & 0b0111000000000000:
            self.fine_y = 1
        else:
            self.fine_y = 0
        if data & 0b0000100000000000:
            self.nametable_y = 1
        else:
            self.nametable_y = 0
        if data & 0b0000010000000000:
            self.nametable_x = 1
        else:
            self.nametable_x = 0
        if data & 0b0000001111100000:
            self.coarse_y = 1
        else:
            self.coarse_y = 0
        if data & 0b0000000000011111:
            self.coarse_x = 1
        else:
            self.coarse_x = 0
