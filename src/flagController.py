from ctypes import c_uint8

class FlagController:
    def __init__(self):
        self.carryFlag = 0
        self.zeroFlag = 0
        self.interrupDisabledtFlag = 0
        self.decimalFlag = 0
        self.breakFlag = 0
        self.unusedFlag = 0
        self.overflowFlag = 0
        self.negativeFlag = 0

    def getFlagsStatusByte(self) -> c_uint8:
        flagsByte = 0
        flagsByte = flagsByte | (self.carryFlag << 0)
        flagsByte = flagsByte | (self.zeroFlag << 1)
        flagsByte = flagsByte | (self.interrupDisabledtFlag << 2)
        flagsByte = flagsByte | (self.decimalFlag << 3)
        flagsByte = flagsByte | (self.breakFlag << 4)
        flagsByte = flagsByte | (self.unusedFlag << 5)
        flagsByte = flagsByte | (self.overflowFlag << 6)
        flagsByte = flagsByte | (self.negativeFlag << 7)

        return flagsByte


    ############ Getters ############


    def getCarryFlag(self) -> int:
        return self.carryFlag

    def getZeroFlag(self) -> int:
        return self.zeroFlag
    
    def geInterrupDisabledtFlag(self) -> int:
        return self.interrupDisabledtFlag

    def getDecimalFlag(self) -> int:
        return self.decimalFlag

    def getBreakFlag(self) -> int:
        return self.breakFlag

    def getUnusedFlag(self) -> int:
        return self.unusedFlag

    def getOverflowFlag(self) -> int:
        return self.overflowFlag

    def getNegativeFlag(self) -> int:
        return self.negativeFlag


    ############ Setters ############


    def setCarryFlag(self):
        self.carryFlag = 1

    def setZeroFlag(self):
        self.zeroFlag = 1
    
    def setInterrupDisabledtFlag(self):
        self.interrupDisabledtFlag = 1

    def setDecimalFlag(self):
        self.decimalFlag = 1

    def setBreakFlag(self):
        self.breakFlag = 1

    def setUnusedFlag(self):
        self.unusedFlag = 1

    def setOverflowFlag(self):
        self.overflowFlag = 1

    def setNegativeFlag(self):
        self.negativeFlag = 1


    ############ Clear Flags ############


    def clearCarryFlag(self):
        self.carryFlag = 0

    def clearZeroFlag(self):
        self.zeroFlag = 0
    
    def clearInterrupDisabledtFlag(self):
        self.interrupDisabledtFlag = 0

    def clearDecimalFlag(self):
        self.decimalFlag = 0

    def clearBreakFlag(self):
        self.breakFlag = 0

    def clearUnusedFlag(self):
        self.unusedFlag = 0

    def clearOverflowFlag(self):
        self.overflowFlag = 0

    def clearNegativeFlag(self):
        self.negativeFlag = 0

    ############ Setters with logic ############

    def setZeroFlagIfNeeded(self, value):
        if value == 0:
            self.zeroFlag = 1
        else:
            self.zeroFlag = 0
        
    def setNegativeIfNeeded(self, value):
        if value & 0x80 != 0:
            self.negativeFlag = 1
        else:
            self.negativeFlag = 0

    def setCarryFlagIfNeeded(self, value):
        # set carry flag
        if value > 0xFF:
            self.setCarryFlag()
        else:
            self.clearCarryFlag()
       