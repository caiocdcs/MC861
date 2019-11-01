int8 = int

KB = 1024

class BUS:

    def __init__(self, cpu, ppu, controller1, controller2):
       self.cpu = cpu
       self.ppu = ppu
       self.cpuRam = [int8(0)]*2*KB
       self.clockCounter = 0
       self.controller1 = controller1
       self.controller2 = controller2
       self.consoleState1 = 0b000000000
       self.consoleState2 = 0b000000000

       self.dma_page = 0x00
       self.dma_addr = 0x00
       self.dma_transfer = False
       self.dma_data = 0x00
       self.dma_even = True

    def cpuRead(self, address, readOnly = True):
        data = int8(0)

        cartridgeData = self.cartridge.cpuRead(address)
        if cartridgeData != None:
            data = cartridgeData
        elif address >= 0x0000 and address <= 0x1FFF:
            data = self.cpuRam[address & 0x07FF]
        elif address >= 0x2000 and address <= 0x3FFF:
            self.ppu.cpuRead(address & 0x0007)
        elif address == 0x4016:
            data = int8(self.consoleState1 & 0x80) >> 7
            # print("{0:b}".format(self.consoleState1))
            self.consoleState1 = self.consoleState1 << 1 & 0xFF
        elif address == 0x4017: # console 2
            pass

        return data  

    def cpuWrite(self, address, data):
        if self.cartridge.cpuWrite(address, data):
            pass
        elif 0x0000 <= address <= 0x1FFF:
            self.cpuRam[address & 0x07FF] = data
        elif 0x2000 <= address <= 0x3FFF:
            self.ppu.cpuWrite(address & 0x0007, data)
        elif address == 0x4014:
            self.dma_page = data
            self.dma_addr = 0x00
            self.dma_transfer = True
        elif address >= 0x4016:
            # print("snapshot")
            self.consoleState1 = self.controller1.read()
        elif address <= 0x4017: # console 2
            pass

    def insertCartridge(self, cartridge):
        self.cartridge = cartridge
        self.ppu.insertCartridge(cartridge)

    def reset(self):
        self.cpu.reset()
        self.ppu.reset()
        self.clockCounter = 0
        self.dma_page = 0x00
        self.dma_addr = 0x00
        self.dma_data = 0x00
        self.dma_transfer = False
        self.dma_even = True

    def clock(self):
        self.ppu.clock()
        if self.clockCounter % 3 == 0:
            if self.dma_transfer:
                if self.dma_even:
                    if self.clockCounter % 2 == 1:
                        self.dma_even = False
                else:
                    if self.clockCounter % 2 == 0:
                        self.dma_data = self.cpuRead(self.dma_page << 8 | self.dma_addr)
                    else:
                        # TODO Check if this is right
                        if self.dma_addr == 0xff:
                            self.dma_transfer = False
                            self.dma_even = True
                            self.dma_addr = 0x00
                            
                        self.ppu.oam[self.dma_addr] = self.dma_data
                        self.dma_addr += 1
            else:
               self.cpu.clock()

        if self.ppu.getNmi():
            self.ppu.setNmi(False)
            self.cpu.nmi()
        
        self.clockCounter += 1

    def setFrame(self):
        while self.ppu.frameComplete == False:
            self.clock()

        self.ppu.frameComplete = False
        # self.cpu.nmi()
        # self.cpu.on_interrupt = False
        # self.clockCounter = 0
