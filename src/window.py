import pyglet
from pyglet.window import key
from controllers import Controllers

class Window(pyglet.window.Window):

    def __init__(self):
        super(Window, self).__init__()
        self.controllers = Controllers()
        self.x = 500
        self.y = 500
        self.dx = 10
        self.dy = 10

    # this function is only for test
    def executeControllers(self, dt):
        if self.controllers.read():
            print('The A key was pressed.')
        if self.controllers.read():
            print('The B arrow key was pressed.')
        if self.controllers.read():
            print('The space key was pressed.')
        if self.controllers.read():
            print('The enter key was pressed.')
        if self.controllers.read():
            print('The up arrow key was pressed.')
            self.y += 4
        if self.controllers.read():
            print('The down arrow key was pressed.')
            self.y -= 4
        if self.controllers.read():
            print('The left arrow key was pressed.')
            self.x -= 4
        if self.controllers.read():
            print('The right arrow key was pressed.')
            self.x += 4
        self.controllers.resetControllers()

    # Enter is start
    # Space is select
    def on_key_press(self, symbol, modifiers):
        if symbol == key.A:
            self.controllers.aButtonPressed()
        elif symbol == key.B:
            self.controllers.bButtonPressed()
        elif symbol == key.LEFT:
            self.controllers.leftButtonPressed()
        elif symbol == key.RIGHT:
            self.controllers.rightButtonPressed()
        elif symbol == key.UP:
            self.controllers.upButtonPressed()
        elif symbol == key.DOWN:
            self.controllers.downButtonPressed()
        elif symbol == key.ENTER:
            self.controllers.startButtonPressed()
        elif symbol == key.SPACE:
            self.controllers.selectButtonPressed()

    def on_draw(self):
        self.clear()
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2i', [self.x, self.y, self.x - self.dx, self.y, self.x - self.dx, self.y - self.dy, self.x, self.y - self.dy]))

