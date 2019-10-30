import sys
from bus import BUS
from cpu import CPU
from ppu import PPU

def main():

	# Check if there's a parameter
	if len(sys.argv) != 2:
		print ("Provide a .nes file\n")
		return
	
	cpu = CPU(sys.argv[1])
	ppu = PPU()
	bus = BUS(cpu, ppu)
	bus.cpuRead(0x1234)
	

if __name__ == "__main__":
	main()
