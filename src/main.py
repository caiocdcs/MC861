import sys
import pyglet
from cpu import CPU
from window import Window

window = Window()

def main():

	# Check if there's a parameter
	if len(sys.argv) != 2:
		print ("Provide a .nes file\n")
		return

	window.set_size(1024, 960)
	pyglet.clock.schedule_interval(window.executeControllers, 0.1)
	pyglet.app.run()
	
	c = CPU(sys.argv[1])
	c.run()

if __name__ == "__main__":
	main()
