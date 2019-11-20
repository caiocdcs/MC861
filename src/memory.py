from defines import *

MirrorHorizontal = 0
MirrorVertical = 1
MirrorSingle0 = 2
MirrorSingle1 = 3
MirrorFour = 4

MirrorLookup = [[0, 0, 1, 1], [0, 1, 0, 1], [0, 0, 0, 0],[1, 1, 1, 1], [0, 1, 2, 3]]

def MirrorAddress(mode, address):
    address = ((address - 0x2000) & 0xFFFF) & 0x0FFF
    table = (address >> 10)#// 0x0400
    offset = address & 0x03FF#% 0x0400
    return (0x2000 + (MirrorLookup[uint8(mode)][table] << 10) + offset) & 0xFFFF
