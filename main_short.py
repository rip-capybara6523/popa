import pygame
import random
import time
import os
from setting import (
    screen, WIDTH, HEIGHT, WHITE, PATH_LEVEL, BASE_HEIGHT, ALLY_TYPES,
    BOSS_STATS, SPAWN_COOLDOWN, SPAWN_COOLDOWN_BOSS, START_ENERGY_MAX,
    ENERGY_REGEN, ENERGY_UPGRADES, SPECIAL_ATTACK_COST, SPECIAL_ATTACK_DMG,
    SPECIAL_ATTACK_COOLDOWN, FPS, load_image
)
from base import Unit
from cats import RangedCat, Bullet
from ui import Base
from enemies import choose_enemy_type

class Game:
    def __init__(self):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, int(HEIGHT * 0.035))
        self.font_small = pygame.font.SysFont(None, int(HEIGHT * 0.024))

        self.menu_x = 20
        self.menu_y = HEIGHT - 85
        self.boxw = int((WIDTH - self.menu_x - 40) // len(ALLY_TYPES))

        self.menu_icons = []
        for st in ALLY_TYPES:
            icon = load_image(st["img_name"], 40, st["color"])
            self.menu_icons.append(icon)

        self.setup()

    def setup(self):
        self.player_base = Base(40, 110, BASE_HEIGHT, "base_player.png", (140, 140, 140))
        self.enemy_base = Base(WIDTH - 150, 110, BASE_HEIGHT, "base_enemy.png", (140, 140, 140))
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

        self.bg_image = None
        if os.path.exists("background.png"):
            self.bg_image = pygame.image.load("background.png").convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (WIDTH, HEIGHT))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
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
        if self.energy >= st["cost"] and now - self.last_spawn_time >= SPAWN_COOLDOWN:
            y_spawn = PATH_LEVEL - st["size"]
            if self.selected_cat == 3:  # Дальнокіт
                cat = RangedCat(self.player_base.rect.right, y_spawn, st["hp"], st["speed"], st["atk"],
                                st["img_name"], st["color"], st["range"], st["shoot_cooldown"], st["size"])
            else:
                cat = Unit(self.player_base.rect.right, y_spawn, st["hp"], st["speed"], st["atk"],
                           st["img_name"], st["color"], st["size"], side='ally')
            self.cats.add(cat)
            self.all_units.add(cat)
            self.energy -= st["cost"]
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
        if self.energy >= SPECIAL_ATTACK_COST and now - self.last_special_time >= SPECIAL_ATTACK_COOLDOWN:
            for e in self.enemies:
                e.hp -= SPECIAL_ATTACK_DMG
            self.energy -= SPECIAL_ATTACK_COST
            self.last_special_time = now

    def spawn_boss(self):
        self.enemy_base.hp = 1
        y = PATH_LEVEL - BOSS_STATS["size"]
        self.boss = Unit(self.enemy_base.rect.left - 100, y, BOSS_STATS["hp"], BOSS_STATS["speed"],
                         BOSS_STATS["atk"], BOSS_STATS["img_name"], BOSS_STATS["color"], BOSS_STATS["size"],
                         side="enemy")
        self.enemies.add(self.boss)
        self.all_units.add(self.boss)
        self.boss_spawned = True
        self.next_enemy_spawn = time.time() + SPAWN_COOLDOWN_BOSS

    def spawn_enemies(self):
        now = time.time()
        if now >= self.next_enemy_spawn:
            et = choose_enemy_type(self.enemy_base.hp, self.boss_spawned)
            spawn_x = self.boss.rect.left - 70 if self.boss_spawned and self.boss and not self.boss_defeated else self.enemy_base.rect.left - 40
            enemy = Unit(spawn_x, PATH_LEVEL - et["size"], et["hp"], et["speed"], et["atk"], et["img_name"],
                         et["color"], et["size"],
                         ranged=et["ranged"], range_dist=et["range"], side='enemy')
            self.enemies.add(enemy)
            self.all_units.add(enemy)
            cd = SPAWN_COOLDOWN_BOSS if self.boss_spawned else SPAWN_COOLDOWN
            self.next_enemy_spawn = now + random.uniform(cd, cd + 2.0)

    def update_units(self):
        now = time.time()

        # =====================================================================
        # 1. ЛОГІКА БЛОКУВАННЯ КОТІВ
        # =====================================================================
        # Сортуємо котів за координатою X (від найближчого до ворога до найвіддаленішого)
        sorted_cats = sorted(self.cats.sprites(), key=lambda c: c.rect.right, reverse=True)

        for i, cat in enumerate(sorted_cats):
            cat.is_blocked = False  # Скидаємо блок за замовчуванням

            # Перевірка зіткнення з ворожою базою
            if cat.rect.colliderect(self.enemy_base.rect):
                cat.is_blocked = True
                cat.rect.right = self.enemy_base.rect.left

            # Перевірка зіткнення з котиком, який іде попереду
            elif i > 0:
                front_cat = sorted_cats[i - 1]
                if cat.rect.right >= front_cat.rect.left - 2:  # 2 пікселі зазору
                    cat.is_blocked = True
                    cat.rect.right = front_cat.rect.left - 2

            # Перевірка зіткнення з ворогами (ближній бій блокує рух кота)
            hit_enemies = pygame.sprite.spritecollide(cat, self.enemies, False)
            if hit_enemies and not isinstance(cat, RangedCat):
                cat.is_blocked = True

        # =====================================================================
        # 2. НОВА ЛОГІКА БЛОКУВАННЯ ВОРОГІВ
        # =====================================================================
        # Сортуємо ворогів за координатою X (від найближчого до нашої бази до найвіддаленішого)
        sorted_enemies = sorted(self.enemies.sprites(), key=lambda e: e.rect.left)

        for i, enemy in enumerate(sorted_enemies):
            enemy.is_blocked = False  # Скидаємо блок за замовчуванням

            # Перевірка зіткнення з базою гравця
            if enemy.rect.colliderect(self.player_base.rect):
                enemy.is_blocked = True
                enemy.rect.left = self.player_base.rect.right

            # Перевірка зіткнення з іншим ворогом попереду (який ближче до бази котів)
            elif i > 0:
                front_enemy = sorted_enemies[i - 1]
                if enemy.rect.left <= front_enemy.rect.right + 2:  # 2 пікселі зазору
                    enemy.is_blocked = True
                    enemy.rect.left = front_enemy.rect.right + 2

            # Перевірка зіткнення з котами (ближній бій або бос зупиняються перед котами)
            if not enemy.ranged or enemy == self.boss:
                hit_cats = pygame.sprite.spritecollide(enemy, self.cats, False)
                if hit_cats:
                    enemy.is_blocked = True

        # =====================================================================
        # 3. ОНОВЛЕННЯ РУХУ ТА АТАК
        # =====================================================================
        # Оновлення котів
        for cat in self.cats:
            if isinstance(cat, RangedCat):
                cat.tick_reload()
                cat.update(self.enemies)
                if cat.can_shoot():
                    self.bullets.append(Bullet(cat.rect.right, cat.rect.y, cat.atk, cat.range_dist))
                    cat.reset_reload()
            else:
                cat.update()

        # Ближній бій
        for cat in self.cats:
            hit_enemies = pygame.sprite.spritecollide(cat, self.enemies, False)
            for enemy in hit_enemies:
                eid, cid = id(enemy), id(cat)
                if not isinstance(cat, RangedCat):
                    if now - cat.last_attack_time.get(eid, 0) >= 0.5:
                        enemy.hp -= cat.atk
                        cat.last_attack_time[eid] = now
                if not enemy.ranged or enemy == self.boss:
                    if now - enemy.last_attack_time.get(cid, 0) >= 0.5:
                        cat.hp -= enemy.atk
                        enemy.last_attack_time[cid] = now

        # Атака бази ворога
        if not self.boss_spawned or self.boss_defeated:
            for cat in self.cats:
                if cat.rect.colliderect(self.enemy_base.rect):
                    if now - cat.last_attack_time.get('base', 0) >= 0.5:
                        self.enemy_base.damage(cat.atk)
                        cat.last_attack_time['base'] = now

        # Оновлення ворогів (тепер вони враховують свій флаг self.is_blocked)
        for enemy in self.enemies:
            enemy.update()
            if enemy.ranged and enemy != self.boss:
                for cat in self.cats:
                    if -enemy.range_dist < (enemy.rect.left - cat.rect.right) < 0:
                        cat.hp -= enemy.atk
                        break
            if enemy.rect.colliderect(self.player_base.rect):
                if now - enemy.last_attack_time.get(id(enemy), 0) >= 0.5:
                    self.player_base.damage(enemy.atk)
                    enemy.last_attack_time[id(enemy)] = now

        # Кулі
        for b in self.bullets: b.update()
        self.bullets = [b for b in self.bullets if b.active]
        for b in self.bullets:
            # 1. Перевірка влучання у ворогів
            hit_enemy = False
            for e in self.enemies:
                if b.rect.colliderect(e.rect):
                    e.hp -= b.dmg
                    b.active = False
                    hit_enemy = True
                    break

            # 2. Якщо куля не влучила у ворога, перевіряємо влучання у БАЗУ ворога
            if not hit_enemy and b.active:
                # Базу можна атакувати далекобійними котами лише якщо бос ще не вийшов, або вже подоланий
                if not self.boss_spawned or self.boss_defeated:
                    if b.rect.colliderect(self.enemy_base.rect):
                        self.enemy_base.damage(b.dmg)
                        b.active = False

        # Видалення мертвих
        for sprite in list(self.all_units):
            if sprite.is_dead():
                self.cats.remove(sprite)
                self.enemies.remove(sprite)
                self.all_units.remove(sprite)
                if sprite == self.boss:
                    self.boss_defeated = True
                    self.enemy_base.hp = 1

    def draw_cat_menu(self):
        pygame.draw.rect(self.screen, (80, 80, 180),
                         (self.menu_x - 10, self.menu_y - 10, self.boxw * len(ALLY_TYPES) + 20, 78), 0, 8)
        for i, st in enumerate(ALLY_TYPES):
            rect = pygame.Rect(self.menu_x + i * self.boxw, self.menu_y, self.boxw - 6, 68)
            highlight = 4 if self.selected_cat == i else 0
            pygame.draw.rect(self.screen, (230, 230, 255), rect, 0, 8)
            pygame.draw.rect(self.screen, (30, 60, 190), rect, highlight, 8)

            self.screen.blit(self.menu_icons[i], (rect.x + 8, rect.y + 14))

            t1 = self.font_small.render(st['name'], True, (0, 0, 0))
            t2 = self.font_small.render(f"Ціна: {st['cost']}", True, (30, 90, 70))
            self.screen.blit(t1, (rect.x + 55, rect.y + 12))
            self.screen.blit(t2, (rect.x + 55, rect.y + 36))
            if st.get("ranged", False):
                self.screen.blit(self.font_small.render("Дист.", True, (140, 40, 40)),
                                 (rect.x + rect.width - 50, rect.y + 12))

    def cat_menu_hit(self, mx, my):
        if self.menu_y <= my <= self.menu_y + 68:
            for i in range(len(ALLY_TYPES)):
                if self.menu_x + i * self.boxw <= mx < self.menu_x + (i + 1) * self.boxw - 6:
                    return i
        return None

    def draw_upgrade_btn(self):
        upg_y = HEIGHT - 165
        ulevel = self.energy_upgrade_level
        self.screen.blit(
            self.font_small.render(f"Прокачка енергії: {ulevel}/{len(ENERGY_UPGRADES)}", True, (40, 70, 220)),
            (20, upg_y))
        rect = pygame.Rect(20, upg_y + 22, 280, 48)
        if ulevel < len(ENERGY_UPGRADES):
            nxt = ENERGY_UPGRADES[ulevel]
            btn_color = (140, 220, 220) if self.energy >= nxt["cost"] else (180, 180, 180)
            pygame.draw.rect(self.screen, btn_color, rect, 0, 6)
            pygame.draw.rect(self.screen, (80, 120, 220), rect, 2, 6)
            self.screen.blit(self.font_small.render(f"Покращити за {nxt['cost']}е", True, (0, 0, 0)),
                             (rect.x + 10, rect.y + 5))
            self.screen.blit(
                self.font_small.render(f"МАКС {nxt['new_max']}, x{nxt['mult']:.2f} реген", True, (30, 90, 170)),
                (rect.x + 10, rect.y + 26))
        else:
            pygame.draw.rect(self.screen, (110, 220, 110), rect, 0, 6)
            pygame.draw.rect(self.screen, (60, 170, 100), rect, 2, 6)
            self.screen.blit(self.font_small.render("Досягнуто ліміту!", True, (30, 120, 60)),
                             (rect.x + 10, rect.y + 14))
        self.upgrade_btn_rect = rect

    def draw_special_btn(self):
        rect = pygame.Rect(WIDTH - 340, HEIGHT - 143, 320, 48)
        cd = max(0, SPECIAL_ATTACK_COOLDOWN - (time.time() - self.last_special_time))
        btn_color = (245, 160, 40) if self.energy >= SPECIAL_ATTACK_COST and cd == 0 else (170, 150, 100)

        pygame.draw.rect(self.screen, btn_color, rect, 0, 6)
        pygame.draw.rect(self.screen, (170, 100, 40), rect, 2, 6)
        txt = f"УЛЬТА (КД {cd:.0f} сек)" if cd > 0 else "УЛЬТА: Атака!"
        self.screen.blit(self.font_small.render(txt, True, (0, 0, 0)), (rect.x + 15, rect.y + 6))
        self.screen.blit(self.font_small.render("750 е: -100 HP всім ворогам", True, (80, 0, 60)),
                         (rect.x + 15, rect.y + 26))
        self.special_btn_rect = rect

    def draw(self):
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill(WHITE)

        pygame.draw.line(self.screen, (100, 100, 100), (0, PATH_LEVEL), (WIDTH, PATH_LEVEL), 4)

        self.player_base.draw(self.screen)
        self.enemy_base.draw(self.screen)
        self.all_units.draw(self.screen)
        for b in self.bullets: b.draw(self.screen)

        self.screen.blit(self.font.render(f"База: {max(self.player_base.hp, 0)}", True, (0, 0, 0)), (20, 20))
        self.screen.blit(self.font.render(f"База ворога: {max(self.enemy_base.hp, 0)}", True, (0, 0, 0)),
                         (WIDTH - 300, 20))
        self.screen.blit(self.font.render(f"Енергія: {int(self.energy)} / {self.energy_max}", True, (0, 80, 200)),
                         (20, 55))

        spawn_cooldown = max(0, SPAWN_COOLDOWN - (time.time() - self.last_spawn_time))
        cd_txt = f"КД випуску: {spawn_cooldown:.1f} сек" if spawn_cooldown > 0 else "Юніт готовий (Шпація)!"
        self.screen.blit(self.font_small.render(cd_txt, True, (160, 80, 0)), (20, 95))

        self.draw_upgrade_btn()
        self.draw_cat_menu()
        self.draw_special_btn()

        if self.boss and not self.boss_defeated and self.boss in self.enemies:
            bx, by, w = self.boss.rect.x, self.boss.rect.y - 38, BOSS_STATS["size"]
            pygame.draw.rect(self.screen, (180, 160, 20), (bx, by, w, 22), 0, 6)
            pygame.draw.rect(self.screen, (0, 0, 0), (bx, by, w, 22), 2, 6)
            pygame.draw.rect(self.screen, (50, 200, 20),
                             (bx, by, min(max(self.boss.hp, 0) / BOSS_STATS["hp"] * w, w), 22), 0, 6)
            self.screen.blit(self.font_small.render("БОС", True, (90, 60, 0)), (bx + 6, by - 22))

        if self.enemy_base.hp <= 0 and self.boss_defeated:
            self.screen.blit(self.font.render("ПЕРЕМОГА! Боса подолано.", True, (0, 180, 0)),
                             (WIDTH // 2 - 180, HEIGHT // 3))
        elif self.player_base.hp <= 0:
            self.screen.blit(self.font.render("Поразка!", True, (200, 0, 0)), (WIDTH // 2 - 60, HEIGHT // 3))

        pygame.display.flip()

    def run(self):
        while self.running:
            if self.enemy_base.hp <= 0 and not self.boss_spawned:
                self.spawn_boss()
            self.handle_events()
            if not (self.player_base.hp <= 0 or (self.enemy_base.hp <= 0 and self.boss_defeated)):
                self.energy = min(self.energy + self.energy_regen, self.energy_max)
                self.spawn_enemies()
                self.update_units()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

if __name__ == "__main__":
    Game().run()
