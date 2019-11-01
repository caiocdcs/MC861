from mapper import Mapper
import struct

KB = 1024

int8 = int

uint8 = int
ordc = lambda c:c if type(c) ==int else ord(c)
fromstring = lambda x, dtype : [dtype(ordc(c)) for c in x]

class Cartridge:

    def __init__(self, fileName):
        self.mapperId = 0
        self.prgBanks = 0
        self.chrBanks = 0
        self.mapper = Mapper()
        self.loadFile(fileName)

    def cpuRead(self, address):
        mappedAddress = 0
        mappedAddress = self.mapper.cpuMapRead(address)
        if mappedAddress != None :
            data = self.prgMemory[mappedAddress] 
            return data
        return None

    def cpuWrite(self, address, data):
        mappedAddress = 0
        mappedAddress = self.mapper.cpuMapWrite(address)
        if mappedAddress != None :
            self.prgMemory[mappedAddress] = data
            return True
        return False

    def ppuRead(self, address):
        mappedAddress = 0
        mappedAddress = self.mapper.ppuMapRead(address)
        if mappedAddress != None :
            data = self.chrMemory[mappedAddress] 
            return data
        return None

    def ppuWrite(self, address, data):
        mappedAddress = 0
        mappedAddress = self.mapper.ppuMapWrite(address)
        if mappedAddress != None :
            self.chrMemory[mappedAddress] = data
            return True
        return False

    def getMirror(self):
        return self.mirror

    def loadFile(self, fileName):
        file = open(fileName, "rb")

        name, numPRG, numCHR, control1, control2, ramSize, tv_system1, tv_system2, _ = struct.unpack("<4sccccccc5s", file.read(16))

        if name != b'NES\x1a':
            raise RuntimeError("Invalid .nes File")

        numPRG = uint8(ord(numPRG))
        numCHR = uint8(ord(numCHR))
        control1 = uint8(ord(control1))
        control2 = uint8(ord(control2))
        ramSize = uint8(ord(ramSize))
        tv_system1 = uint8(ord(tv_system1))
        tv_system2 = uint8(ord(tv_system2))

        mapper1 = (control1 >> uint8(4))
        mapper2 = (control2 >> uint8(4))
        self.mapperId = mapper1 | (mapper2 << uint8(4))

        mirror1 = control1 & uint8(1) 
        mirror2 = (control1 >> uint8(3)) & uint8(1)
        self.mirror = mirror1 | (mirror2 << uint8(1))

        self.battery = (control1 >> uint8(1)) & uint8(1)

        if control1 & uint8(4) == uint8(4):
            file.read(512)

        self.prgMemory = fromstring(file.read(16*KB * numPRG), uint8)
        
        if numCHR == 0:
            self.chrMemory = fromstring(file.read(8*KB), uint8)
        else:
            self.chrMemory = fromstring(file.read(8*KB * numCHR), uint8)

        self.mapper.connect(numPRG, numCHR)

