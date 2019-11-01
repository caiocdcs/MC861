import pygame

class Keyboard:

    def __init__(self):
        self.aButtonPressed = 0
        self.bButtonPressed = 0
        self.selectButtonPressed = 0
        self.startButtonPressed = 0
        self.upButtonPressed = 0
        self.downButtonPressed = 0
        self.leftButtonPressed = 0
        self.rightButtonPressed = 0

    def resetState(self):
        self.aButtonPressed = 0
        self.bButtonPressed = 0
        self.selectButtonPressed = 0
        self.startButtonPressed = 0
        self.upButtonPressed = 0
        self.downButtonPressed = 0
        self.leftButtonPressed = 0
        self.rightButtonPressed = 0

    def pressAButton(self):
        self.aButtonPressed = 1

    def pressBButton(self):
        self.bButtonPressed = 1

    def pressSelectButton(self):
        self.selectButtonPressed = 1

    def pressStartButton(self):
        self.startButtonPressed = 1

    def pressUpButton(self):
        self.upButtonPressed = 1
        print("Up")

    def pressDownButton(self):
        self.downButtonPressed = 1
        print("Down")

    def pressLeftButton(self):
        self.leftButtonPressed = 1
        print("Left")

    def pressRightButton(self):
        self.rightButtonPressed = 1
        print("Right")

    def read(self):
        keyboard = 0
        keyboard = keyboard | (self.rightButtonPressed << 0)
        keyboard = keyboard | (self.leftButtonPressed << 1)
        keyboard = keyboard | (self.downButtonPressed << 2)
        keyboard = keyboard | (self.upButtonPressed << 3)
        keyboard = keyboard | (self.startButtonPressed << 4)
        keyboard = keyboard | (self.selectButtonPressed << 5)
        keyboard = keyboard | (self.bButtonPressed << 6)
        keyboard = keyboard | (self.aButtonPressed << 7)
        
        self.resetState()
        return keyboard
