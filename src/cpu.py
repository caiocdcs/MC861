from utils import log, logls
from ctypes import c_uint16, c_uint8
from memory import Memory
from flagController import FlagController
from stack import Stack

KB = 1024

class CPU:

    def __init__(self, program_name):
        file = open(program_name, "rb")
        self.program_code = file.read().hex()

        self.sp = c_uint16(255) # SP starts at 0xff
        self.pc = c_uint16(0)
        self.a = c_uint8(0)
        self.x = c_uint8(0)
        self.y = c_uint8(0)
        self.memory = Memory()
        self.flagController = FlagController()
        self.stack = Stack()

        self._read_header()
        self._load_program()
        self._load_interrupt_vectors()

        if self.prg_rom_size == 1:
            self.rom_initial_pos = 32*KB + 16*KB            # initial rom position
        else:
            self.rom_initial_pos = 32*KB
        self.pc.value = self.rom_initial_pos

        self.address = None

    def _read_header(self):
        self.prg_rom_size = int(self._get_byte_from_code_position(int('8', 16)))
        self.chr_rom_size = int(self._get_byte_from_code_position(int('9', 16)))

    def _load_program(self):
        rom_size = 16*KB*self.prg_rom_size
        initial_rom_pos = 32*KB     # ( 0x8000 ) PRG ROM
        rom_code_initial_pos = 32   # 16 bytes of header
        code_pos = 0
        for i in range(0, rom_size):
            b = self._get_byte_from_code_position(rom_code_initial_pos + code_pos)
            if b != '':
                byte = c_uint8(int(b, 16))
                self.memory.set_memory_at_position_int(initial_rom_pos + i, byte)
                if self.prg_rom_size == 1:
                    self.memory.set_memory_at_position_int(initial_rom_pos + rom_size + i, byte)
            code_pos += 2

    def _load_interrupt_vectors(self):
        low_byte = format(self.memory.get_memory_at_position_str('FFFA').value, '02x') 
        high_byte = format(self.memory.get_memory_at_position_str('FFFB').value, '02x')
        self.nmi = (high_byte + low_byte)

        low_byte = format(self.memory.get_memory_at_position_str('FFFC').value, '02x') 
        high_byte = format(self.memory.get_memory_at_position_str('FFFD').value, '02x')
        self.reset = (high_byte + low_byte)

        low_byte = format(self.memory.get_memory_at_position_str('FFFE').value, '02x') 
        high_byte = format(self.memory.get_memory_at_position_str('FFFF').value, '02x')
        self.irq = (high_byte + low_byte)
    
    def log(self):
        p = self.flagController.getFlagsStatusByte()
        if self.address:
            logls(self.a.value, self.x.value, self.y.value, self.sp.value, self.pc.value, p, self.address,
                  self.memory.get_memory_at_position_str(self.address).value)
        else:
            log(self.a.value, self.x.value, self.y.value, self.sp.value, self.pc.value, p)

    def get_next_byte(self):
        if (self.pc.value < self.rom_initial_pos) or (self.pc.value > (self.rom_initial_pos * self.prg_rom_size * 16*KB)):
            return None
        byte = self.memory.get_memory_at_position_int(self.pc.value)
        self.pc.value = self.pc.value + 1
        return format(byte.value, '02x').upper()

    def _get_byte_from_code_position(self, pos):
        end = pos + 2
        byte = self.program_code[pos:end].upper()
        return byte

    ####################################################
    ##########      INSTRUCTION HANDLERS      ##########
    ####################################################

    ## ADC Instructions
    def handleInstructionAdcImmediate(self):
        byte = self.get_next_byte()
        immediate = int(byte, 16)
        self.adc(immediate)

    def handleInstructionAdcZeroPage(self):
        address = self.get_next_byte()
        value = self.memory.get_memory_at_position_str(address).value
        self.adc(value)

    def handleInstructionAdcZeroPageX(self):
        byte = self.get_next_byte()
        addressStart = int(byte, 16)
        address = (addressStart + self.x.value) & 0xFF
        value = self.memory.get_memory_at_position_int(address).value
        self.adc(value)

    def handleInstructionAdcAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        value = self.memory.get_memory_at_position_str(address).value
        self.adc(value)

    def handleInstructionAdcAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        addressStr = (high_byte + low_byte)
        addressStart = int(addressStr, 16)
        address = (addressStart + self.x.value) & 0xFF
        value = self.memory.get_memory_at_position_int(address).value
        self.adc(value)

    def handleInstructionAdcAbsoluteY(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        addressStr = (high_byte + low_byte)
        addressStart = int(addressStr, 16)
        address = (addressStart + self.y.value) & 0xFF
        value = self.memory.get_memory_at_position_int(address).value
        self.adc(value)

    def handleInstructionAdcIndirectX(self):
        byte = self.get_next_byte()

        address = format((int(byte, 16) + self.x.value), '04x')
        low_byte = format(self.memory.get_memory_at_position_str(address).value, '02x')
        high_byte = format(self.memory.get_memory_at_position_str(format((int(address, 16) + 1), '04x')).value, '02x')

        final_address = (high_byte + low_byte)

        value = self.memory.get_memory_at_position_str(final_address).value
        self.adc(value)

    def handleInstructionAdcIndirectY(self):
        byte = self.get_next_byte()

        l_byte = format(self.memory.get_memory_at_position_str(byte).value, '02x')
        h_byte = format(self.memory.get_memory_at_position_int(int(byte, 16) + 1).value, '02x')

        address = (h_byte + l_byte)
        final_address = int(address, 16) + self.y.value

        value = self.memory.get_memory_at_position_int(final_address).value
        self.adc(value)

    def adc(self, value):
        carry = self.flagController.getCarryFlag()
        aOldValue = self.a.value
        sum = aOldValue + value + carry
        self.a.value = sum & 0xFF                           # set a value limiting to one byte            
         
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag
        self.flagController.setCarryFlagIfNeeded(sum)

        # set overflow flag
        if (aOldValue ^ value) & 0x80 == 0 and (aOldValue ^ self.a.value) & 0x80 != 0:
            self.flagController.setOverflowFlag()
        else:
            self.flagController.clearOverflowFlag()

    ## SBC Instructions
    def handleInstructionSbcImmediate(self):
        byte = self.get_next_byte()
        immediate = int(byte, 16)
        self.sbc(immediate)

    def handleInstructionSbcZeroPage(self):
        address = self.get_next_byte()
        value = self.memory.get_memory_at_position_str(address).value
        self.sbc(value)

    def handleInstructionSbcZeroPageX(self):
        byte = self.get_next_byte()
        addressStart = int(byte, 16)
        address = (addressStart + self.x.value) & 0xFF
        value = self.memory.get_memory_at_position_int(address).value
        self.sbc(value)

    def handleInstructionSbcAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        value = self.memory.get_memory_at_position_str(address).value
        self.sbc(value)

    def handleInstructionSbcAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        addressStr = (high_byte + low_byte)
        addressStart = int(addressStr, 16)
        address = (addressStart + self.x.value) & 0xFF
        value = self.memory.get_memory_at_position_int(address).value
        self.sbc(value)

    def handleInstructionSbcAbsoluteY(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        addressStr = (high_byte + low_byte)
        addressStart = int(addressStr, 16)
        address = (addressStart + self.y.value) & 0xFF
        value = self.memory.get_memory_at_position_int(address).value
        self.sbc(value)

    def handleInstructionSbcIndirectX(self):
        byte = self.get_next_byte()

        address = format((int(byte, 16) + self.x.value), '04x')
        low_byte = format(self.memory.get_memory_at_position_str(address).value, '02x')
        high_byte = format(self.memory.get_memory_at_position_str(format((int(address, 16) + 1), '04x')).value, '02x')

        final_address = (high_byte + low_byte)

        value = self.memory.get_memory_at_position_str(final_address).value
        self.sbc(value)

    def handleInstructionSbcIndirectY(self):
        byte = self.get_next_byte()

        l_byte = format(self.memory.get_memory_at_position_str(byte).value, '02x')
        h_byte = format(self.memory.get_memory_at_position_int(int(byte, 16) + 1).value, '02x')

        address = (h_byte + l_byte)
        final_address = int(address, 16) + self.y.value

        value = self.memory.get_memory_at_position_int(final_address).value
        self.sbc(value)

    def sbc(self, value):
        carry = self.flagController.getCarryFlag()
        aOldValue = self.a.value
        result = aOldValue - value - (1-carry)
        self.a.value = result & 0xFF                          # set a value limiting to one byte            
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag
        self.flagController.setCarryFlagIfNeeded(result)

        # set overflow flag
        if (aOldValue ^ value) & 0x80 == 0 and (aOldValue ^ self.a.value) & 0x80 != 0:
            self.flagController.setOverflowFlag()
        else:
            self.flagController.clearOverflowFlag()
            
    ## AND Instructions

    def handleInstructionAndImmediate(self):
        byte = self.get_next_byte()
        self.a.value = int(byte, 16) & self.a.value
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionAndZeroPage(self):
        address = self.get_next_byte()
        value = self.memory.get_memory_at_position_str(address).value
        self.a.value = value & self.a.value
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionAndZeroPageX(self):
        byte = self.get_next_byte()
        addressStart = int(byte, 16)
        address = (addressStart + self.x.value) & 0xFF
        value = self.memory.get_memory_at_position_int(address).value
        self.a.value = value & self.a.value
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag

    def handleInstructionAndAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        value = self.memory.get_memory_at_position_str(address).value
        self.a.value = value & self.a.value
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionAndAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        addressStr = (high_byte + low_byte)
        addressStart = int(addressStr, 16)
        address = (addressStart + self.x.value) & 0xFF
        value = self.memory.get_memory_at_position_int(address).value
        self.a.value = value & self.a.value
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionAndAbsoluteY(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        addressStr = (high_byte + low_byte)
        addressStart = int(addressStr, 16)
        address = (addressStart + self.y.value) & 0xFF
        value = self.memory.get_memory_at_position_int(address).value
        self.a.value = value & self.a.value
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionAndIndirectX(self):
        byte = self.get_next_byte()

        address = format((int(byte, 16) + self.x.value), '04x')
        low_byte = format(self.memory.get_memory_at_position_str(address).value, '02x')
        high_byte = format(self.memory.get_memory_at_position_str(format((int(address, 16) + 1), '04x')).value, '02x')

        final_address = (high_byte + low_byte)

        value = self.memory.get_memory_at_position_str(final_address).value
        self.a.value = value & self.a.value
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionAndIndirectY(self):
        byte = self.get_next_byte()

        l_byte = format(self.memory.get_memory_at_position_str(byte).value, '02x')
        h_byte = format(self.memory.get_memory_at_position_int(int(byte, 16) + 1).value, '02x')

        address = (h_byte + l_byte)
        final_address = int(address, 16) + self.y.value

        value = self.memory.get_memory_at_position_int(final_address).value
        self.a.value = value & self.a.value
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    ## ORA Instructions
    def handleInstructionORAImmediate(self):
        byte = self.get_next_byte()
        self.a.value = int(byte, 16) | self.a.value
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionORAZeroPage(self):
        address = self.get_next_byte()
        value = self.memory.get_memory_at_position_str(address).value
        self.a.value = value | self.a.value
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionORAZeroPageX(self):
        byte = self.get_next_byte()
        addressStart = int(byte, 16)
        address = (addressStart + self.x.value) & 0xFF
        value = self.memory.get_memory_at_position_int(address).value
        self.a.value = value | self.a.value
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionORAAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        value = self.memory.get_memory_at_position_str(address).value
        self.a.value = value | self.a.value
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionORAAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        addressStr = (high_byte + low_byte)
        addressStart = int(addressStr, 16)
        address = (addressStart + self.x.value) & 0xFF
        value = self.memory.get_memory_at_position_int(address).value
        self.a.value = value | self.a.value
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionORAAbsoluteY(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        addressStr = (high_byte + low_byte)
        addressStart = int(addressStr, 16)
        address = (addressStart + self.y.value) & 0xFF
        value = self.memory.get_memory_at_position_int(address).value
        self.a.value = value | self.a.value
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionORAIndirectX(self):
        byte = self.get_next_byte()

        address = format((int(byte, 16) + self.x.value), '04x')
        low_byte = format(self.memory.get_memory_at_position_str(address).value, '02x')
        high_byte = format(self.memory.get_memory_at_position_str(format((int(address, 16) + 1), '04x')).value, '02x')

        final_address = (high_byte + low_byte)

        value = self.memory.get_memory_at_position_str(final_address).value
        self.a.value = value | self.a.value
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionORAIndirectY(self):
        byte = self.get_next_byte()

        l_byte = format(self.memory.get_memory_at_position_str(byte).value, '02x')
        h_byte = format(self.memory.get_memory_at_position_int(int(byte, 16) + 1).value, '02x')

        address = (h_byte + l_byte)
        final_address = int(address, 16) + self.y.value

        value = self.memory.get_memory_at_position_int(final_address).value
        self.a.value = value | self.a.value
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    ## EOR Instructions
    def handleInstructionEORImmediate(self):
        byte = self.get_next_byte()
        self.a.value = int(byte, 16) ^ self.a.value
        self.x.value = 9
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionEORZeroPage(self):
        address = self.get_next_byte()
        value = self.memory.get_memory_at_position_str(address).value
        self.a.value = value ^ self.a.value
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionEORZeroPageX(self):
        byte = self.get_next_byte()
        addressStart = int(byte, 16)
        address = (addressStart + self.x.value) & 0xFF
        value = self.memory.get_memory_at_position_int(address).value
        self.a.value = value ^ self.a.value
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionEORAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        value = self.memory.get_memory_at_position_str(address).value
        self.a.value = value ^ self.a.value
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionEORAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        addressStr = (high_byte + low_byte)
        addressStart = int(addressStr, 16)
        address = (addressStart + self.x.value) & 0xFF
        value = self.memory.get_memory_at_position_int(address).value
        self.a.value = value ^ self.a.value
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionEORAbsoluteY(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        addressStr = (high_byte + low_byte)
        addressStart = int(addressStr, 16)
        address = (addressStart + self.y.value) & 0xFF
        value = self.memory.get_memory_at_position_int(address).value
        self.a.value = value ^ self.a.value
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionEORIndirectX(self):
        byte = self.get_next_byte()

        address = format((int(byte, 16) + self.x.value), '04x')
        low_byte = format(self.memory.get_memory_at_position_str(address).value, '02x')
        high_byte = format(self.memory.get_memory_at_position_str(format((int(address, 16) + 1), '04x')).value, '02x')

        final_address = (high_byte + low_byte)

        value = self.memory.get_memory_at_position_str(final_address).value
        self.a.value = value ^ self.a.value
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionEORIndirectY(self):
        byte = self.get_next_byte()

        l_byte = format(self.memory.get_memory_at_position_str(byte).value, '02x')
        h_byte = format(self.memory.get_memory_at_position_int(int(byte, 16) + 1).value, '02x')

        address = (h_byte + l_byte)
        final_address = int(address, 16) + self.y.value

        value = self.memory.get_memory_at_position_int(final_address).value
        self.a.value = value ^ self.a.value
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    ## INC Instructions
    def handleInstructionINCZeroPage(self):
        byte = self.get_next_byte()
        self.address = byte.zfill(4)

        value = self.memory.get_memory_at_position_str(self.address).value + 1

        self.memory.set_memory_at_position_str(self.address, c_uint8(value))
        self.flagController.setNegativeIfNeeded(value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(value) # set zero flag

    def handleInstructionINCZeroPageX(self):
        byte = self.get_next_byte()
        self.address = format((int(byte, 16) + self.x.value), '04x')

        value = self.memory.get_memory_at_position_str(self.address).value + 1

        self.memory.set_memory_at_position_str(self.address, c_uint8(value))
        self.flagController.setNegativeIfNeeded(value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(value) # set zero flag

    def handleInstructionINCAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        self.address = (high_byte + low_byte)
        value = self.memory.get_memory_at_position_str(self.address).value + 1

        self.memory.set_memory_at_position_str(self.address, c_uint8(value))
        self.flagController.setNegativeIfNeeded(value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(value) # set zero flag

    def handleInstructionINCAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        lookup_address = (high_byte + low_byte)
        self.address = format((int(lookup_address, 16) + self.x.value), '04x')

        value = self.memory.get_memory_at_position_str(self.address).value + 1

        self.memory.set_memory_at_position_str(self.address, c_uint8(value))
        self.flagController.setNegativeIfNeeded(value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(value) # set zero flag

    def handleInstructionINX(self):
        self.x.value = self.x.value + 1
        self.flagController.setNegativeIfNeeded(self.x.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.x.value) # set zero flag

    def handleInstructionINY(self):
        self.y.value = self.y.value + 1
        self.flagController.setNegativeIfNeeded(self.y.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.y.value) # set zero flag

    ## DEC Instructions
    def handleInstructionDECZeroPage(self):
        byte = self.get_next_byte()
        self.address = byte.zfill(4)
        value = self.memory.get_memory_at_position_str(self.address).value - 1

        self.memory.set_memory_at_position_str(self.address, c_uint8(value))
        self.flagController.setNegativeIfNeeded(value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(value) # set zero flag

    def handleInstructionDECZeroPageX(self):
        byte = self.get_next_byte()
        self.address = format((int(byte, 16) + self.x.value), '04x')

        value = self.memory.get_memory_at_position_str(self.address).value - 1

        self.memory.set_memory_at_position_str(self.address, c_uint8(value))
        self.flagController.setNegativeIfNeeded(value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(value) # set zero flag

    def handleInstructionDECAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        self.address = (high_byte + low_byte)

        value = self.memory.get_memory_at_position_str(self.address).value - 1

        self.memory.set_memory_at_position_str(self.address, c_uint8(value))
        self.flagController.setNegativeIfNeeded(value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(value) # set zero flag

    def handleInstructionDECAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        lookup_address = (high_byte + low_byte)
        self.address = format((int(lookup_address, 16) + self.x.value), '04x')

        value = self.memory.get_memory_at_position_str(self.address).value - 1

        self.memory.set_memory_at_position_str(self.address, c_uint8(value))
        self.flagController.setNegativeIfNeeded(value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(value) # set zero flag

    def handleInstructionDEX(self):
        self.x.value = self.x.value - 1
        self.flagController.setNegativeIfNeeded(self.x.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.x.value) # set zero flag

    def handleInstructionDEY(self):
        self.y.value = self.y.value - 1
        self.flagController.setNegativeIfNeeded(self.y.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.y.value) # set zero flag


    ## Transfer Instructions
    def handleInstructionTAX(self):
        self.x.value = self.a.value
        self.flagController.setNegativeIfNeeded(self.x.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.x.value) # set zero flag

    def handleInstructionTXA(self):
        self.a.value = self.x.value
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionTAY(self):
        self.y.value = self.a.value
        self.flagController.setNegativeIfNeeded(self.y.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.y.value) # set zero flag

    def handleInstructionTYA(self):
        self.a.value = self.y.value
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    ## ASL Instructions
    def handleInstructionASLAccumulator(self):
        carry = 1 if (0b10000000 & self.a.value) else 0
        self.a.value = self.a.value << 1
        
        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionASLZeroPage(self):
        address = self.get_next_byte()
        mem = self.memory.get_memory_at_position_str(address)
        carry = 1 if (0b10000000 & mem.value) else 0
        self.memory.set_memory_at_position_str(address, c_uint8(mem.value << 1))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem.value << 1) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem.value << 1) # set zero flag

    def handleInstructionASLZeroPageX(self):
        byte = self.get_next_byte()
        address = format((int(byte, 16) + self.x.value), '04x')
        mem = self.memory.get_memory_at_position_str(address)
        carry = 1 if (0b10000000 & mem.value) else 0
        self.memory.set_memory_at_position_str(address, c_uint8(mem.value << 1))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem.value << 1) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem.value << 1) # set zero flag

    def handleInstructionASLAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        mem = self.memory.get_memory_at_position_str(address)
        carry = 1 if (0b10000000 & mem.value) else 0
        self.memory.set_memory_at_position_str(address, c_uint8(mem.value << 1))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem.value << 1) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem.value << 1) # set zero flag

    def handleInstructionASLAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        final_address = format((int(address, 16) + self.x.value), '04x')

        mem = self.memory.get_memory_at_position_str(final_address)
        carry = 1 if (0b10000000 & mem.value) else 0
        self.memory.set_memory_at_position_str(final_address, c_uint8(mem.value << 1))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem.value << 1) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem.value << 1) # set zero flag

    ## LSR Instructions
    def handleInstructionLSRAccumulator(self):
        carry = 1 if (0b00000001 & self.a.value) else 0
        self.a.value = self.a.value >> 1
        
        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionLSRZeroPage(self):
        address = self.get_next_byte()
        mem = self.memory.get_memory_at_position_str(address)
        carry = 1 if (0b00000001 & mem.value) else 0
        self.memory.set_memory_at_position_str(address, c_uint8(mem.value >> 1))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem.value >> 1) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem.value >> 1) # set zero flag

    def handleInstructionLSRZeroPageX(self):
        byte = self.get_next_byte()
        address = format((int(byte, 16) + self.x.value), '04x')
        mem = self.memory.get_memory_at_position_str(address)
        carry = 1 if (0b00000001 & mem.value) else 0
        self.memory.set_memory_at_position_str(address, c_uint8(mem.value >> 1))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem.value >> 1) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem.value >> 1) # set zero flag

    def handleInstructionLSRAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        mem = self.memory.get_memory_at_position_str(address)
        carry = 1 if (0b00000001 & mem.value) else 0
        self.memory.set_memory_at_position_str(address, c_uint8(mem.value >> 1))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem.value >> 1) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem.value >> 1) # set zero flag

    def handleInstructionLSRAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        final_address = format((int(address, 16) + self.x.value), '04x')

        mem = self.memory.get_memory_at_position_str(final_address)
        carry = 1 if (0b00000001 & mem.value) else 0
        self.memory.set_memory_at_position_str(final_address, c_uint8(mem.value >> 1))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem.value >> 1) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem.value >> 1) # set zero flag

    ## BIT test BITs
    def handleInstructionBITZeroPage(self):
        address = self.get_next_byte()
        mem = self.memory.get_memory_at_position_str(address)
        self.flagController.setZeroFlagIfNeeded(self.a.value & mem.value) # set zero flag

        neg = 1 if (0b10000000 & mem.value) else 0
        ovf = 1 if (0b01000000 & mem.value) else 0

        self.flagController.setNegativeFlag() if ovf else self.flagController.clearNegativeFlag()
        self.flagController.setOverflowFlag() if ovf else self.flagController.clearOverflowFlag()

    def handleInstructionBITAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        mem = self.memory.get_memory_at_position_str(address)
        self.flagController.setZeroFlagIfNeeded(self.a.value & mem.value) # set zero flag

        neg = 1 if (0b10000000 & mem.value) else 0
        ovf = 1 if (0b01000000 & mem.value) else 0

        self.flagController.setNegativeFlag() if ovf else self.flagController.clearNegativeFlag()
        self.flagController.setOverflowFlag() if ovf else self.flagController.clearOverflowFlag()

    ## ROL Instructions
    def handleInstructionROLAccumulator(self):
        carry = 1 if (0b10000000 & self.a.value) else 0
        c = self.flagController.getCarryFlag()
        self.a.value = self.a.value << 1 | c
        
        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionROLZeroPage(self):
        address = self.get_next_byte()
        mem = self.memory.get_memory_at_position_str(address)
        carry = 1 if (0b10000000 & mem.value) else 0
        c = self.flagController.getCarryFlag()
        self.memory.set_memory_at_position_str(address, c_uint8(mem.value << 1 | c))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem.value << 1 | c) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem.value << 1 | c) # set zero flag

    def handleInstructionROLZeroPageX(self):
        byte = self.get_next_byte()
        address = format((int(byte, 16) + self.x.value), '04x')
        mem = self.memory.get_memory_at_position_str(address)
        carry = 1 if (0b10000000 & mem.value) else 0
        c = self.flagController.getCarryFlag()
        self.memory.set_memory_at_position_str(address, c_uint8(mem.value << 1 | c))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem.value << 1 | c) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem.value << 1 | c) # set zero flag

    def handleInstructionROLAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        mem = self.memory.get_memory_at_position_str(address)
        carry = 1 if (0b10000000 & mem.value) else 0
        c = self.flagController.getCarryFlag()
        self.memory.set_memory_at_position_str(address, c_uint8(mem.value << 1 | c))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem.value << 1 | c) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem.value << 1 | c) # set zero flag

    def handleInstructionROLAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        final_address = format((int(address, 16) + self.x.value), '04x')

        mem = self.memory.get_memory_at_position_str(final_address)
        carry = 1 if (0b10000000 & mem.value) else 0
        c = self.flagController.getCarryFlag()
        self.memory.set_memory_at_position_str(final_address, c_uint8(mem.value << 1 | c))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem.value << 1 | c) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem.value << 1 | c) # set zero flag

    ## ROR Instructions
    def handleInstructionRORAccumulator(self):
        carry = 1 if (0b00000001 & self.a.value) else 0
        c = self.flagController.getCarryFlag()
        self.a.value = self.a.value >> 1 | c * 128
        
        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionRORZeroPage(self):
        address = self.get_next_byte()
        mem = self.memory.get_memory_at_position_str(address)
        carry = 1 if (0b00000001 & mem.value) else 0
        c = self.flagController.getCarryFlag()
        self.memory.set_memory_at_position_str(address, c_uint8(mem.value >> 1 | c * 128))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem.value >> 1 | c * 128) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem.value >> 1 | c * 128) # set zero flag

    def handleInstructionRORZeroPageX(self):
        byte = self.get_next_byte()
        address = format((int(byte, 16) + self.x.value), '04x')
        mem = self.memory.get_memory_at_position_str(address)
        carry = 1 if (0b00000001 & mem.value) else 0
        c = self.flagController.getCarryFlag()
        self.memory.set_memory_at_position_str(address, c_uint8(mem.value >> 1 | c * 128))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem.value >> 1 | c * 128) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem.value >> 1 | c * 128) # set zero flag

    def handleInstructionRORAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        mem = self.memory.get_memory_at_position_str(address)
        carry = 1 if (0b00000001 & mem.value) else 0
        c = self.flagController.getCarryFlag()
        self.memory.set_memory_at_position_str(address, c_uint8(mem.value >> 1 | c * 128))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem.value >> 1 | c * 128) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem.value >> 1 | c * 128) # set zero flag

    def handleInstructionRORAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        final_address = format((int(address, 16) + self.x.value), '04x')

        mem = self.memory.get_memory_at_position_str(final_address)
        carry = 1 if (0b00000001 & mem.value) else 0
        c = self.flagController.getCarryFlag()
        self.memory.set_memory_at_position_str(final_address, c_uint8(mem.value >> 1 | c * 128))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem.value >> 1 | c * 128) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem.value >> 1 | c * 128) # set zero flag

    ## CMP Instructions
    def handleInstructionCMPImmediate(self):
        byte = self.get_next_byte()
        immediate = int(byte, 16)
        self.compare(immediate)

    def handleInstructionCMPZeroPage(self):
        address = self.get_next_byte()
        value = self.memory.get_memory_at_position_str(address).value
        self.compare(value)

    def handleInstructionCMPZeroPageX(self):
        byte = self.get_next_byte()
        addressStart = int(byte, 16)
        address = (addressStart + self.x.value) & 0xFF
        value = self.memory.get_memory_at_position_int(address).value
        self.compare(value)

    def handleInstructionCMPAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        value = self.memory.get_memory_at_position_str(address).value
        self.compare(value)

    def handleInstructionCMPAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        final_address = format((int(address, 16) + self.x.value), '04x')

        mem = self.memory.get_memory_at_position_str(final_address)
        self.compare(mem.value)

    def handleInstructionCMPAbsoluteY(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        final_address = format((int(address, 16) + self.y.value), '04x')
        
        mem = self.memory.get_memory_at_position_str(final_address)
        self.compare(mem.value)

    def handleInstructionCMPIndirectX(self):
        byte = self.get_next_byte()

        address = format((int(byte, 16) + self.x.value), '04x')
        low_byte = format(self.memory.get_memory_at_position_str(address).value, '02x')
        high_byte = format(self.memory.get_memory_at_position_str(format((int(address, 16) + 1), '04x')).value, '02x')

        final_address = (high_byte + low_byte)

        value = self.memory.get_memory_at_position_str(final_address).value
        self.compare(value)

    def handleInstructionCMPIndirectY(self):
        byte = self.get_next_byte()

        l_byte = format(self.memory.get_memory_at_position_str(byte).value, '02x')
        h_byte = format(self.memory.get_memory_at_position_int(int(byte, 16) + 1).value, '02x')

        address = (h_byte + l_byte)
        final_address = int(address, 16) + self.y.value

        value = self.memory.get_memory_at_position_int(final_address).value
        self.compare(value)

    def compare(self, value):
        self.flagController.clearCarryFlag()
        result = self.a.value - value
        res = result & 0xFF                          # set a value limiting to one byte            
        self.flagController.setNegativeIfNeeded(res) # set negative flag
        self.flagController.setZeroFlagIfNeeded(res) # set zero flag
        if result >= 0:
            self.flagController.setCarryFlag()

    def handleInstructionCPXImmediate(self):
        byte = self.get_next_byte()
        immediate = int(byte, 16)
        self.compareX(immediate)

    def handleInstructionCPXZeroPage(self):
        address = self.get_next_byte()
        value = self.memory.get_memory_at_position_str(address).value
        self.compareX(value)

    def handleInstructionCPXAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        value = self.memory.get_memory_at_position_str(address).value
        self.compareX(value)

    def compareX(self, value):
        self.flagController.clearCarryFlag()
        result = self.x.value - value
        res = result & 0xFF                          # set a value limiting to one byte            
        self.flagController.setNegativeIfNeeded(res) # set negative flag
        self.flagController.setZeroFlagIfNeeded(res) # set zero flag
        if result >= 0:
            self.flagController.setCarryFlag()

    def handleInstructionCPYImmediate(self):
        byte = self.get_next_byte()
        immediate = int(byte, 16)
        self.compareY(immediate)

    def handleInstructionCPYZeroPage(self):
        address = self.get_next_byte()
        value = self.memory.get_memory_at_position_str(address).value
        self.compareY(value)

    def handleInstructionCPYAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        value = self.memory.get_memory_at_position_str(address).value
        self.compareY(value)

    def compareY(self, value):
        self.flagController.clearCarryFlag()
        result = self.y.value - value
        res = result & 0xFF                          # set a value limiting to one byte            
        self.flagController.setNegativeIfNeeded(res) # set negative flag
        self.flagController.setZeroFlagIfNeeded(res) # set zero flag
        if result >= 0:
            self.flagController.setCarryFlag()

    ## Load Instructions
    def handleInstructionLDAImmediate(self):
        byte = self.get_next_byte()
        immediate = int(byte, 16)
        self.a.value = immediate
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionLDAZeroPage(self):
        address = self.get_next_byte()
        self.a = self.memory.get_memory_at_position_str(address)

        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionLDAZeroPageX(self):
        byte = self.get_next_byte()
        address = format((int(byte, 16) + self.x.value), '04x')
        self.a = self.memory.get_memory_at_position_str(address)

        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionLDAAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        self.a = self.memory.get_memory_at_position_str(address)

        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionLDAAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        final_address = format((int(address, 16) + self.x.value), '04x')

        self.a = self.memory.get_memory_at_position_str(final_address)

        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionLDAAbsoluteY(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        final_address = format((int(address, 16) + self.y.value), '04x')

        self.a = self.memory.get_memory_at_position_str(final_address)

        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionLDAIndirectX(self):
        byte = self.get_next_byte()

        address = format((int(byte, 16) + self.x.value), '04x')
        low_byte = format(self.memory.get_memory_at_position_str(address).value, '02x')
        high_byte = format(self.memory.get_memory_at_position_str(format((int(address, 16) + 1), '04x')).value, '02x')

        final_address = (high_byte + low_byte)

        self.a = self.memory.get_memory_at_position_str(final_address)

        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionLDAIndirectY(self):
        byte = self.get_next_byte()

        l_byte = format(self.memory.get_memory_at_position_str(byte).value, '02x')
        h_byte = format(self.memory.get_memory_at_position_int(int(byte, 16) + 1).value, '02x')

        address = (h_byte + l_byte)
        final_address = int(address, 16) + self.y.value

        self.a = self.memory.get_memory_at_position_int(final_address)

        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    def handleInstructionLDXImmediate(self):
        byte = self.get_next_byte()
        immediate = int(byte, 16)
        self.x.value = immediate
        self.flagController.setNegativeIfNeeded(self.x.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.x.value) # set zero flag

    def handleInstructionLDXZeroPage(self):
        address = self.get_next_byte()
        self.x = self.memory.get_memory_at_position_str(address)

        self.flagController.setNegativeIfNeeded(self.x.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.x.value) # set zero flag

    def handleInstructionLDXZeroPageY(self):
        byte = self.get_next_byte()
        address = format((int(byte, 16) + self.y.value), '04x')
        self.x = self.memory.get_memory_at_position_str(address)

        self.flagController.setNegativeIfNeeded(self.x.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.x.value) # set zero flag

    def handleInstructionLDXAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        self.x = self.memory.get_memory_at_position_str(address)

        self.flagController.setNegativeIfNeeded(self.x.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.x.value) # set zero flag

    def handleInstructionLDXAbsoluteY(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        final_address = format((int(address, 16) + self.y.value), '04x')

        self.x = self.memory.get_memory_at_position_str(final_address)

        self.flagController.setNegativeIfNeeded(self.x.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.x.value) # set zero flag

    def handleInstructionLDYImmediate(self):
        byte = self.get_next_byte()
        immediate = int(byte, 16)
        self.y.value = immediate
        self.flagController.setNegativeIfNeeded(self.y.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.y.value) # set zero flag

    def handleInstructionLDYZeroPage(self):
        address = self.get_next_byte()
        self.y = self.memory.get_memory_at_position_str(address)
        
        self.flagController.setNegativeIfNeeded(self.y.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.y.value) # set zero flag

    def handleInstructionLDYZeroPageX(self):
        byte = self.get_next_byte()
        address = format((int(byte, 16) + self.x.value), '04x')
        self.y = self.memory.get_memory_at_position_str(address)

        self.flagController.setNegativeIfNeeded(self.y.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.y.value) # set zero flag

    def handleInstructionLDYAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        self.y = self.memory.get_memory_at_position_str(address)

        self.flagController.setNegativeIfNeeded(self.y.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.y.value) # set zero flag

    def handleInstructionLDYAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        final_address = format((int(address, 16) + self.x.value), '04x')

        self.y = self.memory.get_memory_at_position_str(final_address)

        self.flagController.setNegativeIfNeeded(self.y.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.y.value) # set zero flag

    ## Store Instructions
    def handleInstructionSTXZeroPage(self):
        byte = self.get_next_byte()

        self.address = byte.zfill(4)
        self.memory.set_memory_at_position_str(self.address, self.x)

    def handleInstructionSTXZeroPageY(self):
        byte = self.get_next_byte()

        self.address = format((int(byte, 16) + self.y.value), '04x')
        self.memory.set_memory_at_position_str(self.address, self.x)

    def handleInstructionSTXAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        self.address = (high_byte + low_byte)

        self.memory.set_memory_at_position_str(self.address, self.x)

    def handleInstructionSTYZeroPage(self):
        byte = self.get_next_byte()

        self.address = byte.zfill(4)
        self.memory.set_memory_at_position_str(self.address, self.y)

    def handleInstructionSTYZeroPageX(self):
        byte = self.get_next_byte()

        self.address = format((int(byte, 16) + self.x.value), '04x')
        self.memory.set_memory_at_position_str(self.address, self.y)

    def handleInstructionSTYAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        self.address = (high_byte + low_byte)

        self.memory.set_memory_at_position_str(self.address, self.y)

    def handleInstructionSTAZeroPage(self):
        byte = self.get_next_byte()

        self.address = byte.zfill(4)
        self.memory.set_memory_at_position_str(self.address, self.a)

    def handleInstructionSTAZeroPageX(self):
        byte = self.get_next_byte()

        self.address = format((int(byte, 16) + self.x.value), '04x')
        self.memory.set_memory_at_position_str(self.address, self.a)

    def handleInstructionSTAAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        self.address = (high_byte + low_byte)

        self.memory.set_memory_at_position_str(self.address, self.a)

    def handleInstructionSTAAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        self.address = format((int(address, 16) + self.x.value), '04x')

        self.memory.set_memory_at_position_str(self.address, self.a)

    def handleInstructionSTAAbsoluteY(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        self.address = format((int(address, 16) + self.y.value), '04x')

        self.memory.set_memory_at_position_str(self.address, self.a)

    def handleInstructionSTAIndirectX(self):
        byte = self.get_next_byte()

        address = format((int(byte, 16) + self.x.value), '04x')
        low_byte = format(self.memory.get_memory_at_position_str(address).value, '02x')
        high_byte = format(self.memory.get_memory_at_position_str(format((int(address, 16) + 1), '04x')).value, '02x')

        self.address = (high_byte + low_byte)

        self.memory.set_memory_at_position_str(self.address, self.a)

    def handleInstructionSTAIndirectY(self):
        byte = self.get_next_byte()

        l_byte = format(self.memory.get_memory_at_position_str(byte).value, '02x')
        h_byte = format(self.memory.get_memory_at_position_int(int(byte, 16) + 1).value, '02x')

        lookup_address = (h_byte + l_byte)
        self.address = format(int(lookup_address, 16) + self.y.value, '04x')

        self.memory.set_memory_at_position_str(self.address, self.a)

    ## Jump Instructions
    def handleInstructionJmpAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)

        self.pc.value = int(address, 16)

    def handleInstructionJmpIndirect(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        l_byte = format(self.memory.get_memory_at_position_str(address).value, '02x')
        h_byte = format(self.memory.get_memory_at_position_int(int(address, 16) + 1).value, '02x')
        final_address = (h_byte + l_byte)

        self.pc.value = int(final_address, 16)

    # Clear flags instructions
    def handleInstructionClearCarryFlag(self):
        self.flagController.clearCarryFlag()

    def handleInstructionClearDecimalMode(self):
        self.flagController.clearDecimalFlag()

    def handleInstructionClearInterruptDisable(self):
        self.flagController.clearInterrupDisabledtFlag()
    
    def handleInstructionClearOverflowFlag(self):
        self.flagController.clearOverflowFlag()

    # Set flags instructions
    def handleInstructionSetCarryFlag(self):
        self.flagController.setCarryFlag()

    def handleInstructionSetDecimalMode(self):
        self.flagController.setDecimalFlag()

    def handleInstructionSetInterruptDisable(self):
        self.flagController.setInterrupDisabledtFlag()
        
    # Stack instructions
    def handleInstructionTXS(self):
        self.sp.value = self.x.value
        self.flagController.setNegativeIfNeeded(self.sp.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.sp.value) # set zero flag

    def handleInstructionSTX(self):
        self.x.value = self.sp.value
        self.flagController.setNegativeIfNeeded(self.x.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.x.value) # set zero flag

    def handleInstructionPHA(self):
        stackAddress = self.stack.getAddress() + (self.sp.value * 8)
        self.memory.set_memory_at_position_int(stackAddress, self.a.value)
        self.sp.value = self.sp.value - 1

    def handleInstructionPLA(self):
        self.sp.value = self.sp.value + 1
        stackAddress = self.stack.getAddress() + (self.sp.value * 8)
        self.a.value = self.memory.get_memory_at_position_int(stackAddress)

    def handleInstructionPHP(self):
        P = self.flagController.getFlagsStatusByte()
        stackAddress = self.stack.getAddress() + (self.sp.value * 8)
        self.memory.set_memory_at_position_int(stackAddress, P)
        self.sp.value = self.sp.value - 1

    def handleInstructionPLP(self):
        self.sp.value = self.sp.value + 1
        stackAddress = self.stack.getAddress() + (self.sp.value * 8)
        P = self.memory.get_memory_at_position_int(stackAddress)
        self.flagController.setFlagsStatusByte(P)

    # RTI Return from Interrupt
    def handleInstructionRTI(self):
        # Process Status World (flags)
        self.sp.value = self.sp.value + 1
        stackAddress = self.stack.getAddress() + (self.sp.value * 8)
        P = self.memory.get_memory_at_position_int(stackAddress)
        self.flagController.setFlagsStatusByte(P)
        # PC
        self.sp.value = self.sp.value + 1
        stackAddress = self.stack.getAddress() + (self.sp.value * 8)
        self.pc.value = self.memory.get_memory_at_position_int(stackAddress)

    # Subroutine Instructions
    def handleInstructionJSR(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)

        pc_l = format(self.pc.value, '04x')[0:2]
        pc_h = format(self.pc.value, '04x')[2:4]

        self.pc.value = int(address, 16)

        # set high byte
        stackAddress = self.stack.getAddress() + (self.sp.value * 8)
        self.memory.set_memory_at_position_int(stackAddress, c_uint8(int(pc_h, 16)))
        self.sp.value = self.sp.value - 1

        # set low byte
        stackAddress = self.stack.getAddress() + (self.sp.value * 8)
        self.memory.set_memory_at_position_int(stackAddress, c_uint8(int(pc_l, 16)))
        self.sp.value = self.sp.value - 1

    def handleInstructionRTS(self):
        # get high byte
        self.sp.value = self.sp.value + 1
        stackAddress = self.stack.getAddress() + (self.sp.value * 8)
        low_byte = format(self.memory.get_memory_at_position_int(stackAddress).value, '02x')

        # get low byte
        self.sp.value = self.sp.value + 1
        stackAddress = self.stack.getAddress() + (self.sp.value * 8)
        high_byte = format(self.memory.get_memory_at_position_int(stackAddress).value, '02x')

        address = (low_byte + high_byte)
        self.pc.value = int(address, 16) + 1
        

    def run(self):
        instruction = self.get_next_byte()

        while instruction:

            # ASL Accumulator
            if instruction == '0A':
                self.handleInstructionASLAccumulator()

            # ASL Zero Page
            if instruction == '06':
                self.handleInstructionASLZeroPage()

            # ASL Zero Page X
            if instruction == '16':
                self.handleInstructionASLZeroPageX()

            # ASL Absolute
            if instruction == '0E':
                self.handleInstructionASLAbsolute()

            # ASL Absolute X
            if instruction == '1E':
                self.handleInstructionASLAbsoluteX()

            # LSR Accumulator
            if instruction == '4A':
                self.handleInstructionLSRAccumulator()

            # LSR Zero Page
            if instruction == '46':
                self.handleInstructionLSRZeroPage()

            # LSR Zero Page X
            if instruction == '56':
                self.handleInstructionLSRZeroPageX()

            # LSR Absolute
            if instruction == '4E':
                self.handleInstructionLSRAbsolute()

            # LSR Absolute X
            if instruction == '5E':
                self.handleInstructionLSRAbsoluteX()

            # ROL Accumulator
            if instruction == '2A':
                self.handleInstructionROLAccumulator()

            # ROL Zero Page
            if instruction == '26':
                self.handleInstructionROLZeroPage()

            # ROL Zero Page X
            if instruction == '36':
                self.handleInstructionROLZeroPageX()

            # ROL Absolute
            if instruction == '2E':
                self.handleInstructionROLAbsolute()

            # ROL Absolute X
            if instruction == '3E':
                self.handleInstructionROLAbsoluteX()

            # ROR Accumulator
            if instruction == '6A':
                self.handleInstructionRORAccumulator()

            # ROR Zero Page
            if instruction == '66':
                self.handleInstructionRORZeroPage()

            # ROR Zero Page X
            if instruction == '76':
                self.handleInstructionRORZeroPageX()

            # ROR Absolute
            if instruction == '6E':
                self.handleInstructionRORAbsolute()

            # ROR Absolute X
            if instruction == '7E':
                self.handleInstructionRORAbsoluteX()

            # BIT Zero Page
            if instruction == '24':
                self.handleInstructionBITZeroPage()

            # BIT Absolute
            if instruction == '2C':
                self.handleInstructionBITAbsolute()

            # CMP Immediate
            elif instruction == 'C9':
                self.handleInstructionCMPImmediate()

            # CMP Zero Page
            elif instruction == 'C5':
                self.handleInstructionCMPZeroPage()

            # CMP Zero Page X
            elif instruction == 'D5':
                self.handleInstructionCMPZeroPageX()

            # CMP Absolute
            elif instruction == 'CD':
                self.handleInstructionCMPAbsolute()

            # CMP Absolute X
            elif instruction == 'DD':
                self.handleInstructionCMPAbsoluteX()

            # CMP Absolute Y
            elif instruction == 'D9':
                self.handleInstructionCMPAbsoluteY()

            # CMP Indirect X
            elif instruction == 'C1':
                self.handleInstructionCMPIndirectX()

            # CMP Indirect Y
            elif instruction == 'D1':
                self.handleInstructionCMPIndirectY()

            # CPX Immediate
            elif instruction == 'E0':
                self.handleInstructionCPXImmediate()

            # CPX Zero Page
            elif instruction == 'E4':
                self.handleInstructionCPXZeroPage()

            # CPX Absolute
            elif instruction == 'EC':
                self.handleInstructionCPXAbsolute()

            # CPY Immediate
            elif instruction == 'C0':
                self.handleInstructionCPYImmediate()

            # CPY Zero Page
            elif instruction == 'C4':
                self.handleInstructionCPYZeroPage()

            # CPY Absolute
            elif instruction == 'CC':
                self.handleInstructionCPYAbsolute()

            # LDA Immediate
            if instruction == 'A9':
                self.handleInstructionLDAImmediate()

            # LDA Zero Page
            if instruction == 'A5':
                self.handleInstructionLDAZeroPage()

            # LDA Zero Page X
            if instruction == 'B5':
                self.handleInstructionLDAZeroPageX()

            # LDA Absolute
            if instruction == 'AD':
                self.handleInstructionLDAAbsolute()

            # LDA Absolute X
            if instruction == 'BD':
                self.handleInstructionLDAAbsoluteX()

            # LDA Absolute Y
            if instruction == 'B9':
                self.handleInstructionLDAAbsoluteY()

            # LDA Indirect X
            if instruction == 'A1':
                self.handleInstructionLDAIndirectX()

            # LDA Indirect Y
            if instruction == 'B1':
                self.handleInstructionLDAIndirectY()

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

            # LDY Zero page
            elif instruction == 'A4':
                self.handleInstructionLDYZeroPage()

            # LDY Zero page X
            elif instruction == 'B4':
                self.handleInstructionLDYZeroPageX()

            # LDY Absolute
            elif instruction == 'AC':
                self.handleInstructionLDYAbsolute()

            # LDY Absolute X
            elif instruction == 'BC':
                self.handleInstructionLDYAbsoluteX()

            # STA Zero page
            elif instruction == '85':
                self.handleInstructionSTAZeroPage()

            # STA Zero page X
            elif instruction == '95':
                self.handleInstructionSTAZeroPageX()

            # STA Absolute
            elif instruction == '8D':
                self.handleInstructionSTAAbsolute()

            # STA Absolute X
            elif instruction == '9D':
                self.handleInstructionSTAAbsoluteX()

            # STA Absolute Y
            elif instruction == '99':
                self.handleInstructionSTAAbsoluteY()

            # STA Indirect X
            elif instruction == '81':
                self.handleInstructionSTAIndirectX()

            # STA Indirect Y
            elif instruction == '91':
                self.handleInstructionSTAIndirectY()

            # STX Absolute
            elif instruction == '8E':
                self.handleInstructionSTXAbsolute()

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
            elif instruction == '84':
                self.handleInstructionSTYZeroPage()

            # STY Zero page X
            elif instruction == '94':
                self.handleInstructionSTYZeroPageX()

            # STY Absolute
            elif instruction == '8C':
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
                self.handleInstructionDECZeroPage()
            
            # DEC Zero page X
            elif instruction == 'D6':
                self.handleInstructionDECZeroPageX()

            # DEC Absolute
            elif instruction == 'CE':
                self.handleInstructionDECAbsolute()

            # DEC Absolute X
            elif instruction == 'DE':
                self.handleInstructionDECAbsoluteX()

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
                pass

            # BRK ( start NMI operation )  
            elif instruction == '00':
                break

            # JMP Absolute
            elif instruction == '4C':
                self.handleInstructionJmpAbsolute()
        
            # JMP Indirect
            elif instruction == '6C':
                self.handleInstructionJmpIndirect()

            # ADC Immediate
            elif instruction == '69':
                self.handleInstructionAdcImmediate()

            # ADC Zero Page
            elif instruction == '65':
                self.handleInstructionAdcZeroPage()

            # ADC Zero Page X
            elif instruction == '75':
                self.handleInstructionAdcZeroPageX()

            # ADC Absolute
            elif instruction == '6D':
                self.handleInstructionAdcAbsolute()

            # ADC Absolute X
            elif instruction == '7D':
                self.handleInstructionAdcAbsoluteX()

            # ADC Absolute Y
            elif instruction == '79':
                self.handleInstructionAdcAbsoluteY()

            # ADC Indirect X
            elif instruction == '61':
                self.handleInstructionAdcIndirectX()

            # ADC Indirect Y
            elif instruction == '71':
                self.handleInstructionAdcIndirectY()

            # SBC Immediate
            elif instruction == 'E9':
                self.handleInstructionSbcImmediate()

            # SBC Zero Page
            elif instruction == 'E5':
                self.handleInstructionSbcZeroPage()

            # SBC Zero Page X
            elif instruction == 'F5':
                self.handleInstructionSbcZeroPageX()

            # SBC Absolute
            elif instruction == 'ED':
                self.handleInstructionSbcAbsolute()

            # SBC Absolute X
            elif instruction == 'FD':
                self.handleInstructionSbcAbsoluteX()

            # SBC Absolute Y
            elif instruction == 'F9':
                self.handleInstructionSbcAbsoluteY()

            # SBC Indirect X
            elif instruction == 'E1':
                self.handleInstructionSbcIndirectX()

            # SBC Indirect Y
            elif instruction == 'F1':
                self.handleInstructionSbcIndirectY()

            # AND Immediante
            elif instruction == '29':
                self.handleInstructionAndImmediate()

            # AND Zero Page
            elif instruction == '25':
                self.handleInstructionAndZeroPage()

            # AND Zero Page X
            elif instruction == '35':
                self.handleInstructionAndZeroPageX()

            # AND Absolute
            elif instruction == '2D':
                self.handleInstructionAndAbsolute()

            # AND Absolute X
            elif instruction == '3D':
                self.handleInstructionAndAbsoluteX()

            # AND Absolute Y
            elif instruction == '39':
                self.handleInstructionAndAbsoluteY()

            # AND Indirect X
            elif instruction == '21':
                self.handleInstructionAndIndirectX()

            # AND Indirect Y
            elif instruction == '31':
                self.handleInstructionAndIndirectY()

            # ORA Inclusive Or Immediate
            elif instruction == '09':
                self.handleInstructionORAImmediate()

            # ORA Inclusive Or Zero Page
            elif instruction == '05':
                self.handleInstructionORAZeroPage()

            # ORA Inclusive Or Zero Page X
            elif instruction == '15':
                self.handleInstructionORAZeroPageX()

            # ORA Inclusive Or Absolute
            elif instruction == '0D':
                self.handleInstructionORAAbsolute()

            # ORA Inclusive Or Absolute
            elif instruction == '1D':
                self.handleInstructionORAAbsoluteX()

            # ORA Inclusive Or Absolute
            elif instruction == '19':
                self.handleInstructionORAAbsoluteY()
            
            # ORA Inclusive Or Indirect X
            elif instruction == '01':
                self.handleInstructionORAIndirectX()

            # ORA Inclusive Or Indirect Y
            elif instruction == '11':
                self.handleInstructionORAIndirectY()

            # EOR Exclusive Or Immediate
            elif instruction == '49':
                self.handleInstructionEORImmediate()

            # EOR Exclusive Or Zero Page
            elif instruction == '45':
                self.handleInstructionEORZeroPage()

            # EOR Exclusive Or Zero Page X
            elif instruction == '55':
                self.handleInstructionEORZeroPageX()

            # EOR Exclusive Or Absolute
            elif instruction == '4D':
                self.handleInstructionEORAbsolute()

            # EOR Exclusive Or Absolute X
            elif instruction == '5D':
                self.handleInstructionEORAbsoluteX()

            # EOR Exclusive Or Absolute Y
            elif instruction == '59':
                self.handleInstructionEORAbsoluteY()

            # EOR Exclusive Or Indirect X
            elif instruction == '41':
                self.handleInstructionEORIndirectX()

            # EOR Exclusive Or Indirect Y
            elif instruction == '51':
                self.handleInstructionEORIndirectY()

            # CLC Clear Carry Flag
            elif instruction == '18':
                self.handleInstructionClearCarryFlag()

            # CLD Clear Decimal Mode
            elif instruction == 'D8':
                self.handleInstructionClearDecimalMode()

            # CLI Clear Interrupt Disable
            elif instruction == '58':
                self.handleInstructionClearInterruptDisable()

            # CLV Clear Overflow Flag
            elif instruction == 'B8':
                self.handleInstructionClearOverflowFlag()

            # SEC Set Carry Flag
            elif instruction == '38':
                self.handleInstructionSetCarryFlag()

            # SED Set Decimal Flag
            elif instruction == 'F8':
                self.handleInstructionSetDecimalMode()
            
            # SEI Set Interrupt Disable
            elif instruction == '78':
                self.handleInstructionSetInterruptDisable()

            # Stack instructions

            # TXS Transfer X to Stack pointer
            elif instruction == '9A':
                self.handleInstructionTXS()

            # STX Transfer Stack pointer to X
            elif instruction == 'BA':
                self.handleInstructionSTX()

            # PHA Push Accumulator
            elif instruction == '48':
                self.handleInstructionPHA()

            # PLA Pull Accumulator
            elif instruction == '68':
                self.handleInstructionPLA()

            # PHP Push Processor status
            elif instruction == '08':
                self.handleInstructionPHP()

            # PLP Pull Processor status
            elif instruction == '28':
                self.handleInstructionPLP()

            # JSR
            elif instruction == '20':
                self.handleInstructionJSR()

            # RTS
            elif instruction == '60':
                self.handleInstructionRTS()

            # RTI
            elif instruction == '40':
                self.handleInstructionRTI()

            self.log()
            self.address = None
            instruction = self.get_next_byte()