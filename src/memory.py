from numpy import uint8, uint16, uint32, uint64
import numpy as np

uint8 = uint8
uint16 = uint16
uint32 = uint32
uint64 = uint64

MirrorHorizontal = 0
MirrorVertical = 1
MirrorSingle0 = 2
MirrorSingle1 = 3
MirrorFour = 4

MirrorLookup = [[0, 0, 1, 1], [0, 1, 0, 1], [0, 0, 0, 0], [1, 1, 1, 1], [0, 1, 2, 3]]

def MirrorAddress(mode, address):
    address = ((address - 0x2000) & 0xFFFF) & 0x0FFF
    table = (address >> 10)
    offset = address & 0x03FF
    return (0x2000 + (MirrorLookup[uint8(mode)][table] << 10) + offset) & 0xFFFF
