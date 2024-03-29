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

def hexToBinary(hex):
	numberOfBits = 8
	binary = bin(hex)[2::].zfill(numberOfBits)
	return binary
