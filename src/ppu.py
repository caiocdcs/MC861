from utils import log_ppu
from window import Window
from pygame import Color

from status import Status
from mask import Mask
from control import Control
from loopy import Loopy

from numpy import uint16

int8 = int

class PPU:

    def __init__(self):
        # Tables
        self.tableName = [[int8(0) for _ in range(1024)]] * 2
        self.tablePalette = [int8(0)]*32
        self.tablePattern = [[int8(0) for _ in range(4096)]] * 2

        self.frameComplete = False
        self.window = Window()

        self.nmi = False
        self.ppu_address = 0x0000

        self.oam = [0]*256
        self.oam_address = 0x00

        self.spriteScanline = [int8(0)]*32
        self.spriteCount = 0
        self.sprite_shifter_pattern_hi = [int8(0)]*8
        self.sprite_shifter_pattern_lo = [int8(0)]*8

        self.fine_x = 0x00
        self.address_latch = 0x00
        self.ppu_data_buffer = 0x00
        self.scanline = 0           # row
        self.cycle = 0              # column

        self.vram_addr = Loopy()
        self.tram_addr = Loopy()

        # PPU flags
        self.status = Status()
        self.mask = Mask()
        self.control = Control()

        # Background
        self.bg_next_tile_id = 0x00
        self.bg_next_tile_attrib = 0x00
        self.bg_next_tile_lsb = 0x00
        self.bg_next_tile_msb = 0x00
        self.bg_shifter_pattern_lo = uint16(0x0000)
        self.bg_shifter_pattern_hi = uint16(0x0000)
        self.bg_shifter_attrib_lo = uint16(0x0000)
        self.bg_shifter_attrib_hi = uint16(0x0000)
        
        # Color mapping
        self.color = {
            0x00: Color(84, 84, 84),
            0x01: Color(0, 30, 116),
            0x02: Color(8, 16, 144),
            0x03: Color(48, 0, 136),
            0x04: Color(68, 0, 100),
            0x05: Color(92, 0, 48),
            0x06: Color(84, 4, 0),
            0x07: Color(60, 24, 0),
            0x08: Color(32, 42, 0),
            0x09: Color(8, 58, 0),
            0x0A: Color(0, 64, 0),
            0x0B: Color(0, 60, 0),
            0x0C: Color(0, 50, 60),
            0x0D: Color(0, 0, 0),
            0x0E: Color(0, 0, 0),
            0x0F: Color(0, 0, 0),

            0x10: Color(152, 150, 152),
            0x11: Color(8, 76, 196),
            0x12: Color(48, 50, 236),
            0x13: Color(92, 30, 228),
            0x14: Color(136, 20, 176),
            0x15: Color(160, 20, 100),
            0x16: Color(152, 34, 32),
            0x17: Color(120, 60, 0),
            0x18: Color(84, 90, 0),
            0x19: Color(40, 114, 0),
            0x1A: Color(8, 124, 0),
            0x1B: Color(0, 118, 40),
            0x1C: Color(0, 102, 120),
            0x1D: Color(0, 0, 0),
            0x1E: Color(0, 0, 0),
            0x1F: Color(0, 0, 0),

            0x20: Color(236, 238, 236),
            0x21: Color(76, 154, 236),
            0x22: Color(120, 124, 236),
            0x23: Color(176, 98, 236),
            0x24: Color(228, 84, 236),
            0x25: Color(236, 88, 180),
            0x26: Color(236, 106, 100),
            0x27: Color(212, 136, 32),
            0x28: Color(160, 170, 0),
            0x29: Color(116, 196, 0),
            0x2A: Color(76, 208, 32),
            0x2B: Color(56, 204, 108),
            0x2C: Color(56, 180, 204),
            0x2D: Color(60, 60, 60),
            0x2E: Color(0, 0, 0),
            0x2F: Color(0, 0, 0),

            0x30: Color(236, 238, 236),
            0x31: Color(168, 204, 236),
            0x32: Color(188, 188, 236),
            0x33: Color(212, 178, 236),
            0x34: Color(236, 174, 236),
            0x35: Color(236, 174, 212),
            0x36: Color(236, 180, 176),
            0x37: Color(228, 196, 144),
            0x38: Color(204, 210, 120),
            0x39: Color(180, 222, 120),
            0x3A: Color(168, 226, 144),
            0x3B: Color(152, 226, 180),
            0x3C: Color(160, 214, 228),
            0x3D: Color(160, 162, 160),
            0x3E: Color(0, 0, 0),
            0x3F: Color(0, 0, 0)
        }

    def cpuWrite(self, address, data):
        data = uint16(data)
        if address == 0x0000:       # Control
            self.control.writeControl(data)
            self.tram_addr.nametable_x = self.control.nametable_x
            self.tram_addr.nametable_y = self.control.nametable_y
        elif address == 0x0001:     # Mask
            self.mask.writeMask(data)
        elif address == 0x0002:     # Status
            pass
        elif address == 0x0003:     # OAM Address
            self.oam_address = data
        elif address == 0x0004:     # OAM Data
            self.oam[self.oam_address] = data
        elif address == 0x0005:     # Scroll
            if self.address_latch == 0:
                self.fine_x = data & 0x07
                self.tram_addr.coarse_x = data >> 3
                self.address_latch = 1
            else:
                self.address_latch = 0
                self.tram_addr.fine_y = data & 0x07
                self.tram_addr.coarse_y = data >> 3
        elif address == 0x0006:     # PPU Address
            if self.address_latch == 0:
                self.tram_addr.writeLoopy(((data & 0x3F) << 8) | (self.tram_addr.readLoopy() & 0x00FF))
                self.address_latch = 1
            else:
                self.tram_addr.writeLoopy((self.tram_addr.readLoopy() & 0xFF00) | data)
                self.vram_addr = self.tram_addr
                self.address_latch = 0
        elif address == 0x0007:     # PPU Data
            self.ppuWrite(self.vram_addr.readLoopy(), data)
            self.vram_addr.writeLoopy(self.vram_addr.readLoopy() + (32 if self.control.increment_mode else 1))

    def cpuRead(self, address):
        data = uint16(0x0000)
        if address == 0x0000:       # Control
            pass
        elif address == 0x0001:     # Mask
            pass
        elif address == 0x0002:     # Status
            data = (self.status.readStatus() | (self.ppu_data_buffer & 0x1F))
            self.status.vertical_blank = 0
            self.address_latch = 0
        elif address == 0x0003:     # OAM Address
            data = self.oam_address
        elif address == 0x0004:     # OAM Data
            data = self.oam[self.oam_address]
        elif address == 0x0005:     # Scroll
            pass
        elif address == 0x0006:     # PPU Address
            pass
        elif address == 0x0007:     # PPU Data
            pass
            data = self.ppu_data_buffer
            self.ppu_data_buffer = self.ppuRead(self.vram_addr.readLoopy())
            if self.vram_addr.readLoopy() >= 0x3F00:
                data = self.ppu_data_buffer
            self.vram_addr.writeLoopy(self.vram_addr.readLoopy() + (32 if self.control.increment_mode else 1))

        return data

    def ppuWrite(self, address, data):
        data = uint16(data)
        address = address & 0x3FFF

        if self.cartridge.ppuWrite(address, data):
            pass

        elif address >= 0x0000 and address <= 0x1FFF:
            self.tablePattern[(address & 0x1000) >> 12][address & 0x0FFF] = data

        elif address >= 0x2000 and address <= 0x3EFF:
            address = address & 0x0FFF
            if self.cartridge.getMirror() == 0:
                if 0x0000 <= address <= 0x03FF:
                    self.tableName[0][address & 0x03FF] = data
                elif 0x0400 <= address <= 0x07FF:
                    self.tableName[1][address & 0x03FF] = data
                elif 0x0800 <= address <= 0x0BFF:
                    self.tableName[0][address & 0x03FF] = data
                elif 0x0C00 <= address <= 0x0FFF:
                    self.tableName[1][address & 0x03FF] = data
            elif self.cartridge.getMirror() == 1:
                if 0x0000 <= address <= 0x03FF:
                    self.tableName[0][address & 0x03FF] = data
                elif 0x0400 <= address <= 0x07FF:
                    self.tableName[0][address & 0x03FF] = data
                elif 0x0800 <= address <= 0x0BFF:
                    self.tableName[1][address & 0x03FF] = data
                elif 0x0C00 <= address <= 0x0FFF:
                    self.tableName[1][address & 0x03FF] = data

        elif 0x3F00 <= address <= 0x3FFF:
            address &= 0x001F
            if address == 0x0010:
                address = 0x0000
            elif address == 0x0014:
                address = 0x0004
            elif address == 0x0018:
                address = 0x0008
            elif address == 0x001C:
                address = 0x000C
            self.tablePalette[address] = data

    def ppuRead(self, address):
        data = uint16(0x0000)
        addr = address & 0x3FFF

        cartridgeData = self.cartridge.ppuRead(address)
        if cartridgeData is not None:
            data = cartridgeData
        elif 0x0000 <= addr <= 0x1FFF:
            data = self.tablePattern[(addr & 0x1000) >> 12][addr & 0x0FFF]
        elif 0x2000 <= addr <= 0x3EFF:
            addr &= 0x0FFF
            if self.cartridge.mirror == 0:  # Vertical
                if 0x0000 <= addr <= 0x03FF:
                    data = self.tableName[0][addr & 0x03FF]
                if 0x0400 <= addr <= 0x07FF:
                    data = self.tableName[1][addr & 0x03FF]
                if 0x0800 <= addr <= 0x0BFF:
                    data = self.tableName[0][addr & 0x03FF]
                if 0x0C00 <= addr <= 0x0FFF:
                    data = self.tableName[1][addr & 0x03FF]
            elif self.cartridge.mirror == 1:
                if 0x0000 <= addr <= 0x03FF:
                    data = self.tableName[0][addr & 0x03FF]
                if 0x0400 <= addr <= 0x07FF:
                    data = self.tableName[0][addr & 0x03FF]
                if 0x0800 <= addr <= 0x0BFF:
                    data = self.tableName[1][addr & 0x03FF]
                if 0x0C00 <= addr <= 0x0FFF:
                    data = self.tableName[1][addr & 0x03FF]
        elif 0x3F00 <= addr <= 0x3FFF:
            addr &= 0x001F
            if addr == 0x0010:
                addr = 0x0000
            if addr == 0x0014:
                addr = 0x0004
            if addr == 0x0018:
                addr = 0x0008
            if addr == 0x001C:
                addr = 0x000C
            data = self.tablePalette[addr] & (0x30 if self.mask.grayscale else 0x3F)

        return data

    def insertCartridge(self, cartridge):
        self.cartridge = cartridge

    def getColor(self, palette, pixel):
        return self.color[self.ppuRead(0x3F00 + (palette << 2) + pixel) & 0x3F]

    def reset(self):
        self.fine_x = 0x00
        self.address_latch = 0x00
        self.ppu_data_buffer = 0x00
        self.scanline = 0           # row
        self.cycle = 0              # column

        self.vram_addr = Loopy()
        self.tram_addr = Loopy()
        # Background
        self.bg_next_tile_id = 0x00
        self.bg_next_tile_attrib = 0x00
        self.bg_next_tile_lsb = 0x00
        self.bg_next_tile_msb = 0x00
        self.bg_shifter_pattern_lo = uint16(0x000)
        self.bg_shifter_pattern_hi = uint16(0x000)
        self.bg_shifter_attrib_lo = uint16(0x000)
        self.bg_shifter_attrib_hi = uint16(0x000)

    def clock(self):

        # if scanline is visible to the user...
        if -1 <= self.scanline < 240:
            if self.scanline == 0 and self.cycle == 0:
                self.cycle = 1 # skip cycle

            if self.scanline == -1 and self.cycle == 1:
                # starting new frame, clear flags and shifters
                self.status.vertical_blank = 0
                self.status.sprite_overflow = 0
                self.status.sprite_zero_hit = 0
                for i in range(8):
                    self.sprite_shifter_pattern_lo[i] = 0
                    self.sprite_shifter_pattern_hi[i] = 0

        # end of frame
        if 241 <= self.scanline < 261:
            if self.scanline == 241 and self.cycle == 1:
                self.status.vertical_blank = 1
                if self.control.enable_nmi:
                    self.nmi = True
                    # TODO: update frame

                    # # print palette
                    # for i in range(32):
                    #     print(self.tablePalette[i])

                    # # print nameTable 1
                    # for i in range(1024):
                    #     print(self.tableName[0][i])

                    # # print nameTable 2
                    # for i in range(1024):
                    #     print(self.tableName[1][i])

                    # # print patternTable 1
                    # for i in range(4096):
                    #     print(self.tablePattern[0][i])

                    # # print patternTable 2
                    # for i in range(4096):
                    #     print(self.tablePattern[1][i])


        # and finally draws the pixel
        # self.window.setPixel(self.cycle - 1, self.scanline,  self.getColor(0x00, 0x00))

        # DEBUG
        # log_ppu(self.cycle, self.scanline, self.status, self.mask, self.control, self.vram_addr, pixel, palette)

        self.cycle += 1
        if self.cycle >= 341:
            self.cycle = 0
            self.scanline += 1

            if self.scanline >= 261:
                self.scanline = -1
                self.frameComplete = True

    def getNmi(self):
        return self.nmi

    def setNmi(self, nmi):
        self.nmi = nmi
