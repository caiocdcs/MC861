from ctypes import c_uint16, c_uint8

KB = 1024

class BUS:

    def __init__(self, cpu, ppu):
       self.cpu = cpu
       self.ppu = ppu
       self.cpuRam = [c_uint8(0)]*2*KB
       self.clockCounter = 0

    def cpuRead(self, address):
        data = c_uint8(0)

        cartridgeData = self.cartridge.cpuRead(address)
        if cartridgeData != None:
            data = cartridgeData
        if address >= 0x0000 and address <= 0x1FFF:
            data = self.cpuRam[address & 0x07FF]
        elif address >= 0x2000 and address <= 0x3FFF:
            self.ppu.cpuRead(address & 0x0007)

        return data  

    def cpuWrite(self, address, data):
        if self.cartridge.cpuWrite(address, data):
            pass
        elif address >= 0x0000 and address <= 0x1FFF:
            self.cpuRam[address & 0x07FF] = data
        elif address >= 0x2000 and address <= 0x3FFF:
            self.ppu.cpuWrite(address & 0x0007, data)


    def insertCartridge(self, cartridge):
        self.cartridge = cartridge
        self.ppu.insertCartridge(cartridge)

    def reset(self):
        self.cpu.reset()
        self.clockCounter = 0

    def clock(self):
        self.ppu.clock()
        if self.clockCounter % 3 == 0:
            self.cpu.clock()
        self.clockCounter += 1

    def setFrame(self, dt):
        while self.ppu.frameComplete == False:
            self.clock()

        self.clockCounter = 0
        self.ppu.frameComplete = False
        self.cpu.nmi()
        self.cpu.on_interrupt = False