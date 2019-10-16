import sys
import pyglet
from cpu import CPU
from window import Window

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

def main():

	# Check if there's a parameter
	if len(sys.argv) != 2:
		print ("Provide a .nes file\n")
		return

	window = Window()
	window.set_size(1280, 720)
	
	pyglet.app.run()
	window.drawSquare(100, 100, 50, 50)

	c = CPU(sys.argv[1])
	c.run()


if __name__ == "__main__":
	main()
