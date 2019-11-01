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

    def readKeyboardFromPlayer1(self):
        return self.player1.read()

    def movePixelDown(self):
        self.y -= 1

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

    # def on_draw(self):
    #     # self.clear()
    #     pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2i', [self.x, self.y, self.x - self.dx, self.y, self.x - self.dx, self.y - self.dy, self.x, self.y - self.dy]))

    def draw_pixel(self, x, y, rgb):
        pyglet.graphics.draw(1, pyglet.gl.GL_POINTS,('v2i', (x, y)), ('c3B', rgb))
