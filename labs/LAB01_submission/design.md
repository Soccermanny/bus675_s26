# Game Design Document — DEAD CREDITS: A Campus Zombie Survival

## Theme / Setting
A campus zombie apocalypse. The semester went sideways when an experimental
energy drink from the chem lab turned the faculty undead. The player is a
surviving student fighting through familiar campus locations — dorms, the quad,
science labs, the library, and the administration building — to reach a
rescue helicopter on the rooftop.

## Player's Goal
Fight through all five campus areas, defeat the Zombie Dean (the final boss),
unlock the rooftop exit, and reach the helicopter.

## Locations

```
[Dorm] --east--> [Quad] --south--> [Science Building]
                   |
                 north
                   |
              [Library] --north--> [Admin Building] --up (locked until Dean is defeated)--> [Rooftop]
```

| Location         | Enemies                           | Items                      |
|------------------|-----------------------------------|----------------------------|
| Dorm             | None (safe start)                 | Coffee Mug, Baseball Bat   |
| Quad             | 2x Zombie                         | Health Potion              |
| Science Building | 1x Zombie, 1x Zombie Professor    | —                          |
| Library          | 2x Zombie                         | —                          |
| Admin Building   | ZombieDean (boss, HP 50)          | Health Potion (boss loot)  |
| Rooftop          | None (win location)               | —                          |

## Enemies

| Class            | HP | STR | DEF | XP  | Special                                   |
|------------------|----|-----|-----|-----|-------------------------------------------|
| Zombie           | 15 |  3  |  8  |  10 | Random name, groaning attack message      |
| ZombieProfessor  | 25 |  5  | 12  |  25 | Drops Health Potion; office-hours remarks |
| ZombieDean       | 50 |  7  | 15  | 100 | BOSS — crits on d20 roll >= 18 (2d6+STR)  |

## Win Condition
Defeat ZombieDean then rooftop exit unlocks then enter Rooftop and VICTORY screen.

## Lose Condition
Player HP drops to 0 during combat → GAME OVER screen.

## Class Hierarchy

```
Item
├── HealthPotion   (heals 15 HP)
├── CoffeeMug      (heals  8 HP)
└── BaseballBat    (+3 STR permanently)

Character
├── Player         (HP 30, STR 5, DEF 12; carries inventory, earns XP)
└── Enemy          (base for all hostile NPCs; has xp_value and loot list)
    ├── Zombie
    ├── ZombieProfessor
    └── ZombieDean

Location           (name, description, connections dict, enemies list, items list)

Combat             (PLAYER_TURN → ENEMY_TURN → COMBAT_END loop)

Game               (EXPLORING / GAME_OVER / VICTORY states; owns world + player)
```

## Additional Notes
- D20 combat: `roll_d20() + attacker.strength >= target.defense` to hit;
  damage = `roll_dice(1, 6) + attacker.strength`.
- ZombieDean has an overridden `attack()` that crits (2d6+STR) on a roll >= 18.
- The 'up' exit in Admin Building starts absent; `Game.initiate_combat()` adds it
  via `admin_building.add_connection('up', rooftop)` after the Dean is defeated.
- All item pickups are done via `get [item name]` in the exploration loop;
  items are removed from `location.items` when picked up.
