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
	cart = Cartridge()
	bus.insertCartridge(cart)
	

if __name__ == "__main__":
	main()
