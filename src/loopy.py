from numpy import uint16

# Loopy https://wiki.nesdev.com/w/index.php/PPU_scrolling
class Loopy:

    def __init__(self):
        self.coarse_x = uint16(0)
        self.coarse_y = uint16(0)
        self.nametable_x = uint16(0)
        self.nametable_y = uint16(0)
        self.fine_y = uint16(0)

    def readLoopy(self):
        loopy = uint16(0)
        loopy = loopy | (self.coarse_x << 0)
        loopy = loopy | (self.coarse_y << 5)
        loopy = loopy | (self.nametable_x << 10)
        loopy = loopy | (self.nametable_y << 11)
        loopy = loopy | (self.fine_y << 12)

        return loopy
    
    def writeLoopy(self, data):
        data = uint16(data)
        self.fine_y = (data & 0b0111000000000000) >> 12
        self.nametable_y = (data & 0b0000100000000000) >> 11
        self.nametable_x = (data & 0b0000010000000000) >> 10
        self.coarse_y = (data & 0b0000001111100000) >> 5
        self.coarse_x = (data & 0b0000000000011111)
