import sys
# import pyglet
from bus import BUS
from cpu import CPU
from ppu import PPU
from window import Window
from keyboard import Keyboard
from Cartridge import Cartridge
import pygame

int8 = int

def main():

	# Check if there's a parameter
	if len(sys.argv) != 2:
		print ("Provide a .nes file\n")
		return
	
	player1 = Keyboard()
	player2 = Keyboard()

	cpu = CPU()
	ppu = PPU()
	bus = BUS(cpu, ppu, player1, player2)
	cart = Cartridge(sys.argv[1])
	bus.insertCartridge(cart)
	
	cpu.connectBus(bus)

	bus.reset()

	pygame.init()
	clock = pygame.time.Clock()
	while 1:
		clock.tick(60)
		bus.setFrame()

		# events = pygame.event.get()
		# for event in events:
		# 	if event.key == pygame.K_a:
		# 		print("adsa")
	

if __name__ == "__main__":
	main()
