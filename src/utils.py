def log(a, x, y, sp, pc, p):
	print ("| pc = " + str.format('0x{:04x}', int(hex(pc), 16)), end=' ')
	print ("| a = " + str.format('0x{:02x}', int(hex(a), 16)), end=' ')
	print ("| x = " + str.format('0x{:02x}', int(hex(x), 16)), end=' ')
	print ("| y = " + str.format('0x{:02x}', int(hex(y), 16)), end=' ')
	print ("| sp = " + str.format('0x{:04x}', int(hex(sp), 16)), end=' ')
	print ("| p[NV-BDIZC] = ", end='')
	print (hexToBinary(p) + " |")

def logls(a, x, y, sp, pc, p, addr, data):
	print ("| pc = " + str.format('0x{:04x}', int(hex(pc), 16)), end=' ')
	print ("| a = " + str.format('0x{:02x}', int(hex(a), 16)), end=' ')
	print ("| x = " + str.format('0x{:02x}', int(hex(x), 16)), end=' ')
	print ("| y = " + str.format('0x{:02x}', int(hex(y), 16)), end=' ')
	print ("| sp = " + str.format('0x{:04x}', int(hex(sp), 16)), end=' ')
	print ("| p[NV-BDIZC] = ", end='')
	print (hexToBinary(p) + " ", end='')
	print ("| MEM[0x" + str(addr).zfill(4) + "] = " + str.format('0x{:02x}', int(hex(data), 16))+ " |")

def log_ppu(cycle, scanline, status, mask, control, loopy):
	print ("| cycle = " + str.format('{:d}', cycle), end=' ')
	print ("| scanline = " + str.format('{:d}', scanline), end=' ')
	print ("| status = " + str.format('0b{:08b}', status.readStatus()), end=' ')
	print ("| mask = " + str.format('0b{:08b}', mask.readMask()), end=' ')
	print ("| control = " + str.format('0b{:08b}', control.readControl()), end=' ')
	print ("| loopy = " + str.format('0b{:08b}', loopy.readLoopy()), end=' |')
	print("\n")

def hexToBinary(hex):
	numberOfBits = 8
	binary = bin(hex)[2::].zfill(numberOfBits)
	return binary
