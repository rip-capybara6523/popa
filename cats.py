import pygame
import random
from setting import load_image
from base import Unit

class RangedCat(Unit):
    def __init__(self, x, y, hp, speed, atk, img_name, fallback_color, range_dist, cooldown, size):
        super().__init__(x, y, hp, speed, atk, img_name, fallback_color, size=size, ranged=True, range_dist=range_dist, side='ally')
        self.shoot_cooldown = cooldown
        self.ranged_reload = random.randint(0, cooldown - 1)
        self.shooting_mode = False

    def update(self, enemies):
        self.shooting_mode = any(0 < enemy.rect.left - self.rect.right <= self.range_dist for enemy in enemies)
        # Рухається, якщо не стріляє і не заблокований іншим котиком
        if not self.shooting_mode and not self.is_blocked:
            self.rect.x += self.speed

    def can_shoot(self):
        return self.ranged_reload == 0 and self.shooting_mode

    def tick_reload(self):
        self.ranged_reload = max(0, self.ranged_reload - 1)

    def reset_reload(self):
        self.ranged_reload = self.shoot_cooldown


class Bullet:
    SIZE = 18
    SPEED = 10

    def __init__(self, x, y, dmg, range_px):
        self.rect = pygame.Rect(x, y + 11, Bullet.SIZE, Bullet.SIZE)
        self.speed = Bullet.SPEED
        self.dmg = dmg
        self.range = range_px
        self.start_x = x
        self.active = True
        self.image = load_image("bullet.png", Bullet.SIZE, (180, 180, 30))

    def update(self):
        self.rect.x += self.speed
        if self.rect.x - self.start_x > self.range:
            self.active = False

    def draw(self, screen):
        screen.blit(self.image, self.rect)