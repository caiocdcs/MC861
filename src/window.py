import pyglet
from pyglet.window import key
from keyboard import Keyboard

class Window(pyglet.window.Window):

    def __init__(self):
        super(Window, self).__init__()
        self.player1 = Keyboard()
        self.player2 = Keyboard()
        self.x = 128
        self.y = 120
        self.dx = 1
        self.dy = 1
        self.color = {
            0x00: (84, 84, 84),
            0x01: (0, 30, 116),
            0x02: (8, 16, 144),
            0x03: (48, 0, 136),
            0x04: (68, 0, 100),
            0x05: (92, 0, 48),
            0x06: (84, 4, 0),
            0x07: (60, 24, 0),
            0x08: (32, 42, 0),
            0x09: (8, 58, 0),
            0x0A: (0, 64, 0),
            0x0B: (0, 60, 0),
            0x0C: (0, 50, 60),
            0x0D: (0, 0, 0),
            0x0E: (0, 0, 0),
            0x0F: (0, 0, 0),

            0x10: (152, 150, 152),
            0x11: (8, 76, 196),
            0x12: (48, 50, 236),
            0x13: (92, 30, 228),
            0x14: (136, 20, 176),
            0x15: (160, 20, 100),
            0x16: (152, 34, 32),
            0x17: (120, 60, 0),
            0x18: (84, 90, 0),
            0x19: (40, 114, 0),
            0x1A: (8, 124, 0),
            0x1B: (0, 118, 40),
            0x1C: (0, 102, 120),
            0x1D: (0, 0, 0),
            0x1E: (0, 0, 0),
            0x1F: (0, 0, 0),

            0x20: (236, 238, 236),
            0x21: (76, 154, 236),
            0x22: (120, 124, 236),
            0x23: (176, 98, 236),
            0x24: (228, 84, 236),
            0x25: (236, 88, 180),
            0x26: (236, 106, 100),
            0x27: (212, 136, 32),
            0x28: (160, 170, 0),
            0x29: (116, 196, 0),
            0x2A: (76, 208, 32),
            0x2B: (56, 204, 108),
            0x2C: (56, 180, 204),
            0x2D: (60, 60, 60),
            0x2E: (0, 0, 0),
            0x2F: (0, 0, 0),

            0x30: (236, 238, 236),
            0x31: (168, 204, 236),
            0x32: (188, 188, 236),
            0x33: (212, 178, 236),
            0x34: (236, 174, 236),
            0x35: (236, 174, 212),
            0x36: (236, 180, 176),
            0x37: (228, 196, 144),
            0x38: (204, 210, 120),
            0x39: (180, 222, 120),
            0x3A: (168, 226, 144),
            0x3B: (152, 226, 180),
            0x3C: (160, 214, 228),
            0x3D: (160, 162, 160),
            0x3E: (0, 0, 0),
            0x3F: (0, 0, 0)
        }

    def readKeyboardFromPlayer1(self):
        return self.player1.read()

    # this function is only for test
    def executeControllers(self, dt):
        if self.player1.read():
            print('The A key was pressed.')
        if self.player1.read():
            print('The B arrow key was pressed.')
        if self.player1.read():
            print('The space key was pressed.')
        if self.player1.read():
            print('The enter key was pressed.')
        if self.player1.read():
            print('The up arrow key was pressed.')
            self.y += 1
        if self.player1.read():
            print('The down arrow key was pressed.')
            self.y -= 1
        if self.player1.read():
            print('The left arrow key was pressed.')
            self.x -= 1
        if self.player1.read():
            print('The right arrow key was pressed.')
            self.x += 1

    # Enter is start
    # Space is select
    def on_key_press(self, symbol, modifiers):
        if symbol == key.A:
            self.player1.aButtonPressed()
        elif symbol == key.B:
            self.player1.bButtonPressed()
        elif symbol == key.LEFT:
            self.player1.leftButtonPressed()
        elif symbol == key.RIGHT:
            self.player1.rightButtonPressed()
        elif symbol == key.UP:
            self.player1.upButtonPressed()
        elif symbol == key.DOWN:
            self.player1.downButtonPressed()
        elif symbol == key.ENTER:
            self.player1.startButtonPressed()
        elif symbol == key.SPACE:
            self.player1.selectButtonPressed()

    def on_draw(self):
        self.clear()
        # pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2i', [self.x, self.y, self.x - self.dx, self.y, self.x - self.dx, self.y - self.dy, self.x, self.y - self.dy]))
        self.update_graphics()

    def update_graphics(self):
        # TODO: get 4 byte sprite where (Y, tile, junk, X)
        # TODO: get TILE for drawing from .chr sprites file (at most 255/6 or 0xFE/F offset)
        # w, h = 256, 240
        # rgb = (255, 255, 255)
        color = 0x20
        rgb = self.color[color]
        pyglet.graphics.draw(1, pyglet.gl.GL_POINTS,('v2i', (self.x, self.y)), ('c3B', rgb))
        # TODO: Pass correct byte array, located from TILE (for example, 16 bytes which should be 0, 1, 2, 3, 0, 1, 2, 3; being 8 of each)
        b = [0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        self.draw_sprite(10, 10, b)
    
    def draw_sprite(self, x, y, byteArray):
        # byteArray must be a value of 16 bytes, which represents the sprite
        # for each bit, the color is decided by n and n+8 bit, which means de first 8 bytes are the LSB and the following 8 the MSB
        # therefore we can make the following calculation for converting it to a single array
        res = []
        for i in range(64):
            res.append(byteArray[i] + (byteArray[i + 64]) * 2)
        # print(res)
        for j in range(8):
            for i in range(8):
                # TODO: based on JUNK and Pallete (Pattern) Table, get correct color to display
                if (byteArray[j * 8 + i]) == 0:
                    rgb = self.color[0x0D]
                else:
                    rgb = self.color[0x20]
                pyglet.graphics.draw(1, pyglet.gl.GL_POINTS,('v2i', (x + i, y + j)), ('c3B', rgb))