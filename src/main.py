import sys
import pyglet
from cpu import CPU
from window import Window

def main():

	# Check if there's a parameter
	if len(sys.argv) != 2:
		print ("Provide a .nes file\n")
		return

	window = Window()
	pyglet.app.run()
	c = CPU(sys.argv[1])
	c.run()


if __name__ == "__main__":
	main()
