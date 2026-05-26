import pygame
import os

pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
WHITE = (255, 255, 255)

PATH_LEVEL = HEIGHT - 250
BASE_HEIGHT = 220
BASE_Y = PATH_LEVEL - BASE_HEIGHT + 40

CAT_COLOR = (200, 200, 255)
CAT_TANK_COLOR = (100, 100, 200)
CAT_FAST_COLOR = (230, 150, 200)
CAT_RANGED_COLOR = (200, 180, 20)
CAT_ULTRA_COLOR = (90, 250, 90)
CAT_SUPER_COLOR = (255, 100, 230)
ENEMY_COLOR = (255, 200, 200)
ENEMY_FAST_COLOR = (230, 120, 160)
ENEMY_BOSS_COLOR = (200, 80, 80)
ENEMY_RANGED_COLOR = (220, 150, 40)
ENEMY_SUPER_COLOR = (250, 220, 55)

FPS = 60

ALLY_TYPES = [
    {"name": "Кіт", "cost": 50, "hp": 100, "speed": 2, "atk": 10, "color": CAT_COLOR, "size": 40, "ranged": False, "img_name": "cat_normal.png"},
    {"name": "Кіт-кремез", "cost": 150, "hp": 260, "speed": 1, "atk": 23, "color": CAT_TANK_COLOR, "size": 50, "ranged": False, "img_name": "cat_heavy.png"},
    {"name": "Танкокіт", "cost": 250, "hp": 450, "speed": 1, "atk": 33, "color": CAT_FAST_COLOR, "size": 55, "ranged": False, "img_name": "cat_tank.png"},
    {"name": "Дальнокіт", "cost": 300, "hp": 65, "speed": 1.1, "atk": 18, "color": CAT_RANGED_COLOR, "size": 45, "ranged": True, "range": int(WIDTH // 2), "shoot_cooldown": 40, "img_name": "cat_ranged.png"},
    {"name": "Гіперкіт", "cost": 500, "hp": 1600, "speed": 4.5, "atk": 48, "color": CAT_SUPER_COLOR, "size": 50, "ranged": False, "img_name": "cat_hyper.png"},
    {"name": "Ультракуб", "cost": 1000, "hp": 6500, "speed": 0.65, "atk": 160, "color": CAT_ULTRA_COLOR, "size": 75, "ranged": False, "img_name": "cat_ultra.png"},
]

ENEMY_TYPES = [
    {"hp": 120, "speed": 1, "atk": 8, "color": ENEMY_COLOR, "ranged": False, "range": 0, "name": "Ворог", "size": 40, "img_name": "enemy_normal.png"},
    {"hp": 200, "speed": 1.7, "atk": 16, "color": ENEMY_FAST_COLOR, "ranged": False, "range": 0, "name": "Швидкий", "size": 40, "img_name": "enemy_fast.png"},
    {"hp": 420, "speed": 0.9, "atk": 30, "color": ENEMY_BOSS_COLOR, "ranged": False, "range": 0, "name": "Бос", "size": 50, "img_name": "enemy_boss.png"},
    {"hp": 70, "speed": 1.05, "atk": 16, "color": ENEMY_RANGED_COLOR, "ranged": True, "range": int(WIDTH // 2), "name": "Дальній", "size": 45, "img_name": "enemy_ranged.png"},
    {"hp": 540, "speed": 0.66, "atk": 38, "color": ENEMY_SUPER_COLOR, "ranged": False, "range": 0, "name": "Суперкуб", "size": 65, "img_name": "enemy_super.png"}
]

BOSS_STATS = {"hp": 3500, "speed": 1, "atk": 55, "color": (240, 219, 29), "size": 130, "img_name": "enemy_final_boss.png"}


SPAWN_COOLDOWN = 2
SPAWN_COOLDOWN_BOSS = 5
START_ENERGY_MAX = 100
ENERGY_REGEN = 0.18

ENERGY_UPGRADES = [
    {"cost": 100, "new_max": 150, "mult": 1.75},
    {"cost": 150, "new_max": 200, "mult": 2.25},
    {"cost": 200, "new_max": 300, "mult": 3.00},
    {"cost": 300, "new_max": 750, "mult": 2.5},
    {"cost": 500, "new_max": 1500, "mult": 3.5}
]

SPECIAL_ATTACK_COST = 750
SPECIAL_ATTACK_DMG = 100
SPECIAL_ATTACK_COOLDOWN = 45

def load_image(filename, size, fallback_color):
    if os.path.exists(filename):
        try:
            img = pygame.image.load(filename).convert_alpha()
            return pygame.transform.scale(img, (size, size))
        except Exception:
            pass
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    surface.fill(fallback_color)
    return surface