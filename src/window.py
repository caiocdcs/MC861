import pygame

SCALE = 2

class Window:
    def __init__(self):
        size = (256*SCALE, 240*SCALE)

        self.surface = pygame.display.set_mode(size)

        pygame.display.update()

    def setPixel(self, i, j, color):
        self.surface.fill(pygame.Color(255,0,0))
        pygame.draw.rect(self.surface, color, pygame.Rect(i*SCALE, j*SCALE, SCALE, SCALE))

    def flip(self):
        pygame.display.flip()