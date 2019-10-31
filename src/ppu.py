from dataclasses import dataclass
from ctypes import c_uint16, c_uint8

# PPU Flags

@dataclass
class status:
    sprite_overflow: c_uint8 = 0
    sprite_zero_hit: c_uint8 = 0
    vertical_blank: c_uint8 = 0

@dataclass
class mask:
    grayscale: c_uint8 = 0
    render_background_left: c_uint8 = 0
    render_sprites_left: c_uint8 = 0
    render_background: c_uint8 = 0
    render_sprites: c_uint8 = 0
    enhance_red: c_uint8 = 0
    enhance_green: c_uint8 = 0
    enhance_blue: c_uint8 = 0

@dataclass
class control:
    nametable_x: c_uint8 = 0
    nametable_y: c_uint8 = 0
    increment_mode: c_uint8 = 0
    pattern_sprite: c_uint8 = 0
    pattern_background: c_uint8 = 0
    sprite_size: c_uint8 = 0
    slave_mode : c_uint8 = 0
    enable_nmi: c_uint8 = 0

class PPU:

    def __init__(self, window):
        self.tableName = [c_uint8(0)]*1024*2
        self.tablePalette = [c_uint8(0)]*32
        self.scanline = 0           # row
        self.cycle = 0              # column
        self.frameComplete = False
        self.window = window
        # PPU flags
        self.status = status()
        self.mask = mask()
        self.control = status()

        self.address_latch = 0x00
        self.ppu_data_buffer = 0x00
        self.vram_addr = 0x0000
        # Color mapping
        self.color = {
            0x00: (84, 84, 84),
            0x01: (0, 30, 116),
            0x02: (8, 16, 144),
            0x03: (48, 0, 136),
            0x04: (68, 0, 100),
            0x05: (92, 0, 48),
            0x06: (84, 4, 0),
            0x07: (60, 24, 0),
            0x08: (32, 42, 0),
            0x09: (8, 58, 0),
            0x0A: (0, 64, 0),
            0x0B: (0, 60, 0),
            0x0C: (0, 50, 60),
            0x0D: (0, 0, 0),
            0x0E: (0, 0, 0),
            0x0F: (0, 0, 0),

            0x10: (152, 150, 152),
            0x11: (8, 76, 196),
            0x12: (48, 50, 236),
            0x13: (92, 30, 228),
            0x14: (136, 20, 176),
            0x15: (160, 20, 100),
            0x16: (152, 34, 32),
            0x17: (120, 60, 0),
            0x18: (84, 90, 0),
            0x19: (40, 114, 0),
            0x1A: (8, 124, 0),
            0x1B: (0, 118, 40),
            0x1C: (0, 102, 120),
            0x1D: (0, 0, 0),
            0x1E: (0, 0, 0),
            0x1F: (0, 0, 0),

            0x20: (236, 238, 236),
            0x21: (76, 154, 236),
            0x22: (120, 124, 236),
            0x23: (176, 98, 236),
            0x24: (228, 84, 236),
            0x25: (236, 88, 180),
            0x26: (236, 106, 100),
            0x27: (212, 136, 32),
            0x28: (160, 170, 0),
            0x29: (116, 196, 0),
            0x2A: (76, 208, 32),
            0x2B: (56, 204, 108),
            0x2C: (56, 180, 204),
            0x2D: (60, 60, 60),
            0x2E: (0, 0, 0),
            0x2F: (0, 0, 0),

            0x30: (236, 238, 236),
            0x31: (168, 204, 236),
            0x32: (188, 188, 236),
            0x33: (212, 178, 236),
            0x34: (236, 174, 236),
            0x35: (236, 174, 212),
            0x36: (236, 180, 176),
            0x37: (228, 196, 144),
            0x38: (204, 210, 120),
            0x39: (180, 222, 120),
            0x3A: (168, 226, 144),
            0x3B: (152, 226, 180),
            0x3C: (160, 214, 228),
            0x3D: (160, 162, 160),
            0x3E: (0, 0, 0),
            0x3F: (0, 0, 0)
        }

    def cpuWrite(self, address, data):
        if address == 0x0000:       # Control
            if data & 0b00000001:
                self.control.vertical_blank = 1
            else:
                self.control.vertical_blank = 0
            if data & 0b00000010:
                self.control.sprite_zero_hit = 1
            else:
                self.control.sprite_zero_hit = 0
            if data & 0b00000100:
                self.control.sprite_overflow = 1
            else:
                self.control.sprite_overflow = 0
            print("0")
        elif address == 0x0001:     # Mask
            if data & 0b00000001:
                self.mask.enhance_blue = 1
            else:
                self.mask.enhance_blue = 0
            if data & 0b00000010:
                self.mask.enhance_green = 1
            else:
                self.mask.enhance_green = 0
            if data & 0b00000100:
                self.mask.enhance_red = 1
            else:
                self.mask.enhance_red = 0
            if data & 0b00001000:
                self.mask.render_sprites = 1
            else:
                self.mask.render_sprites = 0
            if data & 0b00010000:
                self.mask.render_background = 1
            else:
                self.mask.render_background = 0
            if data & 0b00100000:
                self.mask.render_sprites_left = 1
            else:
                self.mask.render_sprites_left = 0
            if data & 0b01000000:
                self.mask.render_background_left = 1
            else:
                self.mask.render_background_left = 0
            if data & 0b10000000:
                self.mask.grayscale = 1
            else:
                self.mask.grayscale = 0
            print("1")
        elif address == 0x0002:     # Status
            print("2")
        elif address == 0x0003:     # OAM Address
            print("3")
        elif address == 0x0004:     # OAM Data
            print("4")
        elif address == 0x0005:     # Scroll
            if self.address_latch == 0:
                self.address_latch = 1
            else:
                self.address_latch = 0
            print("5")
        elif address == 0x0006:     # PPU Address
            if self.address_latch == 0:
                self.address_latch = 1
            else:
                self.address_latch = 0
            print("6")
        elif address == 0x0007:     # PPU Data
            print("7")

    def cpuRead(self, address, readOnly):
        data = c_uint8(0)

        if address == 0x0000:       # Control
            if data & 0b00000001:
                self.control.vertical_blank = 1
            else:
                self.control.vertical_blank = 0
            if data & 0b00000010:
                self.control.sprite_zero_hit = 1
            else:
                self.control.sprite_zero_hit = 0
            if data & 0b00000100:
                self.control.sprite_overflow = 1
            else:
                self.control.sprite_overflow = 0
            print("0")
        elif address == 0x0001:     # Mask
            if data & 0b00000001:
                self.mask.enhance_blue = 1
            else:
                self.mask.enhance_blue = 0
            if data & 0b00000010:
                self.mask.enhance_green = 1
            else:
                self.mask.enhance_green = 0
            if data & 0b00000100:
                self.mask.enhance_red = 1
            else:
                self.mask.enhance_red = 0
            if data & 0b00001000:
                self.mask.render_sprites = 1
            else:
                self.mask.render_sprites = 0
            if data & 0b00010000:
                self.mask.render_background = 1
            else:
                self.mask.render_background = 0
            if data & 0b00100000:
                self.mask.render_sprites_left = 1
            else:
                self.mask.render_sprites_left = 0
            if data & 0b01000000:
                self.mask.render_background_left = 1
            else:
                self.mask.render_background_left = 0
            if data & 0b10000000:
                self.mask.grayscale = 1
            else:
                self.mask.grayscale = 0
            print("1")
        elif address == 0x0002:     # Status
            if data & 0b00000001:
                self.status.enable_nmi = 1
            else:
                self.status.enable_nmi = 0
            if data & 0b00000010:
                self.status.slave_mode = 1
            else:
                self.status.slave_mode = 0
            if data & 0b00000100:
                self.status.sprite_size = 1
            else:
                self.status.sprite_size = 0
            if data & 0b00001000:
                self.status.pattern_background = 1
            else:
                self.status.pattern_background = 0
            if data & 0b00010000:
                self.status.pattern_sprite = 1
            else:
                self.status.pattern_sprite = 0
            if data & 0b00100000:
                self.status.increment_mode = 1
            else:
                self.status.increment_mode = 0
            if data & 0b01000000:
                self.status.nametable_y = 1
            else:
                self.status.nametable_y = 0
            if data & 0b10000000:
                self.status.nametable_x = 1
            else:
                self.status.nametable_x = 0
            self.status.vertical_blank = 0
            self.address_latch = 0
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
            data = self.ppu_data_buffer
            ppu_data_buffer = ppuRead(self.vram_addr)
            if (vram_addr >= 0x3F00):
                data = ppu_data_buffer
            vram_addr += 32 if self.control.increment_mode else 1
            print("7")

        return data

    def ppuWrite(self, address, data):
        address = address & 0x3FFF

    def ppuRead(self, address, readOnly=False):
        data = c_uint8(0)
        address = address & 0x3FFF

        return data

    def insertCartridge(self, cartridge):
        self.cartridge = cartridge

    def getColourFromPaletteRam(self, palette, pixel):
        return self.color[ppuRead(0x3F00 + (palette << 2) + pixel) & 0x3F]

    def getPatternTable(self, i, palette): # i and palette are c_uint8
        for nTileY in range(16):
            for nTileX in range(16):
                nOffset = nTileY * 256 + nTileX * 16
                for row in range(8):
                    tile_lsb = ppuRead(i * 0x1000 + nOffset + row + 0x0000)
                    tile_msb = ppuRead(i * 0x1000 + nOffset + row + 0x0008)
                    for col in range(8):
                        pixel = (tile_lsb & 0x01) + (tile_msb & 0x01)
                        tile_lsb >>= 1
                        tile_msb >>= 1
                        # TODO: set pixel
                        # sprPatternTable[i].setPixel(
                        #     nTileX * 8 + (7 - col),
                        #     nTileY * 8 + row, 
                        #     getColourFromPaletteRam(palette, pixel)
                        # )


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
            