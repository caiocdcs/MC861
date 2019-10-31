class Mapper0:

    def __init__(self, prgBanks, chrBanks):
        self.prgBanks = prgBanks
        self.chrBanks = chrBanks

    def cpuMapRead(self, address):
        if address >= 0x8000 and address <= 0xFFFF:
            mappedAddress = address & (0x7FFF if self.prgBanks > 1 else 0x3FFF)
            return mappedAddress
        return None

    def cpuMapWrite(self, address):
        if address >= 0x8000 and address <= 0xFFFF:
            mappedAddress = address & (0x7FFF if self.prgBanks > 1 else 0x3FFF)
            return mappedAddress
        return None

    def ppuMapRead(self, address):
        if address >= 0x0000 and address <= 0x1FFF:
            mappedAddress = address
            return mappedAddress
        return None

    def ppuMapWrite(self, address):
        return None