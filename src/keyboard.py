class Keyboard:

    def __init__(self):
        self.index = 0
        self.keys = [False] * 8

    def resetState(self):
        self.keys = [False] * 8

    def aButtonPressed(self):
        self.keys[0] = True

    def bButtonPressed(self):
        self.keys[1] = True

    def selectButtonPressed(self):
        self.keys[2] = True

    def startButtonPressed(self):
        self.keys[3] = True

    def upButtonPressed(self):
        self.keys[4] = True

    def downButtonPressed(self):
        self.keys[5] = True

    def leftButtonPressed(self):
        self.keys[6] = True

    def rightButtonPressed(self):
        self.keys[7] = True

    def read(self):
        keyStatus = self.keys[self.index]
        self.updateIndex()
        return keyStatus

    def updateIndex(self):
        self.index += 1
        if self.index > 7:
            self.index = 0