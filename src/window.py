import pyglet
from pyglet.window import key

class Window(pyglet.window.Window):

    def __init__(self):
        super(Window, self).__init__()
        self.label = pyglet.text.Label('Hello, world!', x=10, y=10)

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
        self.clear()
        self.label.draw()
