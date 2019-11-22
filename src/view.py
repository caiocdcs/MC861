from OpenGL.GL import *
import glfw
from controller import *

class View:

    def __init__(self, emulator, bus, title):
        self.emulator = emulator
        self.bus = bus
        self.title = title
        self.texture = self.createTexture()
        self.record = False
        self.frames = None

    def enter(self):
        glClearColor(0, 0, 0, 1)
        glEnable(GL_TEXTURE_2D)
        glfw.set_key_callback(self.emulator.window, self.onKey)

        self.bus.reset()

    def exit(self):
        pass

    def update(self):
        dt = 0.01
        window = self.emulator.window
        bus = self.bus
        # Joystick and key and controller
        self.updateControllers(window, bus)
        bus.stepSeconds(dt)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        self.setTexture(bus.buffer())
        self.drawBuffer(window)
        glBindTexture(GL_TEXTURE_2D, 0)

    def onKey(self, window, key, scancode, action, mods):
        pass

    def createTexture(self):
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glBindTexture(GL_TEXTURE_2D, 0)
        return texture

    def setTexture(self, im):
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 256, 240, 0, GL_RGB, GL_UNSIGNED_BYTE, bytes(im))

    def drawBuffer(self, window):
        w, h = glfw.get_framebuffer_size(window)
        s1 = float(w) / 256
        s2 = float(h) / 240
        padding = 0.0
        f = 1.0 - padding
        if s1 >= s2:
            x = f * s2 / s1
            y = f
        else:
            x = f
            y = f * s1 / s2
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1)
        glVertex2f(-x, -y)
        glTexCoord2f(1, 1)
        glVertex2f(x, -y)
        glTexCoord2f(1, 0)
        glVertex2f(x, y)
        glTexCoord2f(0, 0)
        glVertex2f(-x, y)
        glEnd()

    def updateControllers(self, window, bus):
        turbo = (bus.PPU.Frame % 6) < 3
        k1 = self.readKeys(window, turbo)
        j1 = self.readJoystick(glfw.JOYSTICK_1, turbo)
        j2 = self.readJoystick(glfw.JOYSTICK_2, turbo)
        bus.setButtons1(self.combineButtons(k1, j1))
        bus.setButtons2(j2)

    def readKey(self, window, key):
        return glfw.get_key(window, key) == glfw.PRESS

    def readKeys(self, window, turbo):
        result = [False for _ in range(8)]
        result[ButtonA] = self.readKey(window, glfw.KEY_Z) or (turbo and self.readKey(window, glfw.KEY_A))
        result[ButtonB] = self.readKey(window, glfw.KEY_X) or (turbo and self.readKey(window, glfw.KEY_S))
        result[ButtonSelect] = self.readKey(window, glfw.KEY_RIGHT_SHIFT)
        result[ButtonStart] = self.readKey(window, glfw.KEY_ENTER)
        result[ButtonUp] = self.readKey(window, glfw.KEY_UP)
        result[ButtonDown] = self.readKey(window, glfw.KEY_DOWN)
        result[ButtonLeft] = self.readKey(window, glfw.KEY_LEFT)
        result[ButtonRight] = self.readKey(window, glfw.KEY_RIGHT)
        return result

    def readJoystick(self, joy, turbo):
        result = [False for _ in range(8)]
        return result

    def combineButtons(self, a, b):
        result = [False for _ in range(8)]
        for i in range(8):
            result[i] = a[i] or b[i]
        return result