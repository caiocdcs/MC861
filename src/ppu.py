from ctypes import c_uint16, c_uint8

class PPU:

    def __init__(self, window):
        self.tableName = [c_uint8(0)]*1024*2
        self.tablePalette = [c_uint8(0)]*32
        self.scanline = 0           # row
        self.cycle = 0              # column
        self.frameComplete = False
        self.window = window


    def cpuWrite(self, address, data):
        if address == 0x0000:       # Control
            print("0")
        elif address == 0x0001:     # Mask
            print("1")
        elif address == 0x0002:     # Status
            print("2")
        elif address == 0x0003:     # OAM Address
            print("3")
        elif address == 0x0004:     # OAM Data
            print("4")
        elif address == 0x0005:     # Scroll
            print("5")
        elif address == 0x0006:     # PPU Address
            print("6")
        elif address == 0x0007:     # PPU Data
            print("7")

    def cpuRead(self, address, readOnly):
        data = c_uint8(0)

        if address == 0x0000:       # Control
            print("0")
        elif address == 0x0001:     # Mask
            print("1")
        elif address == 0x0002:     # Status
            print("2")
        elif address == 0x0003:     # OAM Address
            print("3")
        elif address == 0x0004:     # OAM Data
            print("4")
        elif address == 0x0005:     # Scroll
            print("5")
        elif address == 0x0006:     # PPU Address
            print("6")
        elif address == 0x0007:     # PPU Data
            print("7")

        return data

    def ppuWrite(self, address, data):
        address = address & 0x3FFF

    def ppuRead(self, address, readOnly):
        data = c_uint8(0)
        address = address & 0x3FFF

        return data

    def insertCartridge(self, cartridge):
        self.cartridge = cartridge

    def clock(self):

        self.cycle += 1
        
        if self.cycle >= 341:
            self.cycle = 0
            self.scanline += 1

            if self.scanline >= 261:
                self.scanline = -1
                self.frameComplete = True
                self.window.movePixelDown()
                # print("Frame Complete")
            