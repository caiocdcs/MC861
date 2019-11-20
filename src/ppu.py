from memory import *
from palette import *
from defines import *

class PPU:
    def __init__(self, console):
        self.console = console
        self.Cycle = 0
        self.ScanLine = 0
        self.Frame = uint64(0)

        # storage variables 
        self.paletteData = np.zeros(32, dtype=uint8)
        self.nameTableData = np.zeros(2048, dtype=uint8)
        self.oamData = np.zeros(256, dtype=uint8)

        # PPU registers
        self.v = uint16(0)
        self.t = uint16(0)

        self.x = uint8(0)
        self.w = uint8(0)
        self.f = uint8(0)

        self.register = uint8(0)

        self.nmiOccurred = False
        self.nmiOutput = False
        self.nmiPrevious = False
        self.nmiDelay = 0

        self.nameTableByte = uint8(0)
        self.attributeTableByte = uint8(0)
        self.lowTileByte = uint8(0)
        self.highTileByte = uint8(0)

        self.tileData = uint64(0)

        self.spriteCount = 0
        self.spritePatterns = np.zeros(8, dtype=uint32)
        self.spritePositions = np.zeros(8, dtype=uint8)
        self.spritePriorities = np.zeros(8, dtype=uint8)
        self.spriteIndexes = np.zeros(8, dtype=uint8)

        self.flagNameTable = uint8(0)
        self.flagIncrement = uint8(0)
        self.flagSpriteTable = uint8(0)
        self.flagBackgroundTable = uint8(0)
        self.flagSpriteSize = uint8(0)
        self.flagMasterSlave = uint8(0)

        self.flagGrayscale = uint8(0)
        self.flagShowLeftBackground = uint8(0)
        self.flagShowLeftSprites = uint8(0)
        self.flagShowBackground = uint8(0)
        self.flagShowSprites = uint8(0)
        self.flagRedTint = uint8(0)
        self.flagGreenTint = uint8(0)
        self.flagBlueTint = uint8(0)

        self.flagSpriteZeroHit = uint8(0)
        self.flagSpriteOverflow = uint8(0)

        self.oamAddress = uint8(0)
        self.bufferedData = uint8(0)

        # width: 256
        # height: 240
        #self.front = np.zeros((240, 256, 3), dtype = np.uint8)
        #self.back = np.zeros((240, 256, 3), dtype = np.uint8)
        self.front = np.zeros(240*256*3, dtype=uint8)
        self.back = np.zeros(240*256*3, dtype=uint8)

        self.Reset()

        '''
        self.step_func = [self.storeTileData, self.fetchNameTableByte, 
                          self.emptyFunc, self.fetchAttributeTableByte, 
                          self.emptyFunc, self.fetchLowTileByte,
                          self.emptyFunc, self.fetchHighTileByte ]
        self.write_reg_ops = [self.writeControl, self.writeMask, self.emptyFunc_b, self.writeOAMAddress, self.writeOAMData, self.writeScroll, self.writeAddress, self.writeData]
        '''
    def emptyFunc(self):
        pass
    def emptyFunc_b(self, uint8):
        pass
    def Reset(self):
        self.Cycle = 340
        self.ScanLine = 240
        self.Frame = 0
        self.writeControl(0)
        self.writeMask(0)
        self.writeOAMAddress(0)

    def Read(self, address):
        address = address & 0x3FFF
        if address < 0x2000:
            return self.console.Mapper.Read(address)
        elif address < 0x3F00:
            mode = self.console.Cartridge.Mirror
            return self.nameTableData[MirrorAddress(mode, address) & 0x7FF]
        elif address < 0x4000:
            return self.readPalette(address & 0x1F)
        raise RuntimeError("Unhandled PPU Memory read at address: 0x%04X" % address)

    def Write(self, address, value):
        address = address & 0x3FFF
        if address < 0x2000:
            self.console.Mapper.Write(address, value)
        elif address < 0x3F00:
            mode = self.console.Cartridge.Mirror
            self.nameTableData[MirrorAddress(mode, address) & 0x7FF] = value
        elif address < 0x4000:
            self.writePalette(address & 0x1F, value)
        else:
            raise RuntimeError("Unhandled PPU Memory write at address: 0x%04X" % address)

    def readPalette(self, address):
        address = uint16(address)
        if address >= 16 and address & 0x3 == 0:
            address -= 16
        return self.paletteData[address]

    def writePalette(self, address, value):
        address = uint16(address)
        value = uint8(value)
        if address >= 16 and address & 0x3 == 0:
            address -= 16
        self.paletteData[address] = value

    def ReadRegister(self, address):
        address = uint16(address)
        if address == 0x2002:
            return self.readStatus()
        elif address == 0x2004:
            return self.readOAMData()
        elif address == 0x2007:
            return self.readData()
        return 0

    def WriteRegister(self, address, value):
        address = uint16(address)
        value = uint8(value)
        self.register = value
        if address == 0x4014:
            self.writeDMA(value)
        elif address == 0x2000:
            self.writeControl(value)
        elif address == 0x2001:
            self.writeMask(value)
        elif address == 0x2003:
            self.writeOAMAddress(value)
        elif address == 0x2004:
            self.writeOAMData(value)
        elif address == 0x2005:
            self.writeScroll(value)
        elif address == 0x2006:
            self.writeAddress(value)
        elif address == 0x2007:
            self.writeData(value)
            #self.write_reg_ops[address - 0x2000](value)
        '''
        ops = {
                0x2000: self.writeControl,
                0x2001: self.writeMask,
                0x2003: self.writeOAMAddress,
                0x2004: self.writeOAMData,
                0x2005: self.writeScroll,
                0x2006: self.writeAddress,
                0x2007: self.writeData,
                0x4014: self.writeDMA
        }
        ops[address](value)
        '''

    def writeControl(self, value):
        self.flagNameTable = (value >> 0) & 3
        self.flagIncrement = (value >> 2) & 1
        self.flagSpriteTable = (value >> 3) & 1
        self.flagBackgroundTable = (value >> 4) & 1
        self.flagSpriteSize = (value >> 5) & 1
        self.flagMasterSlave = (value >> 6) & 1
        self.nmiOutput = (((value >> 7) & 1) == 1)
        self.nmiChange()
        self.t = ((self.t & 0xF3FF) | ((value & 0x03) << 10))

    def writeMask(self, value):
        self.flagGrayscale = (value >> 0) & 1
        self.flagShowLeftBackground = (value >> 1) & 1
        self.flagShowLeftSprites = (value >> 2) & 1
        self.flagShowBackground = (value >> 3) & 1
        self.flagShowSprites = (value >> 4) & 1
        self.flagRedTint = (value >> 5) & 1
        self.flagGreenTint = (value >> 6) & 1
        self.flagBlueTint = (value >> 7) & 1

    def readStatus(self):
        result = self.register & 0x1F
        result |= (self.flagSpriteOverflow << 5)
        result |= (self.flagSpriteZeroHit << 6)
        if self.nmiOccurred:
            result |= (1 << 7)
        self.nmiOccurred = False
        self.nmiChange()
        self.w = 0
        return result

    def writeOAMAddress(self, value):
        self.oamAddress = uint8(value)

    def readOAMData(self):
        return uint8(self.oamData[self.oamAddress])

    def writeOAMData(self, value):
        self.oamData[self.oamAddress] = uint8(value)
        self.oamAddress = (self.oamAddress + 1) & 0xFF 

    def writeScroll(self, value):
        if self.w == 0:
            self.t = uint16((self.t & uint16(0xFFE0)) | uint16(uint16(value) >> uint16(3)))
            self.x = uint8(value) & uint8(0x07)
            self.w = uint8(1)
        else:
            self.t = uint16((self.t & uint16(0x8FFF)) | ((uint16(value) & uint16(0x07)) << uint16(12)))
            self.t = uint16((self.t & uint16(0xFC1F)) | ((uint16(value) & uint16(0xF8)) << uint16(2)))
            # self.t twice!
            self.w = uint8(0)

    def writeAddress(self, value):
        if self.w == 0:
            self.t = uint16((self.t & uint16(0x80FF)) | ((uint16(value) & uint16(0x3F)) << uint16(8)))
            self.w = uint8(1)
        else:
            self.t = uint16((self.t & uint16(0xFF00)) | uint16(value))
            self.v = self.t
            self.w = uint8(0)

    def readData(self):
        value = uint8(self.Read(uint16(self.v)))
        if self.v & uint16(0x3FFF) < uint16(0x3F00):
            buffered = uint8(self.bufferedData)
            self.bufferedData = value
            value = buffered
        else:
            self.bufferedData = self.Read(uint16(self.v - uint16(0x1000)))

        if self.flagIncrement == 0:
            self.v = uint16(self.v + uint16(1))
        else:
            self.v = uint16(self.v + uint16(32))
        return uint8(value)

    def writeData(self, value):
        self.Write(uint16(self.v), uint8(value))
        if self.flagIncrement == 0:
            self.v = uint16(self.v + uint16(1))
        else:
            self.v = uint16(self.v + uint16(32))

    def writeDMA(self, value):
        cpu = self.console.CPU
        address = uint16(uint16(value) << uint16(8))
        for _ in range(256):
            self.oamData[self.oamAddress] = cpu.Read(address)
            self.oamAddress = (self.oamAddress + 1)
            address = (address + 1)
        # self.oamAddress = 0

    def incrementX(self):
        if self.v & uint16(0x001F) == uint16(31):
            self.v &= uint16(0xFFE0)
            self.v ^= uint16(0x0400)
        else:
            self.v = (self.v + uint16(1))

    def incrementY(self):
        if self.v & uint16(0x7000) != uint16(0x7000):
            self.v = (self.v + uint16(0x1000))
        else:
            self.v &= uint16(0x8FFF)
            y = uint16(self.v & uint16(0x03E0)) >> uint16(5)
            if y == uint16(29):
                y = uint16(0)
                self.v ^= uint16(0x0800)
            elif y == uint16(31):
                y = uint16(0)
            else:
                y = uint16(y + uint16(1))
            self.v = (self.v & uint16(0xFC1F)) | (y << uint16(5))

    def copyX(self):
        self.v = (self.v & uint16(0xFBE0)) | (self.t & uint16(0x041F))

    def copyY(self):
        self.v = (self.v & uint16(0x841F)) | (self.t & uint16(0x7BE0))

    def nmiChange(self):
        nmi = (self.nmiOutput and self.nmiOccurred)
        if nmi and not self.nmiPrevious:
            self.nmiDelay = 15
        self.nmiPrevious = nmi

    def setVerticalBlank(self):
        self.front, self.back = self.back, self.front
        self.nmiOccurred = True
        self.nmiChange()

    def clearVerticalBlank(self):
        self.nmiOccurred = False
        self.nmiChange()

    def fetchNameTableByte(self):
        v = self.v
        address = uint16(0x2000) | (v & uint16(0x0FFF))
        self.nameTableByte = uint8(self.Read(address))

    def fetchAttributeTableByte(self):
        v = self.v
        address = uint16(0x23C0) | (v & uint16(0x0C00)) | ((v >> uint16(4)) & uint16(0x38)) | ((v >> uint16(2)) & uint16(0x07))
        shift = ((v >> uint16(4)) & uint16(4)) | (v & uint16(2))
        self.attributeTableByte = uint8(((self.Read(uint16(address)) >> uint16(shift)) & uint16(3)) << uint16(2))

    def fetchLowTileByte(self):
        fineY = uint8(self.v >> uint16(12)) & uint8(7)
        table = self.flagBackgroundTable
        tile = self.nameTableByte
        address = (uint16(table) << uint16(12)) + uint16(uint8(tile) << uint16(4)) + uint16(fineY)
        self.lowTileByte = uint8(self.Read(address))

    def fetchHighTileByte(self):
        fineY = (self.v >> uint16(12)) & uint8(7)
        table = self.flagBackgroundTable
        tile = self.nameTableByte
        address_8 = (uint16(table) << uint16(12)) + (uint16(tile) << uint16(4)) + uint16(fineY) + uint16(8)
        self.highTileByte = uint8(self.Read(address_8))

    def storeTileData(self):
        data = uint64(0)
        a = self.attributeTableByte
        for _ in range(8):
            p1 = uint8((self.lowTileByte & 0x80) >> 7)
            p2 = uint8((self.highTileByte & 0x80) >> 6)
            self.lowTileByte <<= uint8(1) 
            self.highTileByte <<= uint8(1)
            data <<= uint64(4)
            data |= (uint64(a) | uint64(p1) | uint64(p2))
        self.tileData |= uint64(data)

    def backgroundPixel(self):
        if self.flagShowBackground == 0:
            return 0
        data = (self.tileData >> uint64(32)) >> (uint64((uint64(7) - uint64(self.x)) << uint64(2)))
        return uint8(data) & uint8(0x0F)

    def spritePixel(self): 
        if self.flagShowSprites == 0:
            return 0,0 
        for i in range(self.spriteCount):
            offset = (self.Cycle - 1) - self.spritePositions[i]
            if offset < 0 or offset > 7:
                continue
            offset = 7 - offset
            color = uint8((self.spritePatterns[i] >> uint32(offset << 2)) & uint32(0x0F))
            if color & 0x3 == 0:
                continue
            return i, color
        return 0,0 

    def renderPixel(self):
        x = self.Cycle - 1
        y = self.ScanLine
        background = self.backgroundPixel()
        i, sprite = self.spritePixel()
        if x < 8 and self.flagShowLeftBackground == 0:
            background = 0
        if x < 8 and self.flagShowLeftSprites == 0:
            sprite = 0
        b = (background & uint8(0x3) != 0)
        s = (sprite & uint8(0x3) != 0)
        color = 0

        if not b:
            if not s:
                color = 0
            else:
                # not b and s
                color = sprite | 0x10
        else:
            if not s:
                # b and not s
                color = background
            else:
                # b and s
                if self.spriteIndexes[i] == 0 and x < 255:
                    self.flagSpriteZeroHit = 1 
                if self.spritePriorities[i] == 0:
                    color = sprite | 0x10
                else:
                    color = background

        c = Palette[self.readPalette(color) & 0x3F]
        p = (y * 256 + x) * 3
        self.back[p + 0] = c[0]
        self.back[p + 1] = c[1]
        self.back[p + 2] = c[2]

    def fetchSpritePattern(self, i, row):
        k = (i << 2) + 1
        tile = self.oamData[k]
        attributes = self.oamData[k + 1]
        address = 0
        if self.flagSpriteSize == 0:
            if attributes & 0x80 == 0x80:
                row = 7 - row
            table = self.flagSpriteTable
            address = uint16(((uint16(table) << 12) + (uint16(tile) << 4) + uint16(row)))
        else:
            if attributes & 0x80 == 0x80:
                row = 15 - row
            table = tile & 1
            tile &= 0xFE
            if row > 7:
                tile += 1
                row -= 8
            address = uint16(((uint16(table) << 12)+ (tile << 4) + uint16(row)))
        a = (attributes & 3) << 2
        lowTileByte = self.Read(address)
        highTileByte = self.Read((address + 8))
        data = uint32(0)
        for i in range(8):
            if attributes & 0x40 == 0x40:
                p1 = uint32(lowTileByte) & 1
                p2 = ((uint32(highTileByte) & 1) << 1)
                lowTileByte >>= 1
                highTileByte >>= 1
            else:
                p1 = uint32((uint32(lowTileByte) & 0x80) >> 7)
                p2 = uint32((uint32(highTileByte) & 0x80) >> 6)
                lowTileByte = lowTileByte << 1
                highTileByte = highTileByte << 1
            data <<= uint32(4)
            data |= (uint32(a) | uint32(p1) | uint32(p2))
        return uint32(data)

    def evaluateSprites(self):
        h = 8 if self.flagSpriteSize == 0 else 16
        count = 0
        for i in range(64):
            k = (i << 2)
            y = self.oamData[k]
            a = self.oamData[k + 2]
            x = self.oamData[k + 3]
            row = self.ScanLine - y
            if row < 0 or row >= h:
                continue
            if count < 8:
                self.spritePatterns[count] = self.fetchSpritePattern(i, row)
                self.spritePositions[count] = x
                self.spritePriorities[count] = (a >> 5) & 1
                self.spriteIndexes[count] = i
            count += 1
        if count > 8:
            count = 8
            self.flagSpriteOverflow = 1
        self.spriteCount = count

    def tick(self):
        if self.nmiDelay > 0:
            self.nmiDelay -= 1 
            if self.nmiDelay == 0 and self.nmiOutput and self.nmiOccurred:
                self.console.CPU.triggerNMI = True

        if self.flagShowBackground != 0 or self.flagShowSprites != 0:
            if self.f == 1 and self.ScanLine == 261 and self.Cycle == 339:
                self.Cycle = 0
                self.ScanLine = 0
                self.Frame += 1
                self.f ^= 1
                return

        self.Cycle += 1
        if self.Cycle > 340:
            self.Cycle = 0
            self.ScanLine += 1
            if self.ScanLine > 261:
                self.ScanLine = 0
                self.Frame += 1
                self.f ^= 1

    def Step(self):
        self.tick()

        renderingEnabled = (self.flagShowBackground != 0) or (self.flagShowSprites != 0)
        preLine = (self.ScanLine == 261)
        visibleLine = (self.ScanLine < 240)

        # background logic
        if renderingEnabled:
            preFetchCycle = (self.Cycle >= 321) and (self.Cycle <= 336)
            visibleCycle = (self.Cycle >= 1) and (self.Cycle <= 256)
            fetchCycle = preFetchCycle or visibleCycle
            renderLine = preLine or visibleLine
            if visibleLine and visibleCycle:
                self.renderPixel()
            if renderLine and fetchCycle:
                self.tileData <<= uint64(4)
                c = self.Cycle & 0x7
                '''
                self.step_func = [self.storeTileData, self.fetchNameTableByte, 
                                  self.emptyFunc, self.fetchAttributeTableByte, 
                                  self.emptyFunc, self.fetchLowTileByte,
                                  self.emptyFunc, self.fetchHighTileByte ]
                '''
                if c == 0:
                    self.storeTileData()
                elif c == 1:
                    self.fetchNameTableByte()
                elif c == 3:
                    self.fetchAttributeTableByte()
                elif c == 5:
                    self.fetchLowTileByte()
                elif c == 7:
                    self.fetchHighTileByte()
                #self.step_func[c]()

            if preLine and self.Cycle >= 280 and self.Cycle <= 304:
                self.copyY()
            if renderLine:
                if fetchCycle and self.Cycle & 0x7 == 0:
                    self.incrementX()
                if self.Cycle == 256:
                    self.incrementY()
                if self.Cycle == 257:
                    self.copyX()
            # sprite logic
            if self.Cycle == 257:
                if visibleLine:
                    self.evaluateSprites()
                else:
                    self.spriteCount = 0

        # vblank logic
        if self.ScanLine == 241 and self.Cycle == 1:
            self.setVerticalBlank()
        if preLine and self.Cycle == 1:
            self.clearVerticalBlank()
            self.flagSpriteZeroHit = 0
            self.flagSpriteOverflow = 0
