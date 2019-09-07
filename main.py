import sys
from ctypes import *

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

def getInstruction(contentHex, pc):
	begin = pc
	end = pc + 2
	byte = contentHex[begin:end].upper()
	return byte

def main():

	# Initialize 
	p = c_uint16(0)
	sp = c_uint16(0)
	pc = c_uint16(0)
	a = c_uint8(0)
	x = c_uint8(0)
	y = c_uint8(0)
	addr = c_uint16(0)
	data = c_uint8(0)

	if (len(sys.argv) != 2):
		print ("Provide a .nes file\n")
		return

	file = open(sys.argv[1], "rb")
	contentHex = file.read().hex() 

	byte = getInstruction(contentHex, pc.value)

	while byte:
	#	log(a.value, x.value, y.value, sp.value, pc.value, p.value)
		logls(a.value, x.value, y.value, sp.value, pc.value, p.value, addr.value, data.value)

		# LDA
		if byte == 'A9':
			print ("instruction: " + byte)

		# LDX
		elif byte == 'A2':
			print ("instruction: " + byte)

		# INX
		elif byte == 'E8':
			print ("instruction: " + byte)
		
		pc.value = pc.value + 2
		byte = getInstruction(contentHex, pc.value)

if __name__ == "__main__":
    main()
