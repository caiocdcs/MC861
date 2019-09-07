import sys
from ctypes import *

####################################################
###############      INITIALIZE      ###############
####################################################


p = c_uint16(0)
sp = c_uint16(0)
pc = c_uint16(0)
a = c_uint8(0)
x = c_uint8(0)
y = c_uint8(0)
addr = c_uint16(0)
data = c_uint8(0)


####################################################
##################      LOGS      ##################
####################################################


def log():
	print ("| pc = 0x" + str(pc.value), end=' ')
	print ("| a = 0x" + str(a.value), end=' ')
	print ("| x = 0x" + str(x.value), end=' ')
	print ("| y = 0x" + str(y.value), end=' ')
	print ("| sp = 0x" + str(sp.value), end=' ')
	print ("| p[NV-BDIZC] = ", end='')
	print (hexToBinary(p.value) + " |")

def logls():
	print ("| pc = 0x" + str(pc.value), end=' ')
	print ("| a = 0x" + str(a.value), end=' ')
	print ("| x = 0x" + str(x.value), end=' ')
	print ("| y = 0x" + str(y.value), end=' ')
	print ("| sp = 0x" + str(sp.value), end=' ')
	print ("| p[NV-BDIZC] = ", end='')
	print (hexToBinary(p.value) + " |", end='')
	print ("| MEM[0x" + str(addr.value) + "] = 0x" + str(data.value) + " |")


####################################################
##########      AUXIALIARY FUNCTIONS      ##########
####################################################


def hexToBinary(hex):
	numberOfBits = 8
	binary = bin(hex)[2::].zfill(numberOfBits)
	return binary

def getNextByte(contentHex):
	# log()
	logls()

	begin = pc.value
	pc.value = pc.value + 2
	end = pc.value
	byte = contentHex[begin:end].upper()
	
	return byte

####################################################
##########      INSTRUCTION HANDLERS      ##########
####################################################

def handleInstructionINX(contentHex):
	x.value = x.value + 1

def handleInstructionLDAImmediate(contentHex):
	byte = getNextByte(contentHex)
	immediate = int(byte, 16)
	a.value = immediate

def handleInstructionLDXImmediate(contentHex):
	byte = getNextByte(contentHex)
	immediate = int(byte, 16)
	x.value = immediate

def main():

	# Check if there's a parameter
	if (len(sys.argv) != 2):
		print ("Provide a .nes file\n")
		return

	file = open(sys.argv[1], "rb")
	contentHex = file.read().hex() # convert binary file on a hex string

	
	byte = getNextByte(contentHex)

	while byte:

		# LDA Immediate
		if byte == 'A9':
			print ("instruction: " + byte)
			handleInstructionLDAImmediate(contentHex)

		# LDX Immediate
		elif byte == 'A2':
			print ("instruction: " + byte)
			handleInstructionLDXImmediate(contentHex)

		# INX
		elif byte == 'E8':
			print ("instruction: " + byte)
			handleInstructionINX(contentHex)
		
		byte = getNextByte(contentHex)

if __name__ == "__main__":
    main()
