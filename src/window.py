import pyglet
from pyglet.window import key
from keyboard import Keyboard

class Window(pyglet.window.Window):

    def __init__(self):
        super(Window, self).__init__()
        self.keyboard = Keyboard()
        self.x = 500
        self.y = 500
        self.dx = 10
        self.dy = 10

    def readKeyboard(self):
        return self.keyboard.read()

    # this function is only for test
    def executeControllers(self, dt):
        if self.keyboard.read():
            print('The A key was pressed.')
        if self.keyboard.read():
            print('The B arrow key was pressed.')
        if self.keyboard.read():
            print('The space key was pressed.')
        if self.keyboard.read():
            print('The enter key was pressed.')
        if self.keyboard.read():
            print('The up arrow key was pressed.')
            self.y += 4
        if self.keyboard.read():
            print('The down arrow key was pressed.')
            self.y -= 4
        if self.keyboard.read():
            print('The left arrow key was pressed.')
            self.x -= 4
        if self.keyboard.read():
            print('The right arrow key was pressed.')
            self.x += 4
        self.keyboard.resetState()

    # Enter is start
    # Space is select
    def on_key_press(self, symbol, modifiers):
        if symbol == key.A:
            self.keyboard.aButtonPressed()
        elif symbol == key.B:
            self.keyboard.bButtonPressed()
        elif symbol == key.LEFT:
            self.keyboard.leftButtonPressed()
        elif symbol == key.RIGHT:
            self.keyboard.rightButtonPressed()
        elif symbol == key.UP:
            self.keyboard.upButtonPressed()
        elif symbol == key.DOWN:
            self.keyboard.downButtonPressed()
        elif symbol == key.ENTER:
            self.keyboard.startButtonPressed()
        elif symbol == key.SPACE:
            self.keyboard.selectButtonPressed()

    def on_draw(self):
        self.clear()
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2i', [self.x, self.y, self.x - self.dx, self.y, self.x - self.dx, self.y - self.dy, self.x, self.y - self.dy]))

