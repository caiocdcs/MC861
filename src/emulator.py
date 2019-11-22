from bus import *
import glfw
from OpenGL.GL import *
from view import *

class Emulator:
    def __init__(self, window):
        self.window = window
        self.view = None

    def start(self, path):
        if path:
            self.playGame(path)
            self.run()
        else:
            print("ROM Error...")

    def run(self):
        while not glfw.window_should_close(self.window):
            self.step()
            glfw.swap_buffers(self.window)
            glfw.poll_events()
        self.setView(None)

    def playGame(self, path):
        bus = Bus(path)
        self.setView(View(self, bus, path))

    def setView(self, view):
        self.view = view
        if self.view is not None:
            self.view.enter()
        self.timestamp = glfw.get_time()

    def setTitle(self, title):
        glfw.set_window_title(self.window, title)

    def step(self):
        glClear(GL_COLOR_BUFFER_BIT)
        if self.view is not None:
            self.view.update()
