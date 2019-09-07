from utils import log, logls
from ctypes import c_uint16, c_uint8
from memory import Memory

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
    
    def log_instruction(self, address = None):
        if (address):
            logls(self.a.value, self.x.value, self.y.value, self.sp.value, self.pc.value, self.p.value, address, self.memory.get_memory_at_position(address).value)
        else:
            log(self.a.value, self.x.value, self.y.value, self.sp.value, self.pc.value, self.p.value)

    def get_next_byte(self):
        begin = self.pc.value
        self.pc.value = self.pc.value + 2
        end = self.pc.value
        byte = self.program_code[begin:end].upper()
        return byte

    ####################################################
    ##########      INSTRUCTION HANDLERS      ##########
    ####################################################

    def handleInstructionINX(self):
        self.x.value = self.x.value + 1
        self.log_instruction()

    def handleInstructionLDAImmediate(self):
        byte = self.get_next_byte()
        immediate = int(byte, 16)
        self.a.value = immediate
        self.log_instruction()

    def handleInstructionLDXImmediate(self):
        byte = self.get_next_byte()
        immediate = int(byte, 16)
        self.x.value = immediate
        self.log_instruction()

    def handleInstructionSTXZeroPage(self):
        byte = self.get_next_byte()
        self.memory.set_memory_at_position(byte, self.x)
        self.log_instruction(byte)

    def run(self):
        instruction = self.get_next_byte()

        while instruction:
            # LDA
            if instruction == 'A9':
                self.handleInstructionLDAImmediate()

            # LDX
            elif instruction == 'A2':
                self.handleInstructionLDXImmediate()

            # INX
            elif instruction == 'E8':
                self.handleInstructionINX()

            # STX Zero page
            elif instruction == '86':
                self.handleInstructionSTXZeroPage()
            
            instruction = self.get_next_byte()