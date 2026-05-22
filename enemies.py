import random
from setting import ENEMY_TYPES

def choose_enemy_type(enemy_base_hp, boss_spawned):
    if boss_spawned:
        return random.choices(ENEMY_TYPES, weights=[10, 20, 0, 0, 70])[0]

    hp = enemy_base_hp
    pool = [ENEMY_TYPES[0]]
    weights = [70]
    if hp <= 750: pool.append(ENEMY_TYPES[1]); weights.append(20)
    if hp <= 500: pool.append(ENEMY_TYPES[2]); weights.append(7)
    if hp <= 250: pool.append(ENEMY_TYPES[3]); weights.append(3)

    return random.choices(pool, weights=weights)[0]