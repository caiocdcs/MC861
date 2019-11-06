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
        loopy = loopy | (self.coarse_x << 0)
        loopy = loopy | (self.coarse_y << 5)
        loopy = loopy | (self.nametable_x << 10)
        loopy = loopy | (self.nametable_y << 11)
        loopy = loopy | (self.fine_y << 12)

        return loopy
    
    def writeLoopy(self, data):
        self.fine_y = (data >> 12 | 0)
        self.nametable_y = (data >> 11 | 0)
        self.nametable_x = (data >> 10 | 0)
        self.coarse_y = (data >> 5 | 0)
        self.coarse_x = (data >> 0 | 0)
