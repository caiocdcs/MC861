from dataclasses import dataclass
from ctypes import c_uint16, c_uint8

# PPU Flags

@dataclass
class status:
    sprite_overflow: c_uint8 = 1
    sprite_zero_hit: c_uint8 = 1
    vertical_blank: c_uint8 = 1

@dataclass
class mask:
    grayscale: c_uint8 = 1
    render_background_left: c_uint8 = 1
    render_sprites_left: c_uint8 = 1
    render_background: c_uint8 = 1
    render_sprites: c_uint8 = 1
    enhance_red: c_uint8 = 1
    enhance_green: c_uint8 = 1
    enhance_blue: c_uint8 = 1

@dataclass
class control:
    nametable_x: c_uint8 = 1
    nametable_y: c_uint8 = 1
    increment_mode: c_uint8 = 1
    pattern_sprite: c_uint8 = 1
    pattern_background: c_uint8 = 1
    sprite_size: c_uint8 = 1
    slave_mode : c_uint8 = 1
    enable_nmi: c_uint8 = 1

@dataclass
class loopy:
    coarse_x: c_uint16 = 5
    coarse_y: c_uint16 = 5
    nametable_x: c_uint16 = 1
    nametable_y: c_uint16 = 1
    fine_y: c_uint16 = 3
    reg: c_uint16 = 0x0000

class PPU:

    def __init__(self, window):
        # Tables
        self.tableName = [c_uint8(0)]*1024*2
        self.tablePalette = [c_uint8(0)]*32
        self.tablePattern = [c_uint8(0)]*4096*2

        self.scanline = 0           # row
        self.cycle = 0              # column
        self.frameComplete = False
        self.window = window

        # PPU flags
        self.status = status()
        self.mask = mask()
        self.control = control()

        # Background
        self.bg_next_tile_id = 0x00
        self.bg_next_tile_attrib = 0x00
        self.bg_next_tile_lsb = 0x00
        self.bg_next_tile_msb = 0x00
        self.bg_shifter_pattern_lo = 0x0000
        self.bg_shifter_pattern_hi = 0x0000
        self.bg_shifter_attrib_lo = 0x0000
        self.bg_shifter_attrib_hi = 0x0000

        self.vram_addr = loopy()
        self.tram_addr = loopy()
        self.fine_x = 0x00
        self.nmi = False

        self.address_latch = 0x00
        self.ppu_data_buffer = 0x00

        self.oam = [0]*256
        self.oam_address = 0x00

        self.spriteScanline = [0]*32
        self.spriteCount = 0
        self.sprite_shifter_pattern_hi = [0]*8
        self.sprite_shifter_pattern_lo = [0]*8
        
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
            print("cpuWrite: 0")
            if data.value & 0b10000000:
                self.control.enable_nmi = 1
            else:
                self.control.enable_nmi = 1
            if data.value & 0b01000000:
                self.control.slave_mode = 1
            else:
                self.control.slave_mode = 0
            if data.value & 0b00100000:
                self.control.sprite_size = 1
            else:
                self.control.sprite_size = 0
            if data.value & 0b00010000:
                self.control.pattern_background = 1
            else:
                self.control.pattern_background = 0
            if data.value & 0b00001000:
                self.control.pattern_sprite = 1
            else:
                self.control.pattern_sprite = 0
            if data.value & 0b00000100:
                self.control.increment_mode = 1
            else:
                self.control.increment_mode = 0
            if data.value & 0b00000010:
                self.control.nametable_y = 1
            else:
                self.control.nametable_y = 0
            if data.value & 0b000000001:
                self.control.nametable_x = 1
            else:
                self.control.nametable_x = 0
        elif address == 0x0001:     # Mask
            if data.value & 0b10000000:
                self.mask.enhance_blue = 1
            else:
                self.mask.enhance_blue = 0
            if data.value & 0b01000000:
                self.mask.enhance_green = 1
            else:
                self.mask.enhance_green = 0
            if data.value & 0b00100000:
                self.mask.enhance_red = 1
            else:
                self.mask.enhance_red = 0
            if data.value & 0b00010000:
                self.mask.render_sprites = 1
            else:
                self.mask.render_sprites = 0
            if data.value & 0b00001000:
                self.mask.render_background = 1
            else:
                self.mask.render_background = 0
            if data.value & 0b00000100:
                self.mask.render_sprites_left = 1
            else:
                self.mask.render_sprites_left = 0
            if data.value & 0b00000010:
                self.mask.render_background_left = 1
            else:
                self.mask.render_background_left = 0
            if data.value & 0b010000001:
                self.mask.grayscale = 1
            else:
                self.mask.grayscale = 0
            print("cpuWrite: 1")
        elif address == 0x0002:     # Status
            print("cpuWrite: 2")
        elif address == 0x0003:     # OAM Address
            print("cpuWrite: 3")
            self.oam_address = data
        elif address == 0x0004:     # OAM Data
            print("cpuWrite: 4")
            self.oam[self.oam_address] = data
        elif address == 0x0005:     # Scroll
            print("cpuWrite: 5")
            if self.address_latch == 0:
                self.fine_x = data.value & 0x07
                self.tram_addr.coarse_x = data.value >> 3
                self.address_latch = 1
            else:
                self.address_latch = 0
                self.tram_addr.fine_y = data.value & 0x07
                self.tram_addr.coarse_y = data.value >> 3
        elif address == 0x0006:     # PPU Address
            if self.address_latch == 0:
                self.tram_addr.reg = ((data.value & 0x3F) << 8) | (self.tram_addr.reg & 0x00FF)
                self.address_latch = 1
            else:
                self.tram_addr.reg = (self.tram_addr.reg & 0xFF00) | data.value
                self.vram_addr = self.tram_addr
                self.address_latch = 0
            print("cpuWrite: 6")
        elif address == 0x0007:     # PPU Data
            print("cpuWrite: 7")
            self.ppuWrite(self.vram_addr.reg, data)
            self.vram_addr.reg += 32 if self.control.increment_mode else 1

    def cpuRead(self, address, readOnly):
        data = c_uint8(0)
        if address == 0x0000:       # Control
            if data.value & 0b10000000:
                self.control.enable_nmi = 1
            else:
                self.control.enable_nmi = 0
            if data.value & 0b01000000:
                self.control.slave_mode = 1
            else:
                self.control.slave_mode = 0
            if data.value & 0b00100000:
                self.control.sprite_size = 1
            else:
                self.control.sprite_size = 0
            if data.value & 0b00010000:
                self.control.pattern_background = 1
            else:
                self.control.pattern_background = 0
            if data.value & 0b00001000:
                self.control.pattern_sprite = 1
            else:
                self.control.pattern_sprite = 0
            if data.value & 0b00000100:
                self.control.increment_mode = 1
            else:
                self.control.increment_mode = 0
            if data.value & 0b00000010:
                self.control.nametable_y = 1
            else:
                self.control.nametable_y = 0
            if data.value & 0b000000001:
                self.control.nametable_x = 1
            else:
                self.control.nametable_x = 0
            print("cpuRead: 0")
        elif address == 0x0001:     # Mask
            if data.value & 0b10000000:
                self.mask.enhance_blue = 1
            else:
                self.mask.enhance_blue = 0
            if data.value & 0b01000000:
                self.mask.enhance_green = 1
            else:
                self.mask.enhance_green = 0
            if data.value & 0b00100000:
                self.mask.enhance_red = 1
            else:
                self.mask.enhance_red = 0
            if data.value & 0b00010000:
                self.mask.render_sprites = 1
            else:
                self.mask.render_sprites = 0
            if data.value & 0b00001000:
                self.mask.render_background = 1
            else:
                self.mask.render_background = 0
            if data.value & 0b00000100:
                self.mask.render_sprites_left = 1
            else:
                self.mask.render_sprites_left = 0
            if data.value & 0b00000010:
                self.mask.render_background_left = 1
            else:
                self.mask.render_background_left = 0
            if data.value & 0b010000001:
                self.mask.grayscale = 1
            else:
                self.mask.grayscale = 0
            print("cpuRead: 1")
        elif address == 0x0002:     # Status
            if data.value & 0b10000000:
                self.status.vertical_blank = 1
            else:
                self.status.vertical_blank = 0
            if data.value & 0b10000000:
                self.status.sprite_zero_hit = 1
            else:
                self.status.sprite_zero_hit = 0
            if data.value & 0b10000000:
                self.status.sprite_overflow = 1
            else:
                self.status.sprite_overflow = 0
            # self.status.vertical_blank = 0 TODO: undestand better hoe vertical blank is set
            self.address_latch = 0
            print("cpuRead: 2")
        elif address == 0x0003:     # OAM Address
            print("cpuRead: 3")
            data = self.oam_address
        elif address == 0x0004:     # OAM Data
            data = self.oam[self.oam_address]
            print("cpuRead: 4")
        elif address == 0x0005:     # Scroll
            print("cpuRead: 5")
        elif address == 0x0006:     # PPU Address
            print("cpuRead: 6")
        elif address == 0x0007:     # PPU Data
            print("cpuRead: 7")
            data = self.ppu_data_buffer
            ppu_data_buffer = self.ppuRead(self.vram_addr.reg)
            if (self.vram_addr.reg >= 0x3F00):
                data = ppu_data_buffer
            self.vram_addr.reg += 32 if self.control.increment_mode else 1
            print(self.vram_addr.reg)

        return data

    def ppuWrite(self, address, data):
        print("ppuWrite")
        address = address & 0x3FFF
        if (address >= 0x0000 & address <= 0x1FFF):
            offset = 4096 if (address & 0x1000) >> 12 else 0
            self.tablePattern[offset + address & 0x0FFF] = data
        if (address >= 0x3F00 & address <= 0x3FFF):
            address &= 0x001F
            if (address == 0x0010):
                address = 0x0000
            if (address == 0x0014):
                address = 0x0004
            if (address == 0x0018):
                address = 0x0008
            if (address == 0x001C):
                address = 0x000C
            self.tablePalette[address] = data

    def ppuRead(self, address, readOnly=False):
        data = c_uint8(0)
        addr = address & 0x3FFF

        if (addr >= 0x0000 & addr <= 0x1FFF):
            offset = 4096 if (addr & 0x1000) >> 12 else 0
            data = self.tablePattern[addr + offset & 0x0FFF]
        elif (addr >= 0x2000 & addr <= 0x3EFF):
            addr &= 0x0FFF
            if (self.cartridge.mirror == 0):
                if (addr >= 0x0000 & addr <= 0x03FF):
                    data = self.tableName[addr & 0x03FF]
                if (addr >= 0x0400 & addr <= 0x07FF):
                    data = self.tableName[addr + 1024 & 0x03FF]
                if (addr >= 0x0800 & addr <= 0x0BFF):
                    data = self.tableName[addr & 0x03FF]
                if (addr >= 0x0C00 & addr <= 0x0FFF):
                    data = self.tableName[addr + 1024 & 0x03FF]
            elif (self.cartridge.mirror == 1):
                if (addr >= 0x0000 & addr <= 0x03FF):
                    data = self.tableName[addr & 0x03FF]
                if (addr >= 0x0400 & addr <= 0x07FF):
                    data = self.tableName[addr & 0x03FF]
                if (addr >= 0x0800 & addr <= 0x0BFF):
                    data = self.tableName[addr + 1024 & 0x03FF]
                if (addr >= 0x0C00 & addr <= 0x0FFF):
                    data = self.tableName[addr + 1024 & 0x03FF]
        elif (addr >= 0x3F00 & addr <= 0x3FFF):
            addr &= 0x001F
            if (addr == 0x0010):
                addr = 0x0000
            if (addr == 0x0014):
                addr = 0x0004
            if (addr == 0x0018):
                addr = 0x0008
            if (addr == 0x001C):
                addr = 0x000C
            data = self.tablePallete[addr] & (0x30 if self.mask.grayscale else 0x3F)

        return data

    def insertCartridge(self, cartridge):
        self.cartridge = cartridge

    def getColor(self, palette, pixel):
        return self.color[self.ppuRead(0x3F00 + (palette << 2) + pixel).value & 0x3F]

    # def getPatternTable(self, i, palette): # i and palette are c_uint8
    #     for nTileY in range(16):
    #         for nTileX in range(16):
    #             nOffset = nTileY * 256 + nTileX * 16
    #             for row in range(8):
    #                 tile_lsb = self.ppuRead(i * 0x1000 + nOffset + row + 0x0000)
    #                 tile_msb = self.ppuRead(i * 0x1000 + nOffset + row + 0x0008)
    #                 for col in range(8):
    #                     pixel = (tile_lsb & 0x01) + (tile_msb & 0x01)
    #                     tile_lsb >>= 1
    #                     tile_msb >>= 1

    def clock(self):

        self.cycle += 1

        def IncrementScrollX():
            if (self.maskf.render_background | self.mask.render_sprites):
                if (self.vram_addr.coarse_x == 31):
                    self.vram_addr.coarse_x = 0
                    self.vram_addr.nametable_x = ~self.vram_addr.nametable_x
                else:
                    self.vram_addr.coarse_x +- 1

        def IncrementScrollY():
            if (self.mask.render_background | self.mask.render_sprites):
                if (self.vram_addr.fine_y < 7):
                    self.vram_addr.fine_y += 1
                else:
                    self.vram_addr.fine_y = 0
                    if (self.vram_addr.coarse_y == 29):
                        self.vram_addr.coarse_y = 0
                        self.vram_addr.nametable_y = ~self.vram_addr.nametable_y
                    elif (self.vram_addr.coarse_y == 31):
                        self.vram_addr.coarse_y = 0
                    else:
                        self.vram_addr.coarse_y += 1

        def TransferAddressX():
            if (self.mask.render_background | self.mask.render_sprites):
                self.vram_addr.nametable_x = self.tram_addr.nametable_x
                self.vram_addr.coarse_x    = self.tram_addr.coarse_x

        def TransferAddressY():
            if (self.mask.render_background | self.mask.render_sprites):
                self.vram_addr.fine_y      = self.tram_addr.fine_y
                self.vram_addr.nametable_y = self.tram_addr.nametable_y
                self.vram_addr.coarse_y    = self.tram_addr.coarse_y

        def LoadBackgroundShifters():
            self.bg_shifter_pattern_lo = (self.bg_shifter_pattern_lo & 0xFF00) | self.bg_next_tile_lsb.value
            self.bg_shifter_pattern_hi = (self.bg_shifter_pattern_hi & 0xFF00) | self.bg_next_tile_msb.value
            self.bg_shifter_attrib_lo  = 0xFF if (self.bg_shifter_attrib_lo & 0xFF00) | (self.bg_next_tile_attrib & 0b01) else 0x00
            self.bg_shifter_attrib_hi  = 0xFF if (self.bg_shifter_attrib_hi & 0xFF00) | (self.bg_next_tile_attrib & 0b10) else 0x00

        def UpdateShifters():
            if (self.mask.render_background):
                self.bg_shifter_pattern_lo <<= 1
                self.bg_shifter_pattern_hi <<= 1
                self.bg_shifter_attrib_lo <<= 1
                self.bg_shifter_attrib_hi <<= 1
            if (self.mask.render_sprites and self.cycle >= 1 and self.cycle < 258):
                j = 0
                for i in range(self.spriteCount, 4):
                    if (self.spriteScanline[i+3] > 0):
                        self.spriteScanline[i+3] -= 1
                    else:
                        self.sprite_shifter_pattern_lo[j] <<= 1
                        self.sprite_shifter_pattern_hi[j] <<= 1
                    j+=1

        if (self.scanline >= -1 and self.scanline < 240):
            if (self.scanline == 0 and self.cycle == 0):
                self.cycle = 1

            if (self.scanline == -1 and self.cycle == 1):
                self.status.vertical_blank = 0
                self.status.sprite_overflow = 0
                self.status.sprite_zero_hit = 0
                for i in range(8):
                    self.sprite_shifter_pattern_lo[i] = 0
                    self.sprite_shifter_pattern_hi[i] = 0

        if ((self.cycle >= 2 and self.cycle < 258) | (self.cycle >= 321 and self.cycle < 338)):
            UpdateShifters()
            case = (self.cycle - 1) % 8
            if (case == 0):
                self.bg_next_tile_id = self.ppuRead(0x2000 | (self.vram_addr.reg & 0x0FFF)).value
            elif (case == 2):
                self.bg_next_tile_attrib = self.ppuRead(0x23C0 | (self.vram_addr.nametable_y << 11) 
                                                    | (self.vram_addr.nametable_x << 10) 
                                                    | ((self.vram_addr.coarse_y >> 2) << 3) 
                                                    | (self.vram_addr.coarse_x >> 2))
                if (self.vram_addr.coarse_y & 0x02):
                    self.bg_next_tile_attrib >>= 4
                if (self.vram_addr.coarse_x & 0x02):
                    self.bg_next_tile_attrib >>= 2
                self.bg_next_tile_attrib = self.bg_next_tile_attrib.value & 0x03
            elif (case == 4):
                self.bg_next_tile_lsb = self.ppuRead((self.control.pattern_background << 12)
                                        + (self.bg_next_tile_id << 4)
                                        + (self.vram_addr.fine_y) + 0)
            elif (case == 6):
                self.bg_next_tile_msb = self.ppuRead((self.control.pattern_background << 12)
                                        + (self.bg_next_tile_id << 4)
                                        + (self.vram_addr.fine_y) + 8)
            else:
                IncrementScrollX()
                
        if (self.cycle == 256):
            IncrementScrollY()
            
        if (self.cycle == 257):
            LoadBackgroundShifters()
            TransferAddressX()
            
        if (self.cycle == 338 or self.cycle == 340):
            self.bg_next_tile_id = self.ppuRead(0x2000 | (self.vram_addr.reg & 0x0FFF)).value
            
        if (self.scanline == -1 and self.cycle >= 280 and self.cycle < 305):
            TransferAddressY()

        # # TODO: Foreground Rendering
        # # Some code here
        if self.cycle == 257 and self.scanline >= 0:
            self.spriteScanline = [0]*32
            self.spriteCount = 0

            bSpriteZeroHitPossible = False

            entry = 0
            while entry < 256 and self.spriteCount < 33:
                diff = self.scanline - self.oam[entry]
                if diff >= 0 and diff < 16 if control.sprite_size else 8:
                    if self.spriteCount < 32:
                        if entry == 0:
                            bSpriteZeroHitPossible = True

                        self.spriteScanline[self.spriteCount] = self.oam[entry]
                        self.spriteScanline[self.spriteCount + 1] = self.oam[entry + 1]
                        self.spriteScanline[self.spriteCount + 2] = self.oam[entry + 2]
                        self.spriteScanline[self.spriteCount + 3] = self.oam[entry + 3]

                        self.spriteCount += 4
                entry += 4
            self.status.sprite_overflow = self.spriteCount > 8
        
        if self.cycle == 340:
            for i in range(0, self.spriteCount, 4):
                if not self.control.sprite_size:
                    # 8x8 Sprite Mode
                    if not (self.spriteScanline[i + 2] & 0x80): #Sprite is NOT flipped vertically, i.e. normal
                        sprite_pattern_addr_lo = (self.control.pattern_sprite << 12) | (self.spriteScanline[i+1] << 4) | (self.scanline - self.spriteScanline[i])
                    else:   # shifted vertically
                        sprite_pattern_addr_lo = (self.control.pattern_sprite << 12) | (self.spriteScanline[i+1] << 4) | (7 - (self.scanline - self.spriteScanline[i]))
                else:
                    if not (self.spriteScanline[i + 2] & 0x80): # normal sprite, not shifted vertically
                        if self.scanline - self.spriteScanline[i] < 8:
                            sprite_pattern_addr_lo = ((self.spriteScanline[i+1] & 0x01) << 12) | ((self.spriteScanline[i+1] & 0xFE) << 4) | ((self.scanline - self.spriteScanline[i]) & 0x07)
                        else:
                            sprite_pattern_addr_lo = ((self.spriteScanline[i+1] & 0x01) << 12) | (((self.spriteScanline[i+1] & 0xFE) +1) << 4) | ((self.scanline - self.spriteScanline[i]) & 0x07)
                    else:  
                        if self.scanline - self.spriteScanline[i] < 8:
                            sprite_pattern_addr_lo = ((self.spriteScanline[i+1] & 0x01) << 12) | (((self.spriteScanline[i+1] & 0xFE)+1) << 4) | (7 - (self.scanline - self.spriteScanline[i]) & 0x07)
                        else:
                            sprite_pattern_addr_lo = ((self.spriteScanline[i+1] & 0x01) << 12) | ((self.spriteScanline[i+1] & 0xFE) << 4) | (7 - (self.scanline - self.spriteScanline[i]) & 0x07)

                sprite_pattern_addr_hi = sprite_pattern_addr_lo + 8
                sprite_pattern_bits_lo = self.ppuRead(sprite_pattern_addr_lo)
                sprite_pattern_bits_hi = self.ppuRead(sprite_pattern_addr_hi)

                def flipbyte(b):
                    b = (b & 0xF0) >> 4 | (b & 0x0F) << 4
                    b = (b & 0xCC) >> 2 | (b & 0x33) << 2
                    b = (b & 0xAA) >> 1 | (b & 0x55) << 1
                    return b
				
                if self.spriteScanline[i+2] & 0x40:
                    sprite_pattern_bits_lo = flipbyte(sprite_pattern_bits_lo)
                    sprite_pattern_bits_hi = flipbyte(sprite_pattern_bits_hi)

                self.sprite_shifter_pattern_lo[i] = sprite_pattern_bits_lo
                self.sprite_shifter_pattern_hi[i] = sprite_pattern_bits_hi

        if (self.scanline >= 241 and self.scanline < 261):
            if (self.scanline == 241 and self.cycle == 1):
                self.status.vertical_blank = 1
                if (self.control.enable_nmi):
                    self.nmi = True

        # Background check

        bg_pixel = 0x00
        bg_palette = 0x00
        if (self.mask.render_background):
            bit_mux = 0x8000 >> self.fine_x

            p0_pixel = (self.bg_shifter_pattern_lo & bit_mux) > 0
            p1_pixel = (self.bg_shifter_pattern_hi & bit_mux) > 0

            bg_pixel = (p1_pixel << 1) | p0_pixel

            bg_pal0 = (self.bg_shifter_attrib_lo & bit_mux) > 0
            bg_pal1 = (self.bg_shifter_attrib_hi & bit_mux) > 0
            bg_palette = (bg_pal1 << 1) | bg_pal0

        # TODO: Foreground check
        fg_pixel = 0x00
        fg_palette = 0x00
        fg_priority = 0x00

        if (self.mask.render_sprites):
            bSpriteZeroBeingRendered = False

            j = 0
            for i in range(0, self.spriteCount, 4):
                if (self.spriteScanline[i+3] == 0):
                    fg_pixel_lo = (self.sprite_shifter_pattern_lo[j] & 0x80) > 0
                    fg_pixel_hi = (self.sprite_shifter_pattern_hi[j] & 0x80) > 0
                    fg_pixel = (fg_pixel_hi << 1) | fg_pixel_lo

                    fg_palette = (self.spriteScanline[i+2] & 0x03) + 0x04
                    fg_priority = (self.spriteScanline[i+2] & 0x20) == 0

                    if fg_pixel != 0:
                        if i == 0:
                            bSpriteZeroBeingRendered = True
                        break
                j += 1

        # Pixel
        pixel = 0x00
        palette = 0x00

        if (bg_pixel == 0 and fg_pixel == 0):
            pixel = 0x00
            palette = 0x00
        elif (bg_pixel == 0 and fg_pixel > 0):
            pixel = fg_pixel
            palette = fg_palette
        elif (bg_pixel > 0 and fg_pixel == 0):
            pixel = bg_pixel
            palette = bg_palette
        elif (bg_pixel > 0 and fg_pixel > 0):
            if (fg_priority):
                pixel = fg_pixel
                palette = fg_palette
            else:
                pixel = bg_pixel
                palette = bg_palette

            if (bSpriteZeroHitPossible and bSpriteZeroBeingRendered):
                if (self.mask.render_background & self.mask.render_sprites):
                    if (~(self.mask.render_background_left | self.mask.render_sprites_left)):
                        if (self.cycle >= 9 and self.cycle < 258):
                            status.sprite_zero_hit = 1
                    else:
                        if (self.cycle >= 1 and self.cycle < 258):
                            status.sprite_zero_hit = 1

        self.window.draw_pixel(self.cycle - 1, self.scanline,  self.getColor(palette, pixel))

        self.cycle += 1
        if self.cycle >= 341:
            self.cycle = 0
            self.scanline += 1

            if self.scanline >= 261:
                self.scanline = -1
                self.frameComplete = True
