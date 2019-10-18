import pyglet
from pyglet.window import key

class Window(pyglet.window.Window):

    def __init__(self):
        super(Window, self).__init__()
        self.label = pyglet.text.Label('Hello, world!', x=10, y=10)
        self.x = 100
        self.y = 100
        self.dx = 4
        self.dy = 4

    def drawSpriteWithDimensions(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = 4*dx  # One pixel of the emulator represents 4 pixels of the screen
        self.dy = 4*dy

    # Enter is start
    # Space is select
    def on_key_press(self, symbol, modifiers):
        if symbol == key.A:
            print('The A key was pressed.')
        elif symbol == key.B:
            print('The B arrow key was pressed.')
        elif symbol == key.LEFT:
            print('The left arrow key was pressed.')
        elif symbol == key.RIGHT:
            print('The right arrow key was pressed.')
        elif symbol == key.UP:
            print('The up arrow key was pressed.')
        elif symbol == key.DOWN:
            print('The down arrow key was pressed.')
        elif symbol == key.ENTER:
            print('The enter key was pressed.')
        elif symbol == key.SPACE:
            print('The space key was pressed.')

    def on_draw(self):
        # self.clear()
        self.label.draw()
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2i', [self.x, self.y, self.x - self.dx, self.y, self.x - self.dx, self.y - self.dy, self.x, self.y - self.dy]))

