# DEAD CREDITS: A Campus Zombie Survival

## Story
The end-of-semester energy drink from the chem lab turned everyone undead.
You are the last surviving student. Fight through five campus locations,
take out the Zombie Dean, and reach the rooftop for rescue.

## How to Play

### Running the Game
```bash
python game.py
```
Requires Python 3.8+. No external packages needed.

### Commands

| Command           | What it does                                      |
|-------------------|---------------------------------------------------|
| `go [direction]`  | Move north / south / east / west / up / down      |
| `[direction]`     | Shorthand — e.g. just type `north`                |
| `look`            | Re-describe the current location                  |
| `fight`           | Attack the first living enemy in this room        |
| `get [item]`      | Pick up a named item from the floor               |
| `use [item]`      | Use an item from your inventory                   |
| `inventory` / `i` | List items you are carrying                       |
| `status`          | Show your current HP, STR, and DEF                |
| `help`            | Print the full command list                       |
| `quit`            | Exit the game                                     |

### During Combat

| Action          | Effect                                      |
|-----------------|---------------------------------------------|
| `attack`        | Roll d20 + STR vs enemy DEF; deal 1d6+STR   |
| `use [item]`    | Use an inventory item (costs your turn)     |
| `inventory`     | Peek at inventory (free, no turn cost)      |
| `run`           | 50 % chance to escape combat                |

## Goal
1. Clear enemies from the Quad, Science Building, and Library.
2. Collect the Coffee Mug and Baseball Bat from your Dorm room.
3. Enter the Admin Building and defeat the **Zombie Dean** (boss, HP 50).
4. The roof door unlocks — go `up` into the Admin Building.
5. Reach the **Rooftop** to trigger the victory end-screen.

## Tips
- Pick up the **Baseball Bat** in the Dorm before leaving — it raises your STR by 3 permanently.
- Use **Health Potions** before your HP drops below 10.
- `ZombieProfessor` drops a Health Potion when defeated.
- The Zombie Dean can land critical hits (2d6 + STR) on a high roll — heal up first.
- You can `run` from regular zombies to regroup, but running costs no HP.
