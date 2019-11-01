from ctypes import c_uint16, c_uint8

KB = 1024

class BUS:

    def __init__(self, cpu, ppu):
       self.cpu = cpu
       self.ppu = ppu
       self.cpuRam = [c_uint8(0)]*2*KB
       self.clockCounter = 0

       self.dma_page = 0x00
       self.dma_addr = 0x00
       self.dma_data = 0x00

       self.dma_transfer = False
       self.dma_even = True

    def cpuRead(self, address, readOnly = True):
        data = c_uint8(0)

        cartridgeData = self.cartridge.cpuRead(address)
        if cartridgeData != None:
            data = cartridgeData
        if address >= 0x0000 and address <= 0x1FFF:
            data = self.cpuRam[address & 0x07FF]
        elif address >= 0x2000 and address <= 0x3FFF:
            self.ppu.cpuRead(address & 0x0007, readOnly)

        return data  

    def cpuWrite(self, address, data):
        if self.cartridge.cpuWrite(address, data):
            pass
        elif address >= 0x0000 and address <= 0x1FFF:
            self.cpuRam[address & 0x07FF] = data
        elif address >= 0x2000 and address <= 0x3FFF:
            self.ppu.cpuWrite(address & 0x0007, data)
        elif address == 0x4014:
            self.dma_page = data
            self.dma_addr = 0x00
            self.dma_transfer = True


    def insertCartridge(self, cartridge):
        self.cartridge = cartridge
        self.ppu.insertCartridge(cartridge)

    def reset(self):
        self.cpu.reset()
        self.clockCounter = 0

    def clock(self):
        self.ppu.clock()
        if self.clockCounter % 3 == 0:
            if self.dma_transfer:
                if self.dma_even:
                    if self.clockCounter % 2 == 1:
                        self.dma_even = False
                else:
                    if self.clockCounter % 2 == 0:
                        self.dma_data = self.cpuRead(self.dma_page.value << 8 | self.dma_addr).value
                    else:
                        if self.dma_addr == 0xff:
                            self.dma_transfer = False
                            self.dma_even = True
                            self.dma_addr = 0x00
                            
                        self.ppu.oam[self.dma_addr] = self.dma_data
                        self.dma_addr += 1
            else: 
                self.cpu.clock()
        self.clockCounter += 1

        if self.ppu.nmi:
            self.ppu.nmi = False
            self.cpu.nmi()

    def setFrame(self, dt):
        while self.ppu.frameComplete == False:
            self.clock()

        self.clockCounter = 0
        self.ppu.frameComplete = False