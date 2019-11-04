class Status:

    def __init__(self):
        self.sprite_overflow = 0    #5
        self.sprite_zero_hit = 0    #6
        self.vertical_blank = 0     #7

    def readStatus(self):
        status = 0
        status = status | (self.sprite_overflow << 5)
        status = status | (self.sprite_zero_hit << 6)
        status = status | (self.vertical_blank << 7)

        return status