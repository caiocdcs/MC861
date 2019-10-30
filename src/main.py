import sys
from bus import BUS
from cpu import CPU
from ppu import PPU
from cartridge import Cartridge 

def main():

	# Check if there's a parameter
	if len(sys.argv) != 2:
		print ("Provide a .nes file\n")
		return
	
	cpu = CPU(sys.argv[1])
	ppu = PPU()
	bus = BUS(cpu, ppu)
	cart = Cartridge(sys.argv[1])
	bus.insertCartridge(cart)

	print(bus.cpuRead(0x8888, False))
	

if __name__ == "__main__":
	main()
