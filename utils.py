def log(a, x, y, sp, pc, p):
	print ("| pc = 0x" + str(pc), end=' ')
	print ("| a = 0x" + str(a), end=' ')
	print ("| x = 0x" + str(x), end=' ')
	print ("| y = 0x" + str(y), end=' ')
	print ("| sp = 0x" + str(sp), end=' ')
	print ("| p[NV-BDIZC] = ", end='')
	print (hexToBinary(p) + " |")

def logls(a, x, y, sp, pc, p, addr, data):
	print ("| pc = 0x" + str(pc), end=' ')
	print ("| a = 0x" + str(a), end=' ')
	print ("| x = 0x" + str(x), end=' ')
	print ("| y = 0x" + str(y), end=' ')
	print ("| sp = 0x" + str(sp), end=' ')
	print ("| p[NV-BDIZC] = ", end='')
	print (hexToBinary(p) + " |", end='')
	print ("| MEM[0x" + str(addr) + "] = 0x" + str(data) + " |")

def hexToBinary(hex):
	numberOfBits = 8
	binary = bin(hex)[2::].zfill(numberOfBits)
	return binary
