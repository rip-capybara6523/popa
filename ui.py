import pygame
from setting import BASE_Y, load_image

class Base:
    def __init__(self, x, width, height, img_name, fallback_color):
        self.rect = pygame.Rect(x, BASE_Y, width, height)
        self.hp = 1000
        self.max_hp = 1000
        self.image = load_image(img_name, width, fallback_color)
        self.image = pygame.transform.scale(self.image, (width, height))

    def damage(self, value):
        self.hp = max(0, self.hp - value)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), (self.rect.x, self.rect.y - 18, self.rect.width, 10), 2, 4)
        value = max(self.hp, 0) / self.max_hp * self.rect.width
        pygame.draw.rect(screen, (0, 200, 50), (self.rect.x, self.rect.y - 18, value, 10))