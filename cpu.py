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
        self.pc = 0
        self.memory = Memory()

    def get_next_instruction(self):
        begin = self.pc
        end = self.pc + 2
        byte = self.program_code[begin:end].upper()
        self.pc.value = self.pc.value + 2
        return byte

    def run(self):
        byte = self.get_next_instruction()

        while byte:
            # LDA
            if byte == 'A9':
                print ("instruction: " + byte)

            # LDX
            elif byte == 'A2':
                print ("instruction: " + byte)

            # INX
            elif byte == 'E8':
                print ("instruction: " + byte)
            
            byte = self.get_next_instruction()

            log(self.a.value, self.x.value, self.y.value, self.sp.value, self.pc.value, self.p.value)