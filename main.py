import pygame
import random

pygame.init()

# настройки
WIDTH, HEIGHT = 800, 400
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("OOP Battle Cats Mini")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
RED = (255, 80, 80)
BLACK = (0, 0, 0)

# -------------------
# БАЗА
# -------------------
class Base:
    def init(self, x, hp, color):
        self.x = x
        self.hp = hp
        self.color = color

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, 200, 40, 100))


# -------------------
# ЮНИТ
# -------------------
class Unit:
    def init(self, x, y, direction, color):
        self.x = x
        self.y = y
        self.direction = direction
        self.color = color
        self.hp = 100
        self.speed = 1
        self.attack = 1

    def update(self):
        self.x += self.speed * self.direction

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, 30, 30))

    def is_colliding(self, other):
        return abs(self.x - other.x) < 30


# -------------------
# ИГРА
# -------------------
class Game:
    def init(self):
        self.cats = []
        self.enemies = []
        self.spawn_timer = 0

        self.player_base = Base(0, 500, BLUE)
        self.enemy_base = Base(760, 500, RED)

    def spawn_cat(self):
        self.cats.append(Unit(50, 250, 1, BLUE))

    def spawn_enemy(self):
        self.enemies.append(Unit(700, 250, -1, RED))

    def update(self):
        # спавн врагов
        self.spawn_timer += 1
        if self.spawn_timer > 120:
            self.spawn_enemy()
            self.spawn_timer = 0

        # движение
        for unit in self.cats + self.enemies:
            unit.update()

        # бои
        for cat in self.cats:
            for enemy in self.enemies:
                if cat.is_colliding(enemy):
                    cat.hp -= enemy.attack
                    enemy.hp -= cat.attack

        # атака баз
        for cat in self.cats:
            if cat.x > 730:
                self.enemy_base.hp -= cat.attack
                cat.hp = 0

        for enemy in self.enemies:
            if enemy.x < 50:
                self.player_base.hp -= enemy.attack
                enemy.hp = 0

        # удаление
        self.cats = [c for c in self.cats if c.hp > 0]
        self.enemies = [e for e in self.enemies if e.hp > 0]

    def draw(self):
        screen.fill(WHITE)

        # базы
        self.player_base.draw()
        self.enemy_base.draw()

        # юниты
        for unit in self.cats + self.enemies:
            unit.draw()

        # HP текст
        font = pygame.font.SysFont(None, 24)
        text1 = font.render(f"Base HP: {self.player_base.hp}", True, BLACK)
        text2 = font.render(f"Enemy HP: {self.enemy_base.hp}", True, BLACK)

        screen.blit(text1, (10, 10))
        screen.blit(text2, (600, 10))


# -------------------
# ЗАПУСК
# -------------------
game = Game()

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # спавн кота
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game.spawn_cat()

    game.update()
    game.draw()

    pygame.display.update()

pygame.quit()