from controller import *
from mapper import *
from cpu import CPU
from ppu import PPU
from palette import *
import struct
from cartridge import *

CPUFrequency = 1789773
iNESFileMagic = b'NES\x1a'

uint8 = int
ordc = lambda c: c if type(c) ==int else ord(c)
fromstring = lambda x, dtype : [dtype(ordc(c)) for c in x]


class Bus:
    def __init__(self, path):

        cartridge, _ = self.loadRom(path)
        ram = [0 for _ in range(2048)] 
        controller1 = Controller()
        controller2 = Controller()

        self.Cartridge = cartridge
        self.Controller1 = controller1
        self.Controller2 = controller2
        self.RAM = ram

        mapper = Mapper(self.Cartridge)

        self.Mapper = mapper
        self.CPU = CPU(self)
        self.PPU = PPU(self)

    def loadRom(self, path):
        print("Loading %s" % path)
        fin = open(path, "rb")
        Magic, NumPRG, NumCHR, Control1, Control2, NumRAM, _ = struct.unpack("<4sccccc7s", fin.read(16))
        if Magic != iNESFileMagic:
            raise RuntimeError("Invalid .nes File")

        NumPRG = uint8(ord(NumPRG))
        NumCHR = uint8(ord(NumCHR))
        Control1 = uint8(ord(Control1))
        Control2 = uint8(ord(Control2))

        mapper1 = (Control1 >> uint8(4))
        mapper2 = (Control2 >> uint8(4))
        mapper = mapper1 | (mapper2 << uint8(4))

        mirror1 = Control1 & uint8(1)
        mirror2 = (Control1 >> uint8(3)) & uint8(1)
        mirror = mirror1 | (mirror2 << uint8(1))

        battery = (Control1 >> uint8(1)) & uint8(1)

        # read trainer if present (unused)
        if Control1 & uint8(4) == uint8(4):
            fin.read(512)

        # read prg-rom bank(s)
        prg = fromstring(fin.read(16384 * NumPRG), uint8)
        # read chr-rom bank(s)
        _chr = fromstring(fin.read(8192 * NumCHR), uint8)

        if NumCHR == 0:
            _chr = [0 for _ in range(8192)]
        return Cartridge(prg, _chr, mapper, mirror, battery), None

    def reset(self):
        self.CPU.reset()
    
    def step(self):
        cpuCycles = self.CPU.step()
        ppuCycles = cpuCycles * 3
        for _ in range(ppuCycles):
            self.PPU.Step()
            self.Mapper.Step()
        return cpuCycles

    def stepFrame(self):
        cpuCycles = 0
        frame = self.PPU.Frame
        while frame == self.PPU.Frame:
            cpuCycles += self.step()
        return cpuCycles

    def stepSeconds(self, seconds):
        cycles = int(CPUFrequency * seconds)
        while cycles > 0:
            cycles -= self.step()

    def buffer(self):
        return self.PPU.front 

    def backgroundColor(self):
        return Palette[self.PPU.readPalette(0) & 0x3F]

    def setButtons1(self, buttons):
        self.Controller1.setButtons(buttons)
    def setButtons2(self, buttons):
        self.Controller2.setButtons(buttons)