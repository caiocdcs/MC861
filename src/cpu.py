from utils import log, logls
from ctypes import c_uint16, c_uint8
from memory import Memory
from flagController import FlagController
from stack import Stack

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
        self.stack = Stack()
    
    def log(self, address = None):
        if (address):
            p = self.flagController.getFlagsStatusByte()
            logls(self.a.value, self.x.value, self.y.value, self.sp.value, ceil(self.pc.value / 2), p, address, self.memory.get_memory_at_position_str(address).value)
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

    # FIXME
    def handleInstructionAndZeroPageX(self):
        byte = self.get_next_byte()
        addressStart = int(byte, 16)
        address = (addressStart + self.x.value) & 0xFF
        value = self.memory.get_memory_at_position_int(address).value
        self.a.value = value & self.a.value
        self.flagController.setNegativeIfNeeded(self.a.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.a.value) # set zero flag

    ## INC Instructions
    def handleInstructionINX(self):
        self.x.value = self.x.value + 1
        self.flagController.setNegativeIfNeeded(self.x.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.x.value) # set zero flag


    def handleInstructionINY(self):
        self.y.value = self.y.value + 1
        self.flagController.setNegativeIfNeeded(self.y.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.y.value) # set zero flag


    ## DEC Instructions
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

    ## Load Instructions
    def handleInstructionLDAImmediate(self):
        byte = self.get_next_byte()
        immediate = int(byte, 16)
        self.a.value = immediate
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
        value = self.memory.get_memory_at_position_str(address)
        self.x.value = value.value
        self.flagController.setNegativeIfNeeded(self.x.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.x.value) # set zero flag

    def handleInstructionLDYImmediate(self):
        byte = self.get_next_byte()
        immediate = int(byte, 16)
        self.y.value = immediate
        self.flagController.setNegativeIfNeeded(self.y.value) # set negative flag
        self.flagController.setZeroFlagIfNeeded(self.y.value) # set zero flag

    ## Store Instructions
    def handleInstructionSTXZeroPage(self):
        byte = self.get_next_byte()
        self.memory.set_memory_at_position_str(byte, self.x)

    def handleInstructionSTXZeroPageY(self):
        byte = self.get_next_byte()

        address = format((int(byte, 16) + self.y.value), '04x')
        self.memory.set_memory_at_position_str(address, self.x)
        self.log(address)

    def handleInstructionSTXAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)

        self.memory.set_memory_at_position_str(address, self.x)

    def handleInstructionSTYZeroPage(self):
        byte = self.get_next_byte()
        self.memory.set_memory_at_position_str(byte, self.y)

    def handleInstructionSTYZeroPageY(self):
        byte = self.get_next_byte()

        address = format((int(byte, 16) + self.x.value), '04x')
        self.memory.set_memory_at_position_str(address, self.y)

    def handleInstructionSTYAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)

        self.memory.set_memory_at_position_str(address, self.y)

    ## Jump Instructions
    def handleInstructionJmpAbsolute(self):
        low_byte = self.get_next_byte()
        high_byte = self.get_next_byte()

        address = (high_byte + low_byte)
        self.pc.value = int(address, 16) * 2

    def handleInstructionJmpIndirect(self):
        byte = self.get_next_byte()
        byte_h = str(int(byte, 16) + 1)
        
        low_byte = str(self.memory.get_memory_at_position_str(byte))
        high_byte = str(self.memory.get_memory_at_position_str(byte_h))

        address = (high_byte + low_byte)
        self.pc.value = int(address, 16) * 2

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

    def handleInstructionSTX(self):
        self.x.value = self.sp.value

    def handleInstructionPHA(self):
        stackAddress = self.stack.getAddress() + (self.sp.value * 8)
        self.memory.set_memory_at_position_int(stackAddress, self.a.value)
        self.sp.value = self.sp.value + 1

    def handleInstructionPLA(self):
        self.sp.value = self.sp.value - 1
        stackAddress = self.stack.getAddress() + (self.sp.value * 8)
        self.a.value = self.memory.get_memory_at_position_int(stackAddress)

    def handleInstructionPHP(self):
        # self.a.value = self.flagController.getFlagsStatusByte() #TODO
        print('TODO')

    def handleInstructionPLP(self):
        # self.flagController.setFlagsStatusByte() # TODO undestand where to get from
        print('TODO')

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

            # LDX Zero Page
            elif instruction == 'A6':
                self.handleInstructionLDXZeroPage()

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
            elif instruction == '84':
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

            # ADC Immediate
            elif instruction == '69':
                self.handleInstructionAdcImmediate()

            # ADC Zero Page
            elif instruction == '65':
                self.handleInstructionAdcZeroPage()

            # ADC Zero Page X
            elif instruction == '75':
                self.handleInstructionAdcZeroPageX()

            # # ADC Absolute
            # elif instruction == '6D':
            #     self.handleInstructionAdcAbsolute()

            # # ADC Absolute X
            # elif instruction == '7D':
            #     self.handleInstructionAdcAbsoluteX()

            # # ADC Absolute Y
            # elif instruction == '79':
            #     self.handleInstructionAdcAbsoluteY()

            # # ADC Indirect X
            # elif instruction == '61':
            #     self.handleInstructionAdcIndirectX()

            # # ADC Indirect Y
            # elif instruction == '71':
            #     self.handleInstructionAdcIndirectY()

            # AND Immediante
            elif instruction == '29':
                self.handleInstructionAndImmediate()

            # AND Zero Page
            elif instruction == '25':
                self.handleInstructionAndZeroPage()

            # AND Zero Page X
            elif instruction == '35':
                self.handleInstructionAndZeroPageX()

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

            self.log()
            instruction = self.get_next_byte()