import sys
import pyglet
from bus import BUS
from cpu import CPU
from ppu import PPU
from window import Window
from Cartridge import Cartridge 
from ctypes import c_uint16, c_uint8

def main():

	# Check if there's a parameter
	if len(sys.argv) != 2:
		print ("Provide a .nes file\n")
		return
	
	window = Window()
	window.set_size(256, 240)
	# window.set_size(768, 720)
	cpu = CPU()
	ppu = PPU(window)

	value = c_uint8(4)
	ppu.cpuWrite(0x0000, value)
	read = ppu.cpuRead(0x0000, False)
	print (read)
	# bus = BUS(cpu, ppu)
	# cart = Cartridge(sys.argv[1])
	# bus.insertCartridge(cart)
	
	# cpu.connectBus(bus)

	# # Do all init (load pallettes, background, set flags...) before running pyglet loop
	
	# pyglet.clock.schedule_interval(bus.setFrame, 1/60.0)
	# pyglet.app.run()
	

if __name__ == "__main__":
	main()
