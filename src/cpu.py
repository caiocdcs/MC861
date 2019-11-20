from utils import log, logls
from flagController import FlagController
from stack import Stack
from defines import *

int8 = int
int16 = int

KB = 1024

class CPU:

    def __init__(self, console):
        self.console = console

        self.sp = int16(253) # SP starts at 0xfd
        self.pc = int16(0)
        self.a = int8(0)
        self.x = int8(0)
        self.y = int8(0)
        self.flagController = FlagController()
        self.stack = Stack()

        self.address = None

        self.triggerNMI = False

        self.cycles = 0

        self.handlers = {
                '0A': (self.handleInstructionASLAccumulator, 2),
               '06': (self.handleInstructionASLZeroPage, 5),
               '16': (self.handleInstructionASLZeroPageX, 6),
               '0E': (self.handleInstructionASLAbsolute,6),
               '1E': (self.handleInstructionASLAbsoluteX,7),
               '4A': (self.handleInstructionLSRAccumulator,2),
               '46': (self.handleInstructionLSRZeroPage,5),
               '56': (self.handleInstructionLSRZeroPageX,6),
               '4E': (self.handleInstructionLSRAbsolute,6),
               '5E': (self.handleInstructionLSRAbsoluteX,7),
               '2A': (self.handleInstructionROLAccumulator,2),
               '26': (self.handleInstructionROLZeroPage,5),
               '36': (self.handleInstructionROLZeroPageX,6),
               '2E': (self.handleInstructionROLAbsolute,6),
               '3E': (self.handleInstructionROLAbsoluteX,7),
               '6A': (self.handleInstructionRORAccumulator,2),
               '66': (self.handleInstructionRORZeroPage,5),
               '76': (self.handleInstructionRORZeroPageX,6),
               '6E': (self.handleInstructionRORAbsolute,6),
               '7E': (self.handleInstructionRORAbsoluteX,7),
               '24': (self.handleInstructionBITZeroPage,3),
               '2C': (self.handleInstructionBITAbsolute,4),
               'C9': (self.handleInstructionCMPImmediate,2),
               'C5': (self.handleInstructionCMPZeroPage,3),
               'D5': (self.handleInstructionCMPZeroPageX,4),
               'CD': (self.handleInstructionCMPAbsolute,4),
               'DD': (self.handleInstructionCMPAbsoluteX,4),
               'D9': (self.handleInstructionCMPAbsoluteY,4),
               'C1': (self.handleInstructionCMPIndirectX,6),
               'D1': (self.handleInstructionCMPIndirectY,5),
               'E0': (self.handleInstructionCPXImmediate,2),
               'E4': (self.handleInstructionCPXZeroPage,3),
               'EC': (self.handleInstructionCPXAbsolute,4),
               'C0': (self.handleInstructionCPYImmediate,2),
               'C4': (self.handleInstructionCPYZeroPage,3),
               'CC': (self.handleInstructionCPYAbsolute,4),
               'A9': (self.handleInstructionLDAImmediate,2),
               'A5': (self.handleInstructionLDAZeroPage,3),
               'B5': (self.handleInstructionLDAZeroPageX,4),
               'AD': (self.handleInstructionLDAAbsolute,4),
               'BD': (self.handleInstructionLDAAbsoluteX,4),
               'B9': (self.handleInstructionLDAAbsoluteY,4),
               'A1': (self.handleInstructionLDAIndirectX,6),
               'B1': (self.handleInstructionLDAIndirectY,5),
               'A2': (self.handleInstructionLDXImmediate,2),
               'A6': (self.handleInstructionLDXZeroPage,3),
               'B6': (self.handleInstructionLDXZeroPageY,4),
               'AE': (self.handleInstructionLDXAbsolute,4),
               'BE': (self.handleInstructionLDXAbsoluteY,4),
               'A0': (self.handleInstructionLDYImmediate,2),
               'A4': (self.handleInstructionLDYZeroPage,3),
               'B4': (self.handleInstructionLDYZeroPageX,4),
               'AC': (self.handleInstructionLDYAbsolute,4),
               'BC': (self.handleInstructionLDYAbsoluteX,4),
               '85': (self.handleInstructionSTAZeroPage,3),
               '95': (self.handleInstructionSTAZeroPageX,4),
               '8D': (self.handleInstructionSTAAbsolute,4),
               '9D': (self.handleInstructionSTAAbsoluteX,5),
               '99': (self.handleInstructionSTAAbsoluteY,5),
               '81': (self.handleInstructionSTAIndirectX,6),
               '91': (self.handleInstructionSTAIndirectY,6),
               '8E': (self.handleInstructionSTXAbsolute,3),
               '86': (self.handleInstructionSTXZeroPage,4),
               '96': (self.handleInstructionSTXZeroPageY,4),
               '84': (self.handleInstructionSTYZeroPage,3),
               '94': (self.handleInstructionSTYZeroPageX,4),
               '8C': (self.handleInstructionSTYAbsolute,4),
               'E6': (self.handleInstructionINCZeroPage,5),
               'F6': (self.handleInstructionINCZeroPageX,6),
               'EE': (self.handleInstructionINCAbsolute,6),
               'FE': (self.handleInstructionINCAbsoluteX,7),
               'E8': (self.handleInstructionINX,2),
               'C8': (self.handleInstructionINY,2),
               'C6': (self.handleInstructionDECZeroPage,5),
               'D6': (self.handleInstructionDECZeroPageX,6),
               'CE': (self.handleInstructionDECAbsolute,6),
               'DE': (self.handleInstructionDECAbsoluteX,7),
               'CA': (self.handleInstructionDEX,2),
               '88': (self.handleInstructionDEY,2),
               'AA': (self.handleInstructionTAX,2),
               '8A': (self.handleInstructionTXA,2),
               'A8': (self.handleInstructionTAY,2),
               '98': (self.handleInstructionTYA,2),
               '4C': (self.handleInstructionJmpAbsolute,3),
               '6C': (self.handleInstructionJmpIndirect,5),
               '69': (self.handleInstructionAdcImmediate,2),
               '65': (self.handleInstructionAdcZeroPage,3),
               '75': (self.handleInstructionAdcZeroPageX,4),
               '6D': (self.handleInstructionAdcAbsolute,4),
               '7D': (self.handleInstructionAdcAbsoluteX,4),
               '79': (self.handleInstructionAdcAbsoluteY,4),
               '61': (self.handleInstructionAdcIndirectX,6),
               '71': (self.handleInstructionAdcIndirectY,5),
               'E9': (self.handleInstructionSbcImmediate,2),
               'E5': (self.handleInstructionSbcZeroPage,3),
               'F5': (self.handleInstructionSbcZeroPageX,4),
               'ED': (self.handleInstructionSbcAbsolute,4),
               'FD': (self.handleInstructionSbcAbsoluteX,4),
               'F9': (self.handleInstructionSbcAbsoluteY,4),
               'E1': (self.handleInstructionSbcIndirectX,6),
               'F1': (self.handleInstructionSbcIndirectY,5),
               '29': (self.handleInstructionAndImmediate,2),
               '25': (self.handleInstructionAndZeroPage,3),
               '35': (self.handleInstructionAndZeroPageX,4),
               '2D': (self.handleInstructionAndAbsolute,4),
               '3D': (self.handleInstructionAndAbsoluteX,4),
               '39': (self.handleInstructionAndAbsoluteY,4),
               '21': (self.handleInstructionAndIndirectX,6),
               '31': (self.handleInstructionAndIndirectY,5),
               '09': (self.handleInstructionORAImmediate,2),
               '05': (self.handleInstructionORAZeroPage,3),
               '15': (self.handleInstructionORAZeroPageX,4),
               '0D': (self.handleInstructionORAAbsolute,4),
               '1D': (self.handleInstructionORAAbsoluteX,4),
               '19': (self.handleInstructionORAAbsoluteY,4),
               '01': (self.handleInstructionORAIndirectX,6),
               '11': (self.handleInstructionORAIndirectY,5),
               '49': (self.handleInstructionEORImmediate,2),
               '45': (self.handleInstructionEORZeroPage,3),
               '55': (self.handleInstructionEORZeroPageX,4),
               '4D': (self.handleInstructionEORAbsolute,4),
               '5D': (self.handleInstructionEORAbsoluteX,4),
               '59': (self.handleInstructionEORAbsoluteY,4),
               '41': (self.handleInstructionEORIndirectX,6),
               '51': (self.handleInstructionEORIndirectY,5),
               '18': (self.handleInstructionClearCarryFlag,2),
               'D8': (self.handleInstructionClearDecimalMode,2),
               '58': (self.handleInstructionClearInterruptDisable,2),
               'B8': (self.handleInstructionClearOverflowFlag,2),
               '38': (self.handleInstructionSetCarryFlag,2),
               'F8': (self.handleInstructionSetDecimalMode,2),
               '78': (self.handleInstructionSetInterruptDisable,2),
               '9A': (self.handleInstructionTXS,2),
               'BA': (self.handleInstructionTSX,2),
               '48': (self.handleInstructionPHA,3),
               '68': (self.handleInstructionPLA,4),
               '08': (self.handleInstructionPHP,3),
               '28': (self.handleInstructionPLP,4),
               '20': (self.handleInstructionJSR,6),
               '60': (self.handleInstructionRTS,6),
               '10': (self.handleInstructionBPL,2),
               '30': (self.handleInstructionBMI,2),
               '50': (self.handleInstructionBVC,2),
               '70': (self.handleInstructionBVS,2),
               '90': (self.handleInstructionBCC,2),
               'B0': (self.handleInstructionBCS,2),
               'D0': (self.handleInstructionBNE,2),
               'F0': (self.handleInstructionBEQ,2),
               '40': (self.handleInstructionRTI,1),
               'EA': (self.handleInstructionNoOp,2),
               '00': (self.handleInstructionBrk,7)
            }

    def Read(self, address):
        if address < 0x2000:
            return self.console.RAM[address & 0x07FF]
        elif address < 0x4000:
            return self.console.PPU.ReadRegister(0x2000 | (address & 0x7))
        elif address == 0x4014:
            return self.console.PPU.ReadRegister(address)
        elif address == 0x4015:
            pass
            #return self.console.APU.ReadRegister(address)
        elif address == 0x4016:
            return (self.console.Controller1.Read())
        elif address == 0x4017:
            return (self.console.Controller2.Read())
        elif address < 0x6000:
            pass # [TODO] I/O registers
        elif address >= 0x6000:
            return (self.console.Mapper.Read(address))
        return uint8(0)

    def Write(self, address, value):
        if address < 0x2000:
            self.console.RAM[address & 0x07FF] = value
        elif address < 0x4000:
            self.console.PPU.WriteRegister(0x2000 | (address & 0x7), value)
        elif address < 0x4014:
            pass
            #self.console.APU.WriteRegister(address, value)
        elif address == 0x4014:
            self.console.PPU.WriteRegister(address, value)
        elif address == 0x4015:
            pass
            #self.console.APU.WriteRegister(address, value)
        elif address == 0x4016:
            self.console.Controller1.Write(value)
            self.console.Controller2.Write(value)
        elif address == 0x4017:
            pass
            #self.console.APU.WriteRegister(address, value)
        elif address < 0x6000:
            pass # [TODO] I/O registers
        elif address >= 0x6000:
            self.console.Mapper.Write(address, value)

    def connectBus(self, bus):
        self.bus = bus

    def log(self):
        p = self.flagController.getFlagsStatusByte()
        if self.address:
            logls(self.a, self.x, self.y, self.sp, self.pc, p, self.address,
                self._get_address_str(self.address))
        else:
            log(self.a, self.x, self.y, self.sp, self.pc, p)

    def get_next_byte(self):
        byte = self.Read(self.pc)
        self.pc = self.pc + 1

        return format(byte, '02x').upper()

    def _get_address_int(self, address, set_address=False):
        return self.Read(address)

    def _get_address_str(self, address, set_address=False):
        return self._get_address_int(int(address, 16), set_address)

    def _set_address_int(self, address, data, set_address=False):
        return self.Write(address, data)

    def _set_address_str(self, address, data, set_address=False):
        return self._set_address_int(int(address, 16), data, set_address)

    def reset(self):
        self.sp = int8(253) # SP starts at 0xfd
        low_byte = self.Read(0xFFFC)
        high_byte = self.Read(0xFFFD)

        self.pc = (high_byte << 8) | low_byte
        self.a = int8(0)
        self.x = int8(0)
        self.y = int8(0)
        self.flagController = FlagController()
        self.stack = Stack()

        self.address = None

        self.cycles = 8

    def irq(self):
        if self.flagController.geInterrupDisabledtFlag() == 0:
            pc_l = format(self.pc, '04x')[2:4]
            pc_h = format(self.pc, '04x')[0:2]

            stackAddress = self.stack.getAddress() + (self.sp)
            self._set_address_int(stackAddress, int8(int(pc_h, 16)))
            self.sp = self.sp - 1

            stackAddress = self.stack.getAddress() + (self.sp)
            self._set_address_int(stackAddress, int8(int(pc_l, 16)))
            self.sp = self.sp - 1

            self.flagController.setInterrupDisabledtFlag()
            self.flagController.clearBreakFlag()
            self.flagController.setUnusedFlag()
            self.handleInstructionPHP()

            low_byte = self.Read(0xFFFE)
            high_byte = self.Read(0xFFFF)

            self.pc = (high_byte << 8) | low_byte

            self.cycles = 7

    def nmi(self):
        print("NMI")
        pc_l = format(self.pc, '04x')[2:4]
        pc_h = format(self.pc, '04x')[0:2]

        stackAddress = self.stack.getAddress() + (self.sp)
        self._set_address_int(stackAddress, int8(int(pc_h, 16)))
        self.sp = self.sp - 1

        stackAddress = self.stack.getAddress() + (self.sp)
        self._set_address_int(stackAddress, int8(int(pc_l, 16)))
        self.sp = self.sp - 1

        self.flagController.setInterrupDisabledtFlag()
        self.flagController.clearBreakFlag()
        self.flagController.setUnusedFlag()
        self.handleInstructionPHP()

        low_byte = self.Read(0xFFFA)
        high_byte = self.Read(0xFFFB)
        self.pc = (high_byte << 8) | low_byte

        self.cycles = 8

    def step(self):

        if self.triggerNMI:
            self.nmi()

        self.triggerNMI = False

        # function if op code doesn't exist
        def noHandler():
            pass

        instruction = self.get_next_byte()

        handler, c = self.handlers.get(instruction, (noHandler, 1))
        handler()

        # self.log() # TODO: Uncomment later!
        self.address = None
        return c


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
        value = self._get_address_str(address)
        self.adc(value)

    def handleInstructionAdcZeroPageX(self):
        byte = self.get_next_byte()
        addressStart = int(byte, 16)
        address = (addressStart + self.x) & 0xFF
        value = self._get_address_int(address)
        self.adc(value)

    def handleInstructionAdcAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        value = self._get_address_str(address)
        self.adc(value)

    def handleInstructionAdcAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        addressStr = (high_byte + low_byte)
        addressStart = int(addressStr, 16)
        address = (addressStart + self.x) & 0xFF
        value = self._get_address_int(address)
        self.adc(value)

    def handleInstructionAdcAbsoluteY(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        addressStr = (high_byte + low_byte)
        addressStart = int(addressStr, 16)
        address = (addressStart + self.y) & 0xFF
        value = self._get_address_int(address)
        self.adc(value)

    def handleInstructionAdcIndirectX(self):
        byte = self.get_next_byte()

        address = format((int(byte, 16) + self.x), '04x')
        low_byte = format(self._get_address_str(address), '02x')
        high_byte = format(self._get_address_str(format((int(address, 16) + 1), '04x')), '02x')

        final_address = (high_byte + low_byte)

        value = self._get_address_str(final_address)
        self.adc(value)

    def handleInstructionAdcIndirectY(self):
        byte = self.get_next_byte()

        l_byte = format(self._get_address_str(byte), '02x')
        h_byte = format(self._get_address_int(int(byte, 16) + 1), '02x')

        address = (h_byte + l_byte)
        final_address = int(address, 16) + self.y

        value = self._get_address_int(final_address)
        self.adc(value)

    def adc(self, value):
        carry = self.flagController.getCarryFlag()
        aOldValue = self.a
        sum = aOldValue + value + carry
        self.a = sum & 0xFF                           # set a value limiting to one byte

        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag
        self.flagController.setCarryFlagIfNeeded(sum)         # set carry flag

        # set overflow flag
        if (aOldValue ^ value) & 0x80 == 0 and (aOldValue ^ self.a) & 0x80 != 0:
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
        value = self._get_address_str(address)
        self.sbc(value)

    def handleInstructionSbcZeroPageX(self):
        byte = self.get_next_byte()
        addressStart = int(byte, 16)
        address = (addressStart + self.x) & 0xFF
        value = self._get_address_int(address)
        self.sbc(value)

    def handleInstructionSbcAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        value = self._get_address_str(address)
        self.sbc(value)

    def handleInstructionSbcAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        addressStr = (high_byte + low_byte)
        addressStart = int(addressStr, 16)
        address = (addressStart + self.x) & 0xFF
        value = self._get_address_int(address)
        self.sbc(value)

    def handleInstructionSbcAbsoluteY(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        addressStr = (high_byte + low_byte)
        addressStart = int(addressStr, 16)
        address = (addressStart + self.y) & 0xFF
        value = self._get_address_int(address)
        self.sbc(value)

    def handleInstructionSbcIndirectX(self):
        byte = self.get_next_byte()

        address = format((int(byte, 16) + self.x), '04x')
        low_byte = format(self._get_address_str(address), '02x')
        high_byte = format(self._get_address_str(format((int(address, 16) + 1), '04x')), '02x')

        final_address = (high_byte + low_byte)

        value = self._get_address_str(final_address)
        self.sbc(value)

    def handleInstructionSbcIndirectY(self):
        byte = self.get_next_byte()

        l_byte = format(self._get_address_str(byte), '02x')
        h_byte = format(self._get_address_int(int(byte, 16) + 1), '02x')

        address = (h_byte + l_byte)
        final_address = int(address, 16) + self.y

        value = self._get_address_int(final_address)
        self.sbc(value)

    def sbc(self, value):
        carry = self.flagController.getCarryFlag()
        aOldValue = self.a
        result = aOldValue - value - (1-carry)
        self.a = result & 0xFF                          # set a value limiting to one byte
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

        # set overflow flag
        if (aOldValue ^ value) & 0x80 == 0 and (aOldValue ^ self.a) & 0x80 != 0:
            self.flagController.setOverflowFlag()
            self.flagController.clearCarryFlag()
        else:
            self.flagController.clearOverflowFlag()
            self.flagController.setCarryFlag()

    ## AND Instructions

    def handleInstructionAndImmediate(self):
        byte = self.get_next_byte()
        self.a = int(byte, 16) & self.a
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionAndZeroPage(self):
        address = self.get_next_byte()
        value = self._get_address_str(address)
        self.a = value & self.a
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionAndZeroPageX(self):
        byte = self.get_next_byte()
        addressStart = int(byte, 16)
        address = (addressStart + self.x) & 0xFF
        value = self._get_address_int(address)
        self.a = value & self.a
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag

    def handleInstructionAndAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        value = self._get_address_str(address)
        self.a = value & self.a
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionAndAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        addressStr = (high_byte + low_byte)
        addressStart = int(addressStr, 16)
        address = (addressStart + self.x) & 0xFF
        value = self._get_address_int(address)
        self.a = value & self.a
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionAndAbsoluteY(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        addressStr = (high_byte + low_byte)
        addressStart = int(addressStr, 16)
        address = (addressStart + self.y) & 0xFF
        value = self._get_address_int(address)
        self.a = value & self.a
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionAndIndirectX(self):
        byte = self.get_next_byte()

        address = format((int(byte, 16) + self.x), '04x')
        low_byte = format(self._get_address_str(address), '02x')
        high_byte = format(self._get_address_str(format((int(address, 16) + 1), '04x')), '02x')

        final_address = (high_byte + low_byte)

        value = self._get_address_str(final_address)
        self.a = value & self.a
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionAndIndirectY(self):
        byte = self.get_next_byte()

        l_byte = format(self._get_address_str(byte), '02x')
        h_byte = format(self._get_address_int(int(byte, 16) + 1), '02x')

        address = (h_byte + l_byte)
        final_address = int(address, 16) + self.y

        value = self._get_address_int(final_address)
        self.a = value & self.a
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    ## ORA Instructions
    def handleInstructionORAImmediate(self):
        byte = self.get_next_byte()
        self.a = int(byte, 16) | self.a
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionORAZeroPage(self):
        address = self.get_next_byte()
        value = self._get_address_str(address)
        self.a = value | self.a
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionORAZeroPageX(self):
        byte = self.get_next_byte()
        addressStart = int(byte, 16)
        address = (addressStart + self.x) & 0xFF
        value = self._get_address_int(address)
        self.a = value | self.a
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionORAAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        value = self._get_address_str(address)
        self.a = value | self.a
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionORAAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        addressStr = (high_byte + low_byte)
        addressStart = int(addressStr, 16)
        address = (addressStart + self.x) & 0xFF
        value = self._get_address_int(address)
        self.a = value | self.a
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionORAAbsoluteY(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        addressStr = (high_byte + low_byte)
        addressStart = int(addressStr, 16)
        address = (addressStart + self.y) & 0xFF
        value = self._get_address_int(address)
        self.a = value | self.a
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionORAIndirectX(self):
        byte = self.get_next_byte()

        address = format((int(byte, 16) + self.x), '04x')
        low_byte = format(self._get_address_str(address), '02x')
        high_byte = format(self._get_address_str(format((int(address, 16) + 1), '04x')), '02x')

        final_address = (high_byte + low_byte)

        value = self._get_address_str(final_address)
        self.a = value | self.a
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionORAIndirectY(self):
        byte = self.get_next_byte()

        l_byte = format(self._get_address_str(byte), '02x')
        h_byte = format(self._get_address_int(int(byte, 16) + 1), '02x')

        address = (h_byte + l_byte)
        final_address = int(address, 16) + self.y

        value = self._get_address_int(final_address)
        self.a = value | self.a
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    ## EOR Instructions
    def handleInstructionEORImmediate(self):
        byte = self.get_next_byte()
        self.a = int(byte, 16) ^ self.a
        self.x = 9
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionEORZeroPage(self):
        address = self.get_next_byte()
        value = self._get_address_str(address)
        self.a = value ^ self.a
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionEORZeroPageX(self):
        byte = self.get_next_byte()
        addressStart = int(byte, 16)
        address = (addressStart + self.x) & 0xFF
        value = self._get_address_int(address)
        self.a = value ^ self.a
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionEORAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        value = self._get_address_str(address)
        self.a = value ^ self.a
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionEORAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        addressStr = (high_byte + low_byte)
        addressStart = int(addressStr, 16)
        address = (addressStart + self.x) & 0xFF
        value = self._get_address_int(address)
        self.a = value ^ self.a
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionEORAbsoluteY(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        addressStr = (high_byte + low_byte)
        addressStart = int(addressStr, 16)
        address = (addressStart + self.y) & 0xFF
        value = self._get_address_int(address)
        self.a = value ^ self.a
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionEORIndirectX(self):
        byte = self.get_next_byte()

        address = format((int(byte, 16) + self.x), '04x')
        low_byte = format(self._get_address_str(address), '02x')
        high_byte = format(self._get_address_str(format((int(address, 16) + 1), '04x')), '02x')

        final_address = (high_byte + low_byte)

        value = self._get_address_str(final_address)
        self.a = value ^ self.a
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionEORIndirectY(self):
        byte = self.get_next_byte()

        l_byte = format(self._get_address_str(byte), '02x')
        h_byte = format(self._get_address_int(int(byte, 16) + 1), '02x')

        address = (h_byte + l_byte)
        final_address = int(address, 16) + self.y

        value = self._get_address_int(final_address)
        self.a = value ^ self.a
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    ## INC Instructions
    def handleInstructionINCZeroPage(self):
        byte = self.get_next_byte()
        #self.address = byte.zfill(4)

        value = self._get_address_str(byte) + 1

        self._set_address_str(byte, int8(value), set_address=True)
        self.flagController.setNegativeIfNeeded(value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(value) # set zero flag

    def handleInstructionINCZeroPageX(self):
        byte = self.get_next_byte()
        address = format((int(byte, 16) + self.x), '04x')

        value = self._get_address_str(address) + 1

        self._set_address_str(address, int8(value), set_address=True)
        self.flagController.setNegativeIfNeeded(value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(value) # set zero flag

    def handleInstructionINCAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        value = self._get_address_str(address) + 1

        self._set_address_str(address, int8(value), set_address=True)
        self.flagController.setNegativeIfNeeded(value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(value) # set zero flag

    def handleInstructionINCAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        lookup_address = (high_byte + low_byte)
        address = format((int(lookup_address, 16) + self.x), '04x')

        value = self._get_address_str(address) + 1

        self._set_address_str(address, int8(value), set_address=True)
        self.flagController.setNegativeIfNeeded(value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(value) # set zero flag

    def handleInstructionINX(self):
        self.x = self.x + 1
        self.flagController.setNegativeIfNeeded(self.x) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.x) # set zero flag

    def handleInstructionINY(self):
        self.y = self.y + 1
        self.flagController.setNegativeIfNeeded(self.y) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.y) # set zero flag

    ## DEC Instructions
    def handleInstructionDECZeroPage(self):
        byte = self.get_next_byte()
        address = byte.zfill(4)
        value = self._get_address_str(address) - 1

        self._set_address_str(address, int8(value), set_address=True)
        self.flagController.setNegativeIfNeeded(value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(value) # set zero flag

    def handleInstructionDECZeroPageX(self):
        byte = self.get_next_byte()
        address = format((int(byte, 16) + self.x), '04x')

        value = self._get_address_str(address) - 1

        self._set_address_str(address, int8(value), set_address=True)
        self.flagController.setNegativeIfNeeded(value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(value) # set zero flag

    def handleInstructionDECAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)

        value = self._get_address_str(address) - 1

        self._set_address_str(address, int8(value), set_address=True)
        self.flagController.setNegativeIfNeeded(value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(value) # set zero flag

    def handleInstructionDECAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        lookup_address = (high_byte + low_byte)
        address = format((int(lookup_address, 16) + self.x), '04x')

        value = self._get_address_str(address) - 1

        self._set_address_str(address, int8(value), set_address=True)
        self.flagController.setNegativeIfNeeded(value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(value) # set zero flag

    def handleInstructionDEX(self):
        self.x = self.x - 1
        self.flagController.setNegativeIfNeeded(self.x) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.x) # set zero flag

    def handleInstructionDEY(self):
        self.y = self.y - 1
        self.flagController.setNegativeIfNeeded(self.y) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.y) # set zero flag


    ## Transfer Instructions
    def handleInstructionTAX(self):
        self.x = self.a
        self.flagController.setNegativeIfNeeded(self.x) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.x) # set zero flag

    def handleInstructionTXA(self):
        self.a = self.x
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionTAY(self):
        self.y = self.a
        self.flagController.setNegativeIfNeeded(self.y) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.y) # set zero flag

    def handleInstructionTYA(self):
        self.a = self.y
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    ## ASL Instructions
    def handleInstructionASLAccumulator(self):
        carry = 1 if (0b10000000 & self.a) else 0
        self.a = self.a << 1

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionASLZeroPage(self):
        address = self.get_next_byte()
        mem = self._get_address_str(address)
        carry = 1 if (0b10000000 & mem) else 0
        self._set_address_str(address, int8(mem << 1))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem << 1) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem << 1) # set zero flag

    def handleInstructionASLZeroPageX(self):
        byte = self.get_next_byte()
        address = format((int(byte, 16) + self.x), '04x')
        mem = self._get_address_str(address)
        carry = 1 if (0b10000000 & mem) else 0
        self._set_address_str(address, int8(mem << 1))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem << 1) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem << 1) # set zero flag

    def handleInstructionASLAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        mem = self._get_address_str(address)
        carry = 1 if (0b10000000 & mem) else 0
        self._set_address_str(address, int8(mem << 1))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem << 1) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem << 1) # set zero flag

    def handleInstructionASLAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        final_address = format((int(address, 16) + self.x), '04x')

        mem = self._get_address_str(final_address)
        carry = 1 if (0b10000000 & mem) else 0
        self._set_address_str(final_address, int8(mem << 1))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem << 1) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem << 1) # set zero flag

    ## LSR Instructions
    def handleInstructionLSRAccumulator(self):
        carry = 1 if (0b00000001 & self.a) else 0
        self.a = self.a >> 1

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionLSRZeroPage(self):
        address = self.get_next_byte()
        mem = self._get_address_str(address)
        carry = 1 if (0b00000001 & mem) else 0
        self._set_address_str(address, int8(mem >> 1))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem >> 1) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem >> 1) # set zero flag

    def handleInstructionLSRZeroPageX(self):
        byte = self.get_next_byte()
        address = format((int(byte, 16) + self.x), '04x')
        mem = self._get_address_str(address)
        carry = 1 if (0b00000001 & mem) else 0
        self._set_address_str(address, int8(mem >> 1))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem >> 1) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem >> 1) # set zero flag

    def handleInstructionLSRAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        mem = self._get_address_str(address)
        carry = 1 if (0b00000001 & mem) else 0
        self._set_address_str(address, int8(mem >> 1))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem >> 1) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem >> 1) # set zero flag

    def handleInstructionLSRAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        final_address = format((int(address, 16) + self.x), '04x')

        mem = self._get_address_str(final_address)
        carry = 1 if (0b00000001 & mem) else 0
        self._set_address_str(final_address, int8(mem >> 1))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem >> 1) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem >> 1) # set zero flag

    ## BIT test BITs
    def handleInstructionBITZeroPage(self):
        address = self.get_next_byte()
        mem = self._get_address_str(address)
        self.flagController.setZeroFlagIfNeeded(self.a & mem) # set zero flag

        neg = 1 if (0b10000000 & mem) else 0
        ovf = 1 if (0b01000000 & mem) else 0

        self.flagController.setNegativeFlag() if ovf else self.flagController.clearNegativeFlag()
        self.flagController.setOverflowFlag() if ovf else self.flagController.clearOverflowFlag()

    def handleInstructionBITAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        mem = self._get_address_str(address)
        self.flagController.setZeroFlagIfNeeded(self.a & mem) # set zero flag

        neg = 1 if (0b10000000 & mem) else 0
        ovf = 1 if (0b01000000 & mem) else 0

        self.flagController.setNegativeFlag() if ovf else self.flagController.clearNegativeFlag()
        self.flagController.setOverflowFlag() if ovf else self.flagController.clearOverflowFlag()

    ## ROL Instructions
    def handleInstructionROLAccumulator(self):
        carry = 1 if (0b10000000 & self.a) else 0
        c = self.flagController.getCarryFlag()
        self.a = self.a << 1 | c

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionROLZeroPage(self):
        address = self.get_next_byte()
        mem = self._get_address_str(address)
        carry = 1 if (0b10000000 & mem) else 0
        c = self.flagController.getCarryFlag()
        self._set_address_str(address, int8(mem << 1 | c))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem << 1 | c) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem << 1 | c) # set zero flag

    def handleInstructionROLZeroPageX(self):
        byte = self.get_next_byte()
        address = format((int(byte, 16) + self.x), '04x')
        mem = self._get_address_str(address)
        carry = 1 if (0b10000000 & mem) else 0
        c = self.flagController.getCarryFlag()
        self._set_address_str(address, int8(mem << 1 | c))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem << 1 | c) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem << 1 | c) # set zero flag

    def handleInstructionROLAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        mem = self._get_address_str(address)
        carry = 1 if (0b10000000 & mem) else 0
        c = self.flagController.getCarryFlag()
        self._set_address_str(address, int8(mem << 1 | c))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem << 1 | c) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem << 1 | c) # set zero flag

    def handleInstructionROLAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        final_address = format((int(address, 16) + self.x), '04x')

        mem = self._get_address_str(final_address)
        carry = 1 if (0b10000000 & mem) else 0
        c = self.flagController.getCarryFlag()
        self._set_address_str(final_address, int8(mem << 1 | c))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem << 1 | c) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem << 1 | c) # set zero flag

    ## ROR Instructions
    def handleInstructionRORAccumulator(self):
        carry = 1 if (0b00000001 & self.a) else 0
        c = self.flagController.getCarryFlag()
        self.a = self.a >> 1 | c * 128

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionRORZeroPage(self):
        address = self.get_next_byte()
        mem = self._get_address_str(address)
        carry = 1 if (0b00000001 & mem) else 0
        c = self.flagController.getCarryFlag()
        self._set_address_str(address, int8(mem >> 1 | c * 128))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem >> 1 | c * 128) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem >> 1 | c * 128) # set zero flag

    def handleInstructionRORZeroPageX(self):
        byte = self.get_next_byte()
        address = format((int(byte, 16) + self.x), '04x')
        mem = self._get_address_str(address)
        carry = 1 if (0b00000001 & mem) else 0
        c = self.flagController.getCarryFlag()
        self._set_address_str(address, int8(mem >> 1 | c * 128))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem >> 1 | c * 128) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem >> 1 | c * 128) # set zero flag

    def handleInstructionRORAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        mem = self._get_address_str(address)
        carry = 1 if (0b00000001 & mem) else 0
        c = self.flagController.getCarryFlag()
        self._set_address_str(address, int8(mem >> 1 | c * 128))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem >> 1 | c * 128) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem >> 1 | c * 128) # set zero flag

    def handleInstructionRORAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        final_address = format((int(address, 16) + self.x), '04x')

        mem = self._get_address_str(final_address)
        carry = 1 if (0b00000001 & mem) else 0
        c = self.flagController.getCarryFlag()
        self._set_address_str(final_address, int8(mem >> 1 | c * 128))

        self.flagController.setCarryFlag() if carry else self.flagController.clearCarryFlag()
        self.flagController.setNegativeIfNeeded(mem >> 1 | c * 128) # set negative flag
        self.flagController.setZeroFlagIfNeeded(mem >> 1 | c * 128) # set zero flag

    ## CMP Instructions
    def handleInstructionCMPImmediate(self):
        byte = self.get_next_byte()
        immediate = int(byte, 16)
        self.compare(immediate)

    def handleInstructionCMPZeroPage(self):
        address = self.get_next_byte()
        value = self._get_address_str(address)
        self.compare(value)

    def handleInstructionCMPZeroPageX(self):
        byte = self.get_next_byte()
        addressStart = int(byte, 16)
        address = (addressStart + self.x) & 0xFF
        value = self._get_address_int(address)
        self.compare(value)

    def handleInstructionCMPAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        value = self._get_address_str(address)
        self.compare(value)

    def handleInstructionCMPAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        final_address = format((int(address, 16) + self.x), '04x')

        mem = self._get_address_str(final_address)
        self.compare(mem)

    def handleInstructionCMPAbsoluteY(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        final_address = format((int(address, 16) + self.y), '04x')

        mem = self._get_address_str(final_address)
        self.compare(mem)

    def handleInstructionCMPIndirectX(self):
        byte = self.get_next_byte()

        address = format((int(byte, 16) + self.x), '04x')
        low_byte = format(self._get_address_str(address), '02x')
        high_byte = format(self._get_address_str(format((int(address, 16) + 1), '04x')), '02x')

        final_address = (high_byte + low_byte)

        value = self._get_address_str(final_address)
        self.compare(value)

    def handleInstructionCMPIndirectY(self):
        byte = self.get_next_byte()

        l_byte = format(self._get_address_str(byte), '02x')
        h_byte = format(self._get_address_int(int(byte, 16) + 1), '02x')

        address = (h_byte + l_byte)
        final_address = int(address, 16) + self.y

        value = self._get_address_int(final_address)
        self.compare(value)

    def compare(self, value):
        self.flagController.clearCarryFlag()
        result = self.a - value
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
        value = self._get_address_str(address)
        self.compareX(value)

    def handleInstructionCPXAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        value = self._get_address_str(address)
        self.compareX(value)

    def compareX(self, value):
        self.flagController.clearCarryFlag()
        result = self.x - value
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
        value = self._get_address_str(address)
        self.compareY(value)

    def handleInstructionCPYAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        value = self._get_address_str(address)
        self.compareY(value)

    def compareY(self, value):
        self.flagController.clearCarryFlag()
        result = self.y - value
        res = result & 0xFF                          # set a value limiting to one byte
        self.flagController.setNegativeIfNeeded(res) # set negative flag
        self.flagController.setZeroFlagIfNeeded(res) # set zero flag
        if result >= 0:
            self.flagController.setCarryFlag()

    ## Load Instructions
    def handleInstructionLDAImmediate(self):
        byte = self.get_next_byte()
        immediate = int(byte, 16)
        self.a = immediate
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionLDAZeroPage(self):
        address = self.get_next_byte()
        self.a = self._get_address_str(address)

        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionLDAZeroPageX(self):
        byte = self.get_next_byte()
        address = format((int(byte, 16) + self.x), '04x')
        self.a = self._get_address_str(address)

        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionLDAAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        self.a = self._get_address_str(address)

        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionLDAAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        final_address = format((int(address, 16) + self.x), '04x')

        self.a = self._get_address_str(final_address)

        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionLDAAbsoluteY(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        final_address = format((int(address, 16) + self.y), '04x')

        self.a = self._get_address_str(final_address)

        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionLDAIndirectX(self):
        byte = self.get_next_byte()

        address = format((int(byte, 16) + self.x), '04x')
        low_byte = format(self._get_address_str(address), '02x')
        high_byte = format(self._get_address_str(format((int(address, 16) + 1), '04x')), '02x')

        final_address = (high_byte + low_byte)

        self.a = self._get_address_str(final_address)

        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionLDAIndirectY(self):
        byte = self.get_next_byte()

        l_byte = format(self._get_address_str(byte), '02x')
        h_byte = format(self._get_address_int(int(byte, 16) + 1), '02x')

        address = (h_byte + l_byte)
        final_address = int(address, 16) + self.y

        self.a = self._get_address_int(final_address)

        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionLDXImmediate(self):
        print("Chegooooou")
        byte = self.get_next_byte()
        immediate = int(byte, 16)
        self.x = immediate
        self.flagController.setNegativeIfNeeded(self.x) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.x) # set zero flag

    def handleInstructionLDXZeroPage(self):
        address = self.get_next_byte()
        self.x = self._get_address_str(address)

        self.flagController.setNegativeIfNeeded(self.x) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.x) # set zero flag

    def handleInstructionLDXZeroPageY(self):
        byte = self.get_next_byte()
        address = format((int(byte, 16) + self.y), '04x')
        self.x = self._get_address_str(address)

        self.flagController.setNegativeIfNeeded(self.x) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.x) # set zero flag

    def handleInstructionLDXAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        self.x = self._get_address_str(address)

        self.flagController.setNegativeIfNeeded(self.x) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.x) # set zero flag

    def handleInstructionLDXAbsoluteY(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        final_address = format((int(address, 16) + self.y), '04x')

        self.x = self._get_address_str(final_address)

        self.flagController.setNegativeIfNeeded(self.x) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.x) # set zero flag

    def handleInstructionLDYImmediate(self):
        byte = self.get_next_byte()
        immediate = int(byte, 16)
        self.y = immediate
        self.flagController.setNegativeIfNeeded(self.y) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.y) # set zero flag

    def handleInstructionLDYZeroPage(self):
        address = self.get_next_byte()
        self.y = self._get_address_str(address)

        self.flagController.setNegativeIfNeeded(self.y) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.y) # set zero flag

    def handleInstructionLDYZeroPageX(self):
        byte = self.get_next_byte()
        address = format((int(byte, 16) + self.x), '04x')
        self.y = self._get_address_str(address)

        self.flagController.setNegativeIfNeeded(self.y) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.y) # set zero flag

    def handleInstructionLDYAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        self.y = self._get_address_str(address)

        self.flagController.setNegativeIfNeeded(self.y) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.y) # set zero flag

    def handleInstructionLDYAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        final_address = format((int(address, 16) + self.x), '04x')

        self.y = self._get_address_str(final_address)

        self.flagController.setNegativeIfNeeded(self.y) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.y) # set zero flag

    ## Store Instructions
    def handleInstructionSTXZeroPage(self):
        byte = self.get_next_byte()

        address = byte.zfill(4)
        self._set_address_str(address, self.x, set_address=True)

    def handleInstructionSTXZeroPageY(self):
        byte = self.get_next_byte()

        address = format((int(byte, 16) + self.y), '04x')
        self._set_address_str(address, self.x, set_address=True)

    def handleInstructionSTXAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)

        self._set_address_str(address, self.x, set_address=True)

    def handleInstructionSTYZeroPage(self):
        byte = self.get_next_byte()

        address = byte.zfill(4)
        self._set_address_str(address, self.y, set_address=True)

    def handleInstructionSTYZeroPageX(self):
        byte = self.get_next_byte()

        address = format((int(byte, 16) + self.x), '04x')
        self._set_address_str(address, self.y, set_address=True)

    def handleInstructionSTYAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)

        self._set_address_str(address, self.y, set_address=True)

    def handleInstructionSTAZeroPage(self):
        byte = self.get_next_byte()

        address = byte.zfill(4)
        self._set_address_str(address, self.a, set_address=True)

    def handleInstructionSTAZeroPageX(self):
        byte = self.get_next_byte()

        address = format((int(byte, 16) + self.x), '04x')
        self._set_address_str(address, self.a, set_address=True)

    def handleInstructionSTAAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)

        self._set_address_str(address, self.a, set_address=True)

    def handleInstructionSTAAbsoluteX(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        address = format((int(address, 16) + self.x), '04x')

        self._set_address_str(address, self.a, set_address=True)

    def handleInstructionSTAAbsoluteY(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        address = format((int(address, 16) + self.y), '04x')

        self._set_address_str(address, self.a, set_address=True)

    def handleInstructionSTAIndirectX(self):
        byte = self.get_next_byte()

        address = format((int(byte, 16) + self.x), '04x')
        low_byte = format(self._get_address_str(address), '02x')
        high_byte = format(self._get_address_str(format((int(address, 16) + 1), '04x')), '02x')

        address = (high_byte + low_byte)

        self._set_address_str(address, self.a, set_address=True)

    def handleInstructionSTAIndirectY(self):
        byte = self.get_next_byte()

        l_byte = format(self._get_address_str(byte), '02x')
        h_byte = format(self._get_address_int(int(byte, 16) + 1), '02x')

        lookup_address = (h_byte + l_byte)
        address = format(int(lookup_address, 16) + self.y, '04x')

        self._set_address_str(address, self.a, set_address=True)

    ## Jump Instructions
    def handleInstructionJmpAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)

        self.pc = int(address, 16)

    def handleInstructionJmpIndirect(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        l_byte = format(self._get_address_str(address), '02x')
        h_byte = format(self._get_address_int(int(address, 16) + 1), '02x')
        final_address = (h_byte + l_byte)

        self.pc = int(final_address, 16)

    ## Branch instructions
    def handleInstructionBPL(self):
        byte = int(self.get_next_byte(), 16)
        if self.flagController.getNegativeFlag() == 0:
            if 0b10000000 & byte:
                address = byte-(1<<8)
            else:
                address = byte

            self.cycles += 1
            self.pc = self.pc + address

    def handleInstructionBMI(self):
        byte = int(self.get_next_byte(), 16)
        if self.flagController.getNegativeFlag() == 1:
            if 0b10000000 & byte:
                address = byte-(1<<8)
            else:
                address = byte

            self.cycles += 1
            self.pc = self.pc + address

    def handleInstructionBVC(self):
        byte = int(self.get_next_byte(), 16)
        if self.flagController.getOverflowFlag() == 0:
            if 0b10000000 & byte:
                address = byte-(1<<8)
            else:
                address = byte

            self.cycles += 1
            self.pc = self.pc + address

    def handleInstructionBVS(self):
        byte = int(self.get_next_byte(), 16)
        if self.flagController.getOverflowFlag() == 1:
            if 0b10000000 & byte:
                address = byte-(1<<8)
            else:
                address = byte

            self.cycles += 1
            self.pc = self.pc + address

    def handleInstructionBCC(self):
        byte = int(self.get_next_byte(), 16)
        if self.flagController.getCarryFlag() == 0:
            if 0b10000000 & byte:
                address = byte-(1<<8)
            else:
                address = byte

            self.cycles += 1
            self.pc = self.pc + address

    def handleInstructionBCS(self):
        byte = int(self.get_next_byte(), 16)
        if self.flagController.getCarryFlag() == 1:
            if 0b10000000 & byte:
                address = byte-(1<<8)
            else:
                address = byte

            self.cycles += 1
            self.pc = self.pc + address

    def handleInstructionBNE(self):
        byte = int(self.get_next_byte(), 16)
        if self.flagController.getZeroFlag() == 0:
            if 0b10000000 & byte:
                address = byte-(1<<8)
            else:
                address = byte

            self.cycles += 1
            self.pc = self.pc + address

    def handleInstructionBEQ(self):
        byte = int(self.get_next_byte(), 16)
        if self.flagController.getZeroFlag() == 1:
            if 0b10000000 & byte:
                address = byte-(1<<8)
            else:
                address = byte

            self.cycles += 1
            self.pc = self.pc + address

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
        self.sp = self.x

    def handleInstructionTSX(self):
        self.x = self.sp
        self.flagController.setNegativeIfNeeded(self.x) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.x) # set zero flag

    def handleInstructionPHA(self):
        stackAddress = self.stack.getAddress() + (self.sp)
        self._set_address_int(stackAddress, self.a, set_address=True)
        self.sp = self.sp - 1

    def handleInstructionPLA(self):
        self.sp = self.sp + 1
        stackAddress = self.stack.getAddress() + (self.sp)
        self.a = self._get_address_int(stackAddress, set_address=True)
        self.flagController.setNegativeIfNeeded(self.a) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a) # set zero flag

    def handleInstructionPHP(self):
        P = self.flagController.getFlagsStatusByte()
        pToPush = int8(P | 0x30)                                  # 00110000
        stackAddress = self.stack.getAddress() + (self.sp)
        self._set_address_int(stackAddress, pToPush, set_address=True)
        self.sp = self.sp - 1

    def handleInstructionPLP(self):
        self.sp = self.sp + 1
        stackAddress = self.stack.getAddress() + (self.sp)
        P = self._get_address_int(stackAddress, set_address=True)
        pToSet = P & 0xEF
        self.flagController.setFlagsStatusByte(pToSet)

    # RTI Return from Interrupt
    def handleInstructionRTI(self):
        # Process Status World (flags)
        self.sp = self.sp + 1
        stackAddress = self.stack.getAddress() + (self.sp)
        P = self._get_address_int(stackAddress, set_address=True)
        pToSet = P & 0xEF
        self.flagController.setFlagsStatusByte(pToSet)
        # PC
        # get low byte
        self.sp = self.sp + 1
        stackAddress = self.stack.getAddress() + (self.sp)
        low_byte = format(self._get_address_int(stackAddress), '02x')

        # get high byte
        self.sp = self.sp + 1
        stackAddress = self.stack.getAddress() + (self.sp)
        high_byte = format(self._get_address_int(stackAddress), '02x')

        address = (high_byte + low_byte)
        self.pc = int(address, 16)

    # Subroutine Instructions
    def handleInstructionJSR(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)

        valueToPush = self.pc - 1

        pc_l = format(valueToPush, '04x')[2:4]
        pc_h = format(valueToPush, '04x')[0:2]

        self.pc = int(address, 16)

        stackAddress = self.stack.getAddress() + (self.sp)
        self._set_address_int(stackAddress, int8(int(pc_h, 16)))
        self.sp = self.sp - 1

        stackAddress = self.stack.getAddress() + (self.sp)
        self._set_address_int(stackAddress, int8(int(pc_l, 16)))
        self.sp = self.sp - 1

    def handleInstructionRTS(self):
        self.sp = self.sp + 1
        stackAddress = self.stack.getAddress() + (self.sp)
        low_byte = format(self._get_address_int(stackAddress), '02x')

        self.sp = self.sp + 1
        stackAddress = self.stack.getAddress() + (self.sp)
        high_byte = format(self._get_address_int(stackAddress), '02x')

        address = (high_byte + low_byte)
        self.pc = int(address, 16) + 1

    def handleInstructionNoOp(self):
        pass

    def handleInstructionBrk(self):
        self.pc = self.pc + 1

        pc_l = format(self.pc, '04x')[2:4]
        pc_h = format(self.pc, '04x')[0:2]

        self.flagController.setInterrupDisabledtFlag()

        # push PC to stack
        stackAddress = self.stack.getAddress() + (self.sp)
        self._set_address_int(stackAddress, int8(int(pc_h, 16)))
        self.sp = self.sp - 1

        stackAddress = self.stack.getAddress() + (self.sp)
        self._set_address_int(stackAddress, int8(int(pc_l, 16)))
        self.sp = self.sp - 1

        self.flagController.setBreakFlag()

        self.handleInstructionPHP()
        
        self.flagController.clearBreakFlag()

        # load IRQ pc value
        low_byte = self.Read(0xFFFE)
        high_byte = self.Read(0xFFFF)

        self.pc = (high_byte << 8) | low_byte