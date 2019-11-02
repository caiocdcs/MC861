import sys
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
	# if len(sys.argv) != 2:
	# 	print ("Provide a .nes file\n")
	# 	return
	
	player1 = Keyboard()
	player2 = Keyboard()

	cpu = CPU()
	ppu = PPU()
	bus = BUS(cpu, ppu, player1, player2)
	cart = Cartridge("hangman/controllers.nes")
	bus.insertCartridge(cart)
	
	cpu.connectBus(bus)

	bus.reset()

	done = False

	pygame.init()
	screen = pygame.display.set_mode((400, 300))
	clock = pygame.time.Clock()
	while done == False:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				done = True

			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_a:
					player1.pressAButton()
				if event.key == pygame.K_b:
					player1.pressBButton()
				if event.key == pygame.K_SPACE:
					player1.pressSelectButton()
				if event.key == pygame.K_RETURN:
					player1.pressStartButton()
				if event.key == pygame.K_UP:
					player1.pressUpButton()
				if event.key == pygame.K_LEFT:
					player1.pressLeftButton()
				if event.key == pygame.K_RIGHT:
					player1.pressRightButton()
				if event.key == pygame.K_DOWN:
					player1.pressDownButton()
		# pygame.draw.rect(screen, (0, 128, 255), pygame.Rect(30, 30, 60, 60))
		pygame.display.flip()
		clock.tick(60)
		bus.setFrame()
		

		# events = pygame.event.get()
		# for event in events:
		# 	if event.key == pygame.K_a:
		# 		print("adsa")
	

if __name__ == "__main__":
	main()
