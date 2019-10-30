from mapper0 import Mapper0 

class Cartridge:

    def __init__(self, program_name):
        file = open(program_name, "rb")
        self.prgMemory = file.read().hex()
        self.mapperId = 0
        self.prgBanks = 0
        self.chrBanks = 0
        self.mapper0 = Mapper0(self.prgBanks, self.chrBanks)

    def cpuRead(self, address):
        mappedAddress = self.mapper0.cpuMapRead(address)
        if mappedAddress != None :
            data = self.prgMemory[mappedAddress] 
            return data
        return None

    def cpuWrite(self, address, data):
        mappedAddress = self.mapper0.cpuMapWrite(address)
        if mappedAddress != None :
            self.prgMemory[mappedAddress] = data
            return True
        return False

    def ppuRead(self, address):
        mappedAddress = self.mapper0.ppuMapRead(address)
        if mappedAddress != None :
            data = self.prgMemory[mappedAddress] 
            return data
        return None

    def ppuWrite(self, address, data):
        mappedAddress = self.mapper0.ppuMapWrite(address)
        if mappedAddress != None :
            self.prgMemory[mappedAddress] = data
            return True
        return False
