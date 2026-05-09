import pygame
import random
import time

pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
WHITE = (255, 255, 255)

# Новое: базу и путь опускаем и смещаем выше нижнего меню
PATH_LEVEL = HEIGHT - 270
BASE_HEIGHT = 100
BASE_Y = PATH_LEVEL - BASE_HEIGHT - 30  # Базы повыше линии

CAT_COLOR = (200, 200, 255)
CAT_TANK_COLOR = (100, 100, 200)
CAT_FAST_COLOR = (230, 150, 200)
CAT_RANGED_COLOR = (200, 180, 20)
CAT_ULTRA_COLOR = (90, 250, 90)
CAT_SUPER_COLOR = (255, 100, 230)
BASE_COLOR = (180, 180, 180)
ENEMY_COLOR = (255, 200, 200)
ENEMY_FAST_COLOR = (230, 120, 160)
ENEMY_BOSS_COLOR = (200, 80, 80)
ENEMY_RANGED_COLOR = (220, 150, 40)
ENEMY_SUPER_COLOR = (250, 220, 55)

FPS = 60

ALLY_TYPES = [
    {"name": "Кот", "cost": 50, "hp": 100, "speed": 2, "atk": 10, "color": CAT_COLOR, "size": 40, "ranged": False},
    {"name": "Кот крепыш", "cost": 150, "hp": 260, "speed": 1, "atk": 23, "color": CAT_TANK_COLOR, "size": 40, "ranged": False},
    {"name": "Танковый кот", "cost": 250, "hp": 450, "speed": 1, "atk": 33, "color": CAT_FAST_COLOR, "size": 40, "ranged": False},
    # Дальний кот — дальность увеличена вдвое
    {"name": "Дальний кот", "cost": 300, "hp": 65, "speed": 1.1, "atk": 18, "color": CAT_RANGED_COLOR,
     "size": 40, "ranged": True, "range": int(WIDTH // 2), "shoot_cooldown": 40},
    {"name": "Гипер кот", "cost": 500, "hp": 1600, "speed": 4.5, "atk": 48, "color": CAT_SUPER_COLOR, "size": 40, "ranged": False},
    {"name": "Ультра куб", "cost": 1000, "hp": 6500, "speed": 0.65, "atk": 160, "color": CAT_ULTRA_COLOR, "size": 64, "ranged": False},
]

ENEMY_TYPES = [
    {"hp": 120, "speed": 1, "atk": 8, "color": ENEMY_COLOR, "ranged": False, "range": 0, "name": "Враг", "level":1, "size": 40},
    {"hp": 200, "speed": 1.7, "atk": 16, "color": ENEMY_FAST_COLOR, "ranged": False, "range": 0, "name": "Быстрый", "level":2, "size": 40},
    {"hp": 420, "speed": 0.9, "atk": 30, "color": ENEMY_BOSS_COLOR, "ranged": False, "range": 0, "name": "Босс", "level": 3, "size": 40},
    {"hp": 70, "speed": 1.05, "atk": 16, "color": ENEMY_RANGED_COLOR, "ranged": True, "range": int(WIDTH // 2), "name": "Дальний", "level": 4, "size": 40},
    {"hp": 540, "speed": 0.66, "atk": 38, "color": ENEMY_SUPER_COLOR, "ranged": False, "range": 0, "name": "Супер-куб", "level": 5, "size": 56}
]

SPAWN_COOLDOWN = 2
SPAWN_COOLDOWN_BOSS = 5
START_ENERGY_MAX = 100
ENERGY_REGEN = 0.18

ENERGY_UPGRADES = [
    {"cost": 100,  "new_max": 150,  "mult": 1.75},
    {"cost": 150,  "new_max": 200,  "mult": 2.25},
    {"cost": 200,  "new_max": 300,  "mult": 3.00},
    {"cost": 300,  "new_max": 750,  "mult": 2.5},
    {"cost": 500,  "new_max": 1500,"mult": 3.5}
]

BASE_RANGED_COOLDOWN = 35
BOSS_STATS = {"hp": 3500, "speed": 0.33, "atk": 55, "color": (240,219,29), "size": 120}
SPECIAL_ATTACK_COST = 750
SPECIAL_ATTACK_DMG = 100
SPECIAL_ATTACK_COOLDOWN = 45

class Unit(pygame.sprite.Sprite):
    def __init__(self, x, y, hp, speed, atk, color, size, ranged=False, range_dist=0, side='ally'):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.max_hp = hp
        self.hp = hp
        self.speed = speed
        self.atk = atk
        self.ranged = ranged
        self.range_dist = range_dist
        self.ranged_reload = 0
        self.side = side
        self.size = size

    def update(self):
        dx = self.speed if self.side == 'ally' else -self.speed
        self.rect.x += dx

    def is_dead(self):
        return self.hp <= 0

class RangedCat(Unit):
    def __init__(self, x, y, hp, speed, atk, color, range_dist, cooldown, size):
        super().__init__(x, y, hp, speed, atk, color, size=size, ranged=True, range_dist=range_dist, side='ally')
        self.shoot_cooldown = cooldown
        self.ranged_reload = random.randint(0, cooldown-1)
        self.shooting_mode = False

    def update(self, enemies):
        # Проверяем есть ли враг в радиусе
        self.shooting_mode = False
        for enemy in enemies:
            if 0 < enemy.rect.left - self.rect.right <= self.range_dist:
                self.shooting_mode = True
                break
        if self.shooting_mode:
            pass  # Стоит на месте
        else:
            self.rect.x += self.speed

    def can_shoot(self):
        return self.ranged_reload == 0 and self.shooting_mode

    def tick_reload(self):
        self.ranged_reload = max(0, self.ranged_reload - 1)

    def reset_reload(self):
        self.ranged_reload = self.shoot_cooldown

class UltraCat(Unit):
    def __init__(self, x, y, hp, speed, atk, color, size):
        super().__init__(x, y, hp, speed, atk, color, size, ranged=False, side='ally')

class Bullet:
    SIZE = 18
    SPEED = 10
    COLOR = (180,180,30)

    def __init__(self, x, y, dmg, range_px):
        self.rect = pygame.Rect(x, y + 11, Bullet.SIZE, Bullet.SIZE)
        self.speed = Bullet.SPEED
        self.dmg = dmg
        self.range = range_px
        self.start_x = x
        self.active = True

    def update(self):
        self.rect.x += self.speed
        if self.rect.x - self.start_x > self.range:
            self.active = False

    def draw(self, screen):
        pygame.draw.rect(screen, Bullet.COLOR, self.rect)

class EnemyBoss(Unit):
    def __init__(self, x, y):
        super().__init__(x, y, BOSS_STATS["hp"], BOSS_STATS["speed"], BOSS_STATS["atk"], BOSS_STATS["color"], BOSS_STATS["size"], False, 0, "enemy")

class Base:
    def __init__(self, x, width, color):
        self.rect = pygame.Rect(x, BASE_Y, width, BASE_HEIGHT)
        self.color = color
        self.hp = 1000
        self.max_hp = 1000

    def damage(self, value):
        self.hp = max(0, self.hp - value)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, (0,0,0), (self.rect.x, self.rect.y - 18, self.rect.width, 10), 2, 4)
        value = max(self.hp, 0) / self.max_hp * self.rect.width
        pygame.draw.rect(screen, (0,200,50), (self.rect.x, self.rect.y - 18, value, 10))

class Game:
    def __init__(self):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 30)
        self.font_small = pygame.font.SysFont(None, 23)
        self.player_base = None
        self.enemy_base = None
        self.cats = None
        self.enemies = None
        self.bullets = None
        self.all_units = None
        self.energy = 0
        self.energy_regen = ENERGY_REGEN
        self.energy_max = START_ENERGY_MAX
        self.last_spawn_time = -SPAWN_COOLDOWN
        self.selected_cat = 0
        self.energy_upgrade_level = 0
        self.running = True
        self.next_enemy_spawn = 0
        self.upgrade_btn_rect = None
        self.boss_spawned = False
        self.boss = None
        self.boss_defeated = False
        self.special_btn_rect = None
        self.last_special_time = -SPECIAL_ATTACK_COOLDOWN

    def setup(self):
        self.player_base = Base(30, 70, BASE_COLOR)
        self.enemy_base = Base(WIDTH - 100, 70, BASE_COLOR)
        self.cats = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.all_units = pygame.sprite.Group()
        self.bullets = []
        self.energy = 0
        self.energy_regen = ENERGY_REGEN
        self.energy_max = START_ENERGY_MAX
        self.last_spawn_time = -SPAWN_COOLDOWN
        self.selected_cat = 0
        self.energy_upgrade_level = 0
        self.running = True
        self.next_enemy_spawn = time.time() + random.uniform(2.0, 3.5)
        self.boss_spawned = False
        self.boss = None
        self.boss_defeated = False
        self.last_special_time = -SPECIAL_ATTACK_COOLDOWN

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.try_spawn_cat()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                idx = self.cat_menu_hit(mx, my)
                if idx is not None:
                    self.selected_cat = idx
                if self.upgrade_btn_rect and self.upgrade_btn_rect.collidepoint(mx, my):
                    self.try_upgrade_energy()
                if self.special_btn_rect and self.special_btn_rect.collidepoint(mx, my):
                    self.try_special_attack()

    def try_spawn_cat(self):
        now = time.time()
        st = ALLY_TYPES[self.selected_cat]
        cost = st["cost"]
        enough_energy = self.energy >= cost
        cooldown_ready = now - self.last_spawn_time >= SPAWN_COOLDOWN
        if enough_energy and cooldown_ready:
            y_spawn = PATH_LEVEL - st["size"] // 2
            if self.selected_cat == 3:  # Дальний кастом
                cat = RangedCat(self.player_base.rect.right, y_spawn, st["hp"], st["speed"], st["atk"], st["color"], st["range"], st["shoot_cooldown"], st["size"])
            elif self.selected_cat == 5:
                cat = UltraCat(self.player_base.rect.right, y_spawn-24, st["hp"], st["speed"], st["atk"], st["color"], st["size"])
            else:
                cat = Unit(self.player_base.rect.right, y_spawn, st["hp"], st["speed"], st["atk"], st["color"], st["size"], ranged=st.get("ranged", False), range_dist=st.get("range",0), side='ally')
            self.cats.add(cat)
            self.all_units.add(cat)
            self.energy -= cost
            self.last_spawn_time = now

    def try_upgrade_energy(self):
        if self.energy_upgrade_level >= len(ENERGY_UPGRADES):
            return
        upg = ENERGY_UPGRADES[self.energy_upgrade_level]
        if self.energy >= upg["cost"]:
            self.energy -= upg["cost"]
            self.energy_max = upg["new_max"]
            self.energy_regen = ENERGY_REGEN * upg["mult"]
            self.energy_upgrade_level += 1

    def try_special_attack(self):
        now = time.time()
        cd = now - self.last_special_time
        if self.energy < SPECIAL_ATTACK_COST or cd < SPECIAL_ATTACK_COOLDOWN:
            return
        for e in list(self.enemies):
            if not isinstance(e, EnemyBoss):
                e.hp -= SPECIAL_ATTACK_DMG
        self.energy -= SPECIAL_ATTACK_COST
        self.last_special_time = now

    def enemy_spawn_table(self):
        hp = self.enemy_base.hp
        if not self.boss_spawned:
            table = [(0.70, 0)]
            if hp <= 750:
                table.append((0.20, 1))
            if hp <= 500:
                table.append((0.07, 2))
            if hp <= 250:
                table.append((0.03, 3))
            s = sum(w for w, _ in table)
            accum = 0.0
            span = []
            for w, idx in table:
                span.append((accum/s, accum/s + w/s, idx))
                accum += w
            return span
        else:
            return [(0.0,0.7,4),(0.7,0.9,1),(0.9,1.0,0)]

    def choose_enemy_type(self):
        table = self.enemy_spawn_table()
        r = random.random()
        for start, end, idx in table:
            if start <= r < end:
                return ENEMY_TYPES[idx]
        return ENEMY_TYPES[0]

    def boss_conditions(self):
        return self.enemy_base.hp <= 0 and not self.boss_spawned

    def spawn_boss(self):
        self.enemy_base.hp = 1
        y = PATH_LEVEL - BOSS_STATS["size"] // 2
        self.boss = EnemyBoss(self.enemy_base.rect.left-100, y)
        self.enemies.add(self.boss)
        self.all_units.add(self.boss)
        self.boss_spawned = True
        self.next_enemy_spawn = time.time() + SPAWN_COOLDOWN_BOSS

    def spawn_enemies(self):
        now = time.time()
        cd = SPAWN_COOLDOWN_BOSS if self.boss_spawned else SPAWN_COOLDOWN
        if now >= self.next_enemy_spawn:
            y = PATH_LEVEL - 20
            et = self.choose_enemy_type()
            size = et["size"]
            spawn_x = self.boss.rect.left-70 if self.boss_spawned and self.boss is not None and not self.boss_defeated else self.enemy_base.rect.left-40
            if et.get("ranged", False):
                enemy = Unit(spawn_x, y, et["hp"], et["speed"], et["atk"], et["color"], size, ranged=True, range_dist=et.get("range",0), side='enemy')
            else:
                enemy = Unit(spawn_x, y, et["hp"], et["speed"], et["atk"], et["color"], size, ranged=False, range_dist=0, side='enemy')
            self.enemies.add(enemy)
            self.all_units.add(enemy)
            self.next_enemy_spawn = now + random.uniform(cd, cd+2.0)

    def update_energy(self):
        self.energy = min(self.energy + self.energy_regen, self.energy_max)

    def update_bullets(self):
        for bullet in self.bullets:
            bullet.update()
        self.bullets = [b for b in self.bullets if b.active]
        for bullet in self.bullets:
            for enemy in self.enemies:
                if isinstance(enemy, EnemyBoss):
                    continue
                if bullet.rect.colliderect(enemy.rect):
                    enemy.hp -= bullet.dmg
                    bullet.active = False
                    break

    def update_units(self):
        for cat in self.cats:
            if isinstance(cat, RangedCat):
                cat.tick_reload()
                cat.update(list(self.enemies))
                if cat.can_shoot():
                    bullet = Bullet(cat.rect.right, cat.rect.y, cat.atk, cat.range_dist)
                    self.bullets.append(bullet)
                    cat.reset_reload()
            else:
                cat.update()
        for cat in self.cats:
            if not isinstance(cat, RangedCat) and cat.ranged:
                cat.ranged_reload = max(0, cat.ranged_reload-1)
                if cat.ranged_reload == 0:
                    for enemy in self.enemies:
                        dist = enemy.rect.left - cat.rect.right
                        if 0 < dist <= cat.range_dist:
                            enemy.hp -= cat.atk
                            cat.ranged_reload = BASE_RANGED_COOLDOWN
                            break
            if not self.boss_spawned or self.boss_defeated:
                if cat.rect.colliderect(self.enemy_base.rect):
                    self.enemy_base.damage(cat.atk)
                    cat.hp = 0
            hit_enemies = pygame.sprite.spritecollide(cat, self.enemies, False)
            for enemy in hit_enemies:
                if not isinstance(cat, RangedCat) and not cat.ranged:
                    cat.hp -= enemy.atk
                if not getattr(enemy, 'ranged', False) and not isinstance(enemy, EnemyBoss):
                    enemy.hp -= cat.atk
        for enemy in self.enemies:
            # Теперь враги всегда двигаются, босс тоже (он Unit)
            enemy.update()
            if getattr(enemy, 'ranged', False):
                enemy.ranged_reload = max(0, enemy.ranged_reload-1) if hasattr(enemy, 'ranged_reload') else 0
                if hasattr(enemy, 'range_dist') and enemy.ranged_reload == 0:
                    for cat in self.cats:
                        dist = enemy.rect.left - cat.rect.right
                        if -enemy.range_dist < dist < 0:
                            cat.hp -= enemy.atk
                            enemy.ranged_reload = BASE_RANGED_COOLDOWN
                            break
            if enemy.rect.colliderect(self.player_base.rect):
                self.player_base.damage(enemy.atk)
                enemy.hp = 0
        for group in (self.cats, self.enemies, self.all_units):
            for sprite in list(group):
                if sprite.is_dead():
                    if isinstance(sprite, EnemyBoss):
                        self.boss_defeated = True
                        self.enemy_base.hp = 1
                    group.remove(sprite)
        self.update_bullets()

    def draw_cat_menu(self):
        x = 20
        y = HEIGHT - 100
        boxw = 190
        pygame.draw.rect(self.screen, (80, 80, 180), (x-10, y-10, boxw*len(ALLY_TYPES)+20, 62), 0, 8)
        for i, st in enumerate(ALLY_TYPES):
            rect = pygame.Rect(x+i*boxw, y, boxw-6, 58)
            highlight = 4 if self.selected_cat==i else 0
            pygame.draw.rect(self.screen, (230,230,255), rect, 0, 8)
            pygame.draw.rect(self.screen, (30,60,190), rect, highlight, 8)
            name = st['name']
            color = st['color']
            pygame.draw.rect(self.screen, color, (rect.x+8, rect.y+6, st['size'], st['size']))
            t1 = self.font_small.render(f"{name}", True, (0,0,0))
            t2 = self.font_small.render(f"Цена: {st['cost']}", True, (30,90,70))
            rect_t1 = t1.get_rect(left=rect.x+60, centery=rect.y+22)
            rect_t2 = t2.get_rect(left=rect.x+60, centery=rect.y+44)
            self.screen.blit(t1, rect_t1)
            self.screen.blit(t2, rect_t2)
            if st.get("ranged", False):
                rr = self.font_small.render("Дист.", True, (140,40,40))
                self.screen.blit(rr, (rect.x+135, rect.y+18))

    def cat_menu_hit(self, mx, my):
        x = 20
        y = HEIGHT - 100
        boxw = 190
        if y <= my <= y+58:
            for i in range(len(ALLY_TYPES)):
                if x+i*boxw <= mx < x+(i+1)*boxw-6:
                    return i
        return None

    def draw_upgrade_btn(self):
        upg_y = HEIGHT - 175
        ulevel = self.energy_upgrade_level
        text = f"Прокачка энергии: {ulevel}/{len(ENERGY_UPGRADES)}"
        txt = self.font_small.render(text, True, (40, 70, 220))
        self.screen.blit(txt, (20, upg_y))
        rect = pygame.Rect(20, upg_y+28, 250, 45)
        if ulevel < len(ENERGY_UPGRADES):
            nxt = ENERGY_UPGRADES[ulevel]
            btn_color = (140,220,220) if self.energy>=nxt["cost"] else (180,180,180)
            pygame.draw.rect(self.screen, btn_color, rect, 0, 6)
            pygame.draw.rect(self.screen, (80,120,220), rect, 2, 6)
            text2 = f"Улучшить за {nxt['cost']}э"
            t2 = self.font_small.render(text2, True, (0,0,0))
            self.screen.blit(t2, (rect.x+10, rect.y+5))
            text3 = f"MAX {nxt['new_max']}, x{nxt['mult']:.2f} regen"
            t3 = self.font_small.render(text3, True, (30,90,170))
            self.screen.blit(t3, (rect.x+10, rect.y+24))
        else:
            pygame.draw.rect(self.screen, (110,220,110), rect, 0, 6)
            pygame.draw.rect(self.screen, (60,170,100), rect, 2, 6)
            t2 = self.font_small.render("Достигнут лимит!",True,(30,120,60))
            self.screen.blit(t2, (rect.x+10, rect.y+12))
        self.upgrade_btn_rect = rect

    def draw_special_btn(self):
        rect = pygame.Rect(WIDTH-360, 55, 320, 54)
        now = time.time()
        cd = max(0, SPECIAL_ATTACK_COOLDOWN - (now-self.last_special_time))
        btn_color = (245, 160, 40) if self.energy>=SPECIAL_ATTACK_COST and cd == 0 else (170,150,100)
        pygame.draw.rect(self.screen, btn_color, rect, 0, 6)
        pygame.draw.rect(self.screen, (170, 100, 40), rect, 2, 6)
        if cd > 0:
            t1 = self.font_small.render(f"КД {cd:.0f} сек", True, (90,0,0))
            self.screen.blit(t1, (rect.x+15, rect.y+7))
        else:
            t1 = self.font_small.render("Атака!", True, (0,0,0))
            self.screen.blit(t1, (rect.x+15, rect.y+7))
        t2 = self.font_small.render(f"750 э: -100 HP всем врагам", True, (80,0,60))
        self.screen.blit(t2, (rect.x+15, rect.y+28))
        self.special_btn_rect = rect

    def draw_bullets(self):
        for b in self.bullets:
            b.draw(self.screen)

    def draw(self):
        self.screen.fill(WHITE)
        self.player_base.draw(self.screen)
        self.enemy_base.draw(self.screen)
        self.all_units.draw(self.screen)
        self.draw_bullets()
        # Верхний левый интерфейс
        pb_hp_text = self.font.render(f"База: {max(self.player_base.hp,0)}", True, (0,0,0))
        self.screen.blit(pb_hp_text, (10, 10))
        # Верхний правый интерфейс
        eb_hp_text = self.font.render(f"Враг база: {max(self.enemy_base.hp, 0)}", True, (255, 255, 255))

        # 2. Малюємо текст на екрані, вказавши координати (WIDTH-400, 10)
        self.screen.blit(eb_hp_text, (WIDTH - 400, 10))

        energy_text = self.font.render(f"Энергия: {int(self.energy)} / {self.energy_max}", True, (0,80,200))
        self.screen.blit(eb_hp_text, (WIDTH-400, 10))
        self.screen.blit(energy_text, (10, 50))
        now = time.time()
        spawn_cooldown = max(0, SPAWN_COOLDOWN - (now - self.last_spawn_time))
        cooldown_text = self.font_small.render(
            f"КД выпуска: {spawn_cooldown:.1f} сек" if spawn_cooldown > 0 else "Юнит готов!", True, (160,80,0)
        )
        self.screen.blit(cooldown_text, (10, 80))
        self.draw_upgrade_btn()
        self.draw_cat_menu()
        self.draw_special_btn()
        # Босс
        if self.boss and not self.boss_defeated and self.boss in self.enemies:
            bhp = self.boss.hp
            mxhp = BOSS_STATS["hp"]
            bx = self.boss.rect.x
            by = self.boss.rect.y - 38
            w = BOSS_STATS["size"]
            pygame.draw.rect(self.screen,(180,160,20),(bx,by,w,24),0,6)
            pygame.draw.rect(self.screen,(0,0,0),(bx,by,w,24),2,6)
            valw = min(max(bhp,0)/mxhp*w, w)
            pygame.draw.rect(self.screen,(50,200,20),(bx,by,valw,24),0,6)
            btxt = self.font_small.render("БОСС",True,(90,60,0))
            self.screen.blit(btxt,(bx+6,by-24))
        # Победа / поражение
        if (self.enemy_base.hp <= 0 and self.boss_defeated):
            msg = "ПОБЕДА! Босс повержен."
            msg_surf = self.font.render(msg, True, (200,0,0))
            self.screen.blit(msg_surf, (WIDTH//2-180, 120))
        elif self.player_base.hp <= 0:
            msg = "Поражение!"
            msg_surf = self.font.render(msg, True, (200,0,0))
            self.screen.blit(msg_surf, (WIDTH//2-60, 120))
        pygame.display.flip()

    def game_over(self):
        return (self.enemy_base.hp <= 0 and self.boss_defeated) or self.player_base.hp <= 0

    def run(self):
        self.setup()
        while self.running:
            if self.boss_conditions():
                self.spawn_boss()
            self.handle_events()
            if not self.game_over():
                self.update_energy()
                self.spawn_enemies()
                self.update_units()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()