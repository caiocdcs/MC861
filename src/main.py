import sys
from bus import BUS
from cpu import CPU
from ppu import PPU
# from keyboard import Keyboard
# from Cartridge import Cartridge
import pygame

import glfw
from OpenGL.GL import *
from director import *

def main():

	# Check if there's a parameter
	if len(sys.argv) != 2:
		print ("Provide a .nes file\n")
		return
	
	# player1 = Keyboard()
	# player2 = Keyboard()

	# cpu = CPU()
	# ppu = PPU()
	# bus = BUS(cpu, ppu, player1, player2)
	# cart = Cartridge(sys.argv[1])
	# #cart = Cartridge("hangman/hanging.nes")
	# bus.insertCartridge(cart)
	
	# cpu.connectBus(bus)

	# bus.reset()

	if not glfw.init():
		raise RuntimeError("GLFW Init Error")

	title = "Emulator"
	width  = 256
	height = 240
	scale  = 3

	window = glfw.create_window(width * scale, height * scale, title, None, None)
	glfw.make_context_current(window)

	director = NewDirector(window)
	director.Start(sys.argv[1])
	glEnable(GL_TEXTURE_2D)

	done = False
	# pygame.init()
	# screen = pygame.display.set_mode((256, 240))
	# clock = pygame.time.Clock()
	# while done == False:
	# 	for event in pygame.event.get():
	# 		if event.type == pygame.QUIT:
	# 			done = True

	# 		elif event.type == pygame.KEYDOWN:
	# 			if event.key == pygame.K_UP:
	# 				player1.pressUpButton()
	# 			if event.key == pygame.K_LEFT:
	# 				player1.pressLeftButton()
	# 			if event.key == pygame.K_RIGHT:
	# 				player1.pressRightButton()
	# 			if event.key == pygame.K_DOWN:
	# 				player1.pressDownButton()
	# 	# pygame.draw.rect(screen, (0, 128, 255), pygame.Rect(30, 30, 60, 60))
	# 	pygame.display.flip()
	# 	clock.tick(60)
	# 	bus.setFrame()

if __name__ == "__main__":
	main()
