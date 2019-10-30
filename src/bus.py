from ctypes import c_uint16, c_uint8

KB = 1024

class BUS:

    def __init__(self, cpu, ppu):
       self.cpu = cpu
       self.ppu = ppu
       self.cpuRam = [c_uint8(0)]*2*KB

    def cpuRead(self, address):
        data = c_uint8(0)

        if address >= 0x0000 and address <= 0x1FFF:
            newAddress = address & 0x07FF
            print (newAddress)
            data = self.cpuRam[newAddress]

        return data  

    def cpuWrite(self, address, data):
        if address >= 0x0000 and address <= 0x1FFF:
            self.cpuRam[address & 0x07FF] = data