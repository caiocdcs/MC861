def log(a, x, y, sp, pc, p):
	print ("| pc = 0x" + str(pc).zfill(4), end=' ')
	print ("| a = 0x" + str(a).zfill(2), end=' ')
	print ("| x = 0x" + str(x).zfill(2), end=' ')
	print ("| y = 0x" + str(y).zfill(2), end=' ')
	print ("| sp = 0x" + str(sp).zfill(4), end=' ')
	print ("| p[NV-BDIZC] = ", end='')
	print (hexToBinary(p) + " |")

def logls(a, x, y, sp, pc, p, addr, data):
	print ("| pc = 0x" + str(pc).zfill(4), end=' ')
	print ("| a = 0x" + str(a).zfill(2), end=' ')
	print ("| x = 0x" + str(x).zfill(2), end=' ')
	print ("| y = 0x" + str(y).zfill(2), end=' ')
	print ("| sp = 0x" + str(sp).zfill(4), end=' ')
	print ("| p[NV-BDIZC] = ", end='')
	print (hexToBinary(p) + " ", end='')
	print ("| MEM[0x" + str(addr).zfill(4) + "] = 0x" + str(data).zfill(2) + " |")

def hexToBinary(hex):
	numberOfBits = 8
	binary = bin(hex)[2::].zfill(numberOfBits)
	return binary
