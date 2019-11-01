import sys
import pyglet
from bus import BUS
from cpu import CPU
from ppu import PPU
from window import Window
from keyboard import Keyboard
from Cartridge import Cartridge 

def main():

	# Check if there's a parameter
	if len(sys.argv) != 2:
		print ("Provide a .nes file\n")
		return
	
	player1 = Keyboard()
	player2 = Keyboard()
	window = Window(player1, player2)
	window.set_size(256, 240)
	# window.set_size(768, 720)
	cpu = CPU()
	ppu = PPU(window)
	bus = BUS(cpu, ppu, player1, player2)
	cart = Cartridge(sys.argv[1])
	bus.insertCartridge(cart)
	
	cpu.connectBus(bus)

	# Do all init (load pallettes, background, set flags...) before running pyglet loop
	
	pyglet.clock.schedule_interval(bus.setFrame, 4)
	pyglet.app.run()
	

if __name__ == "__main__":
	main()
