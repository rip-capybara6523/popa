import pygame
import os
from setting import load_image

class Unit(pygame.sprite.Sprite):
    def __init__(self, x, y, hp, speed, atk, img_name, fallback_color, size, ranged=False, range_dist=0, side='ally'):
        super().__init__()
        self.image = load_image(img_name, size, fallback_color)

        if side == 'enemy' and os.path.exists(img_name):
            self.image = pygame.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect(topleft=(x, y))
        self.max_hp = hp
        self.hp = hp
        self.speed = speed
        self.atk = atk
        self.ranged = ranged
        self.range_dist = range_dist
        self.side = side
        self.size = size
        self.last_attack_time = {}
        self.is_blocked = False  # Нове: чи заблокований рух юніта

    def update(self):
        # Рухаємося лише якщо попереду немає перешкод (для ближнього бою)
        if not self.is_blocked:
            self.rect.x += self.speed if self.side == 'ally' else -self.speed

    def is_dead(self):
        return self.hp <= 0