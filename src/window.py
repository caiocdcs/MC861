import pyglet

class Window(pyglet.window.Window):

    def __init__(self):
        super(Window, self).__init__()
        self.label = pyglet.text.Label('Hello, world!', x=10, y=10)

    def on_key_press(self, symbol, modifiers):
        print('A key was pressed')

    def on_draw(self):
        self.clear()
        self.label.draw()
