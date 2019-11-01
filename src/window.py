import pygame

SCALE = 2

class Window:
    def __init__(self):
        size = (256*SCALE, 240*SCALE)

        self.surface = pygame.display.set_mode(size)

        self.surface.fill(pygame.Color(255,0,0))
        pygame.display.update()

    def setPixel(self, i, j, color):
        pygame.draw.rect(self.surface, color, pygame.Rect(i*SCALE, j*SCALE, SCALE, SCALE))

    def flip(self):
        pygame.display.flip()

def main():

    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        # Add this somewhere after the event pumping and before the display.flip()
            pygame.draw.rect(screen, (0, 128, 255), pygame.Rect(30, 30, 60, 60))

        pygame.display.flip()

if __name__ == "__main__":
    main()