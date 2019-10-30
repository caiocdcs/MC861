from ctypes import c_uint16, c_uint8

KB = 1024

class BUS:

    def __init__(self, cpu, ppu):
       self.cpu = cpu
       self.ppu = ppu
       self.cpuRam = [c_uint8(0)]*2*KB
       self.clockCounter = 0

    def cpuRead(self, address, readOnly):
        data = c_uint8(0)

        if address >= 0x0000 and address <= 0x1FFF:
            data = self.cpuRam[address & 0x07FF]
        elif address >= 0x2000 and address <= 0x3FFF:
            self.ppu.cpuRead(address & 0x0007, readOnly)

        return data  

    def cpuWrite(self, address, data):
        if address >= 0x0000 and address <= 0x1FFF:
            self.cpuRam[address & 0x07FF] = data
        elif address >= 0x2000 and address <= 0x3FFF:
            self.ppu.cpuWrite(address & 0x0007, data)


    def insertCartridge(self, cartridge):
        self.cartridge = cartridge
        self.ppu.insertCartridge(cartridge)

    def reset(self):
        self.cpu.reset()
        self.clockCounter = 0