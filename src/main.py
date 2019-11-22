import sys
import glfw
from OpenGL.GL import *
from emulator import *


def main():

	if len(sys.argv) != 2:
		print("Provide a .nes file\n")
		return
	
	if not glfw.init():
		raise RuntimeError("GLFW Init Error")

	title = "bus"
	scale = 3

	window = glfw.create_window(256 * 3, 240 * scale, title, None, None)
	glfw.make_context_current(window)

	emulator = Emulator(window)
	emulator.start(sys.argv[1])
	glEnable(GL_TEXTURE_2D)


if __name__ == "__main__":
	main()
