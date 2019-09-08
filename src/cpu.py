from utils import log, logls
from ctypes import c_uint16, c_uint8
from memory import Memory
from flagController import FlagController

from math import ceil

class CPU:
    def __init__(self, program_name):
        file = open(program_name, "rb")
        self.program_code = file.read().hex()

        self.sp = c_uint16(0)
        self.pc = c_uint16(0)
        self.a = c_uint8(0)
        self.x = c_uint8(0)
        self.y = c_uint8(0)
        self.memory = Memory()
        self.flagController = FlagController()
    
    def log(self, address = None):
        if (address):
            p = self.flagController.getFlagsStatusByte()
            logls(self.a.value, self.x.value, self.y.value, self.sp.value, ceil(self.pc.value / 2), p, address, self.memory.get_memory_at_position(address).value)
        else:
            p = self.flagController.getFlagsStatusByte()
            log(self.a.value, self.x.value, self.y.value, self.sp.value, ceil(self.pc.value / 2), p)

    def get_next_byte(self):
        begin = self.pc.value
        self.pc.value = self.pc.value + 2
        end = self.pc.value
        byte = self.program_code[begin:end].upper()
        return byte

    ####################################################
    ##########      INSTRUCTION HANDLERS      ##########
    ####################################################

    ## INC Instructions
    def handleInstructionINX(self):
        self.x.value = self.x.value + 1
        self.flagController.setCarryFlag()

    def handleInstructionINY(self):
        self.y.value = self.y.value + 1

    ## DEC Instructions
    def handleInstructionDEX(self):
        self.x.value = self.x.value - 1

    def handleInstructionDEY(self):
        self.y.value = self.y.value - 1

    ## Transfer Instructions
    def handleInstructionTAX(self):
        self.x.value = self.a.value

    def handleInstructionTXA(self):
        self.a.value = self.x.value

    def handleInstructionTAY(self):
        self.y.value = self.a.value

    def handleInstructionTYA(self):
        self.a.value = self.y.value

    ## Load Instructions
    def handleInstructionLDAImmediate(self):
        byte = self.get_next_byte()
        immediate = int(byte, 16)
        self.a.value = immediate

    def handleInstructionLDXImmediate(self):
        byte = self.get_next_byte()
        immediate = int(byte, 16)
        self.x.value = immediate

    def handleInstructionLDYImmediate(self):
        byte = self.get_next_byte()
        immediate = int(byte, 16)
        self.y.value = immediate

    ## Store Instructions
    def handleInstructionSTXZeroPage(self):
        byte = self.get_next_byte()
        self.memory.set_memory_at_position(byte, self.x)

    def handleInstructionSTXZeroPageY(self):
        byte = self.get_next_byte()

        address = format((int(byte, 16) + self.y.value), '04x')
        self.memory.set_memory_at_position(address, self.x)
        self.log(address)

    def handleInstructionSTXAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)

        self.memory.set_memory_at_position(address, self.x)

    def handleInstructionSTYZeroPage(self):
        byte = self.get_next_byte()
        self.memory.set_memory_at_position(byte, self.y)

    def handleInstructionSTYZeroPageY(self):
        byte = self.get_next_byte()

        address = format((int(byte, 16) + self.x.value), '04x')
        self.memory.set_memory_at_position(address, self.y)

    def handleInstructionSTYAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)

        self.memory.set_memory_at_position(address, self.y)

    ## Jump Instructions
    def handleInstructionJmpAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        self.pc.value = int(address, 16) * 2

    def handleInstructionJmpIndirect(self):
        byte = self.get_next_byte()
        byte_h = str(int(byte, 16) + 1)
        
        low_byte = str(self.memory.get_memory_at_position(byte))
        high_byte = str(self.memory.get_memory_at_position(byte_h))

        address = (high_byte + low_byte)
        self.pc.value = int(address, 16) * 2

    def run(self):
        self.log()
        instruction = self.get_next_byte()

        while instruction:
            # LDA Immediate
            if instruction == 'A9':
                self.handleInstructionLDAImmediate()

            # LDX Immediate
            elif instruction == 'A2':
                self.handleInstructionLDXImmediate()

            # LDY Immediate
            elif instruction == 'A0':
                self.handleInstructionLDYImmediate()

            # STX Zero page
            elif instruction == '86':
                self.handleInstructionSTXZeroPage()

            # STX Zero page Y
            elif instruction == '96':
                self.handleInstructionSTXZeroPageY()

            # STX Absolute
            elif instruction == '8E':
                self.handleInstructionSTXAbsolute()

            # STY Zero page
            elif instruction == '86':
                self.handleInstructionSTYZeroPage()

            # STY Zero page X
            elif instruction == '96':
                self.handleInstructionSTYZeroPageY()

            # STY Absolute
            elif instruction == '8E':
                self.handleInstructionSTYAbsolute()

            # INX
            elif instruction == 'E8':
                self.handleInstructionINX()
            
            # INY
            elif instruction == 'C8':
                self.handleInstructionINY()

            # DEX
            elif instruction == 'CA':
                self.handleInstructionDEX()
            
            # DEY
            elif instruction == '88':
                self.handleInstructionDEY()

            # TAX
            elif instruction == 'AA':
                self.handleInstructionTAX()

            # TXA
            elif instruction == '8A':
                self.handleInstructionTXA()

            # TAY
            elif instruction == 'A8':
                self.handleInstructionTAY()

            # TYA
            elif instruction == '98':
                self.handleInstructionTYA()

            # NOP ( No operation )
            elif instruction == 'EA':
                continue

            # JMP Absolute
            elif instruction == '4C':
                self.handleInstructionJmpAbsolute()
        
            # JMP Indirect
            elif instruction == '6C':
                self.handleInstructionJmpIndirect()
            
            self.log()
            instruction = self.get_next_byte()