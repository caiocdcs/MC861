import pygame

SCALE = 2

class Window:
    def __init__(self):
        size = (256, 240)

        self.surface = pygame.display.set_mode(size)

        pygame.display.update()

    def setPixel(self, i, j, color):
        # self.surface.fill(pygame.Color(255,0,0))
        pygame.draw.line(self.surface, color, (i, j), (i, j))
        # pygame.draw.rect(self.surface, color, pygame.Rect(i*SCALE, j*SCALE, SCALE, SCALE))

    def flip(self):
        pygame.display.flip()