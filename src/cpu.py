from utils import log, logls
from ctypes import c_uint16, c_uint8
from memory import Memory

from math import ceil

class CPU:
    def __init__(self, program_name):
        file = open(program_name, "rb")
        self.program_code = file.read().hex()

        self.p = c_uint16(0)
        self.sp = c_uint16(0)
        self.pc = c_uint16(0)
        self.a = c_uint8(0)
        self.x = c_uint8(0)
        self.y = c_uint8(0)
        self.memory = Memory()
    
    def log(self, address = None):
        if (address):
            logls(self.a.value, self.x.value, self.y.value, self.sp.value, ceil(self.pc.value / 2), self.p.value, address, self.memory.get_memory_at_position(address).value)
        else:
            log(self.a.value, self.x.value, self.y.value, self.sp.value, ceil(self.pc.value / 2), self.p.value)

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
    def handleInstructionINCZeroPage(self):
        byte = self.get_next_byte()
        address = int(byte, 16)
        self.memory.set_memory_at_position(address, self.memory.get_memory_at_position(address) + 1)

    def handleInstructionINCZeroPageX(self):
        byte = self.get_next_byte()
        address = format((int(byte, 16) + self.x.value), '04x')

        self.memory.set_memory_at_position(address, self.memory.get_memory_at_position(address) + 1)

    def handleInstructionINCAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)

        self.memory.set_memory_at_position(address, self.memory.get_memory_at_position(address) + 1)

    def handleInstructionINCAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        final_address = format((int(address, 16) + self.x.value), '04x')

        self.memory.set_memory_at_position(address, self.memory.get_memory_at_position(final_address) + 1)

    def handleInstructionINX(self):
        self.x.value = self.x.value + 1

    def handleInstructionINY(self):
        self.y.value = self.y.value + 1

    ## DEC Instructions
    def handleInstructionDECZeroPage(self):
        byte = self.get_next_byte()
        address = int(byte, 16)
        self.memory.set_memory_at_position(address, self.memory.get_memory_at_position(address) - 1)

    def handleInstructionDECZeroPageX(self):
        byte = self.get_next_byte()
        address = format((int(byte, 16) + self.x.value), '04x')

        self.memory.set_memory_at_position(address, self.memory.get_memory_at_position(address) - 1)

    def handleInstructionDECAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)

        self.memory.set_memory_at_position(address, self.memory.get_memory_at_position(address) - 1)

    def handleInstructionDECAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        final_address = format((int(address, 16) + self.x.value), '04x')

        self.memory.set_memory_at_position(address, self.memory.get_memory_at_position(final_address) - 1)

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

    def handleInstructionLDXZeroPage(self):
        byte = self.get_next_byte()
        address = int(byte, 16)
        self.x.value = self.memory.get_memory_at_position(address)

    def handleInstructionLDXZeroPageY(self):
        byte = self.get_next_byte()
        address = format((int(byte, 16) + self.y.value), '04x')
        self.x.value = self.memory.get_memory_at_position(address)

    def handleInstructionLDXAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        self.x.value = self.memory.get_memory_at_position(address)

    def handleInstructionLDXAbsoluteY(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        final_address = format((int(address, 16) + self.y.value), '04x')

        self.x.value = self.memory.get_memory_at_position(final_address)

    def handleInstructionLDYImmediate(self):
        byte = self.get_next_byte()
        immediate = int(byte, 16)
        self.y.value = immediate

    def handleInstructionLDYZeroPage(self):
        byte = self.get_next_byte()
        address = int(byte, 16)
        self.y.value = self.memory.get_memory_at_position(address)

    def handleInstructionLDYZeroPageX(self):
        byte = self.get_next_byte()
        address = format((int(byte, 16) + self.x.value), '04x')
        self.y.value = self.memory.get_memory_at_position(address)

    def handleInstructionLDYAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        self.y.value = self.memory.get_memory_at_position(address)

    def handleInstructionLDYAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        final_address = format((int(address, 16) + self.x.value), '04x')

        self.y.value = self.memory.get_memory_at_position(final_address)

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

            # LDX Zero page
            elif instruction == 'A6':
                self.handleInstructionLDXZeroPage()
                
            # LDX Zero page Y
            elif instruction == 'B6':
                self.handleInstructionLDXZeroPageY()

            # LDX Absolute
            elif instruction == 'AE':
                self.handleInstructionLDXAbsolute()

            # LDX Absolute Y
            elif instruction == 'BE':
                self.handleInstructionLDXAbsoluteY()

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

            # INC Zero page
            elif instruction == 'E6':
                self.handleInstructionINCZeroPage()
            
            # INC Zero page X
            elif instruction == 'F6':
                self.handleInstructionINCZeroPageX()

            # INC Absolut
            elif instruction == 'EE':
                self.handleInstructionINCAbsolute()

            # INC Absolute X
            elif instruction == 'FE':
                self.handleInstructionINCAbsoluteX()
                
            # INX
            elif instruction == 'E8':
                self.handleInstructionINX()
            
            # INY
            elif instruction == 'C8':
                self.handleInstructionINY()

            # DEC Zero page
            elif instruction == 'C6':
                self.handleInstructionINCZeroPage()
            
            # DEC Zero page X
            elif instruction == 'D6':
                self.handleInstructionINCZeroPageX()

            # DEC Absolut
            elif instruction == 'CE':
                self.handleInstructionINCAbsolute()

            # DEC Absolute X
            elif instruction == 'DE':
                self.handleInstructionINCAbsoluteX()

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

            # BRK
            elif instruction == '00':
                continue

            # JMP Absolute
            elif instruction == '4C':
                self.handleInstructionJmpAbsolute()
        
            # JMP Indirect
            elif instruction == '6C':
                self.handleInstructionJmpIndirect()
            
            self.log()
            instruction = self.get_next_byte()