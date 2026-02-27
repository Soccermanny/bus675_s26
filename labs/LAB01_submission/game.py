"""
Lab 1: Text-Based Adventure RPG
================================
Manuel Lara

Build your game here! This file contains all the starter code from the lab notebook.
Fill in the TODOs, add your own classes, and make it your own.

Run with: python game.py
"""

import random


# =============================================================================
# Dice Utilities
# =============================================================================

def roll_d20():
    """Roll a 20-sided die."""
    return random.randint(1, 20)


def roll_dice(num_dice, sides):
    """Roll multiple dice and return the total. E.g., roll_dice(2, 6) for 2d6."""
    return sum(random.randint(1, sides) for _ in range(num_dice))


# =============================================================================
# Item Classes
# =============================================================================

class Item:
    """Base class for all usable items."""

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def use(self, character):
        print(f"  Used {self.name}.")


class HealthPotion(Item):
    """Restores 15 HP when consumed."""

    def __init__(self):
        super().__init__("Health Potion", "A glowing red vial. Restores 15 HP.")
        self.heal_amount = 15

    def use(self, character):
        print("  You gulp down the Health Potion. Wounds close up.")
        old_hp = character.health
        character.health = min(character.max_health, character.health + self.heal_amount)
        print(f"  ✨ Healed {character.health - old_hp} HP!  (HP: {character.health}/{character.max_health})")


class CoffeeMug(Item):
    """Cold campus coffee — disgusting but restorative (8 HP)."""

    def __init__(self):
        super().__init__("Campus Coffee", "Cold, burnt campus coffee. Restores 8 HP. Tastes awful.")
        self.heal_amount = 8

    def use(self, character):
        print("  You chug the cold, bitter campus coffee. Disgusting. Effective.")
        old_hp = character.health
        character.health = min(character.max_health, character.health + self.heal_amount)
        print(f"  ☕ Healed {character.health - old_hp} HP!  (HP: {character.health}/{character.max_health})")


class BaseballBat(Item):
    """Permanently boosts STR by 3 when equipped."""

    def __init__(self):
        super().__init__("Baseball Bat", "Aluminum bat from the gym closet. Permanently +3 STR.")
        self.bonus = 3

    def use(self, character):
        character.strength += self.bonus
        print(f"  ⚾ You grip the baseball bat! STR boosted by {self.bonus}! (STR: {character.strength})")


class EnergyDrink(Item):
    """Restores 10 HP. Tastes like battery acid."""

    def __init__(self):
        super().__init__("Energy Drink", "Restores 10 HP. Tastes like battery acid.")

    def use(self, character):
        heal = min(10, character.max_health - character.health)
        character.health += heal
        print(f"  {character.name} slams the energy drink and recovers {heal} HP!  ({character.health}/{character.max_health})")


class FirstAidKit(Item):
    """Restores 20 HP."""

    def __init__(self):
        super().__init__("First Aid Kit", "Restores 20 HP.")

    def use(self, character):
        heal = min(20, character.max_health - character.health)
        character.health += heal
        print(f"  {character.name} patches up and recovers {heal} HP!  ({character.health}/{character.max_health})")


# =============================================================================
# Character Classes
# =============================================================================

class Character:
    """Base class for all characters in the game."""

    def __init__(self, name, health, strength, defense):
        self.name = name
        self.health = health
        self.max_health = health
        self.strength = strength
        self.defense = defense

    def is_alive(self):
        """Return True if health > 0."""
        return self.health > 0

    def take_damage(self, amount):
        """Reduce health by amount, minimum 0."""
        self.health = max(0, self.health - amount)
        print(f"  {self.name} takes {amount} damage!  (HP: {self.health}/{self.max_health})")

    def attack(self, target):
        """
        D20 combat:
          roll d20 + strength vs target defense
          on hit: deal 1d6 + strength damage
        """
        roll = roll_d20()
        attack_total = roll + self.strength
        print(f"  {self.name} rolls {roll} + {self.strength} STR = {attack_total}  vs  DEF {target.defense}")
        if attack_total > target.defense:
            damage = roll_dice(1, 6) + self.strength
            print(f"  🎯 HIT! Deals {damage} damage!")
            target.take_damage(damage)
        else:
            print(f"  💨 MISS! {target.name} dodges the attack!")

    def _hp_bar(self):
        filled = int((self.health / self.max_health) * 10)
        return "█" * filled + "░" * (10 - filled)

    def __str__(self):
        return f"{self.name}  [{self._hp_bar()}]  {self.health}/{self.max_health} HP"


class Player(Character):
    """The player character. Has an inventory and gains XP."""

    STR_UPGRADE_COST = 20   # XP cost per +1 STR
    HP_UPGRADE_COST  = 10   # XP cost per +1 max HP
    HEAL_COST        = 10   # XP cost to recover 10 HP
    MAX_BONUS        = 8    # cap on bonus STR and bonus max HP

    def __init__(self, name):
        super().__init__(name, health=30, strength=5, defense=12)
        self.inventory  = []
        self.xp         = 0
        self.str_bonus  = 0   # bonus STR from XP (max MAX_BONUS)
        self.hp_bonus   = 0   # bonus max HP from XP (max MAX_BONUS)

    def pick_up(self, item):
        """Add item to inventory."""
        self.inventory.append(item)
        print(f"  \u2705 Picked up: {item.name} \u2014 {item.description}")

    def use_item(self, item_name):
        """Find and use an item by name (case-insensitive)."""
        for item in self.inventory:
            if item.name.lower() == item_name.lower():
                item.use(self)
                self.inventory.remove(item)
                return True
        print(f"  \u274c You don't have '{item_name}' in your inventory.")
        return False

    def show_inventory(self):
        """Print all items in the inventory."""
        if not self.inventory:
            print("  \U0001f392 Your backpack is empty.")
        else:
            print("\n  \U0001f392 INVENTORY:")
            for item in self.inventory:
                print(f"     - {item.name}: {item.description}")

    def gain_xp(self, amount):
        self.xp += amount
        print(f"  \u2b50 Gained {amount} XP!  (Total: {self.xp} XP)")


class Enemy(Character):
    """Base class for all enemies. Carries XP value and optional loot."""

    def __init__(self, name, health, strength, defense, xp_value=10, loot=None):
        super().__init__(name, health, strength, defense)
        self.xp_value = xp_value
        self.loot = loot if loot is not None else []


class Zombie(Enemy):
    """Basic minion enemy \u2014 slow but numerous."""

    NAMES = ["Freshman Zombie", "Zombie TA", "Zombie Barista", "Zombie Janitor"]

    def __init__(self):
        super().__init__(
            name=random.choice(Zombie.NAMES),
            health=15, strength=3, defense=8, xp_value=10
        )

    def attack(self, target):
        print(f"  \U0001f9df {self.name} groans and claws at {target.name}!")
        super().attack(target)


class ZombieProfessor(Enemy):
    """Elite enemy \u2014 tougher and angrier. Drops a Health Potion on defeat."""

    def __init__(self):
        super().__init__(
            name="Zombie Professor",
            health=25, strength=5, defense=12, xp_value=25,
            loot=[HealthPotion()]
        )

    def attack(self, target):
        print(f"  \U0001f4bc {self.name} screeches "
              f"'OFFICE HOURS ARE CANCELLED... FOREVER!' and lunges!")
        super().attack(target)


class ZombieDean(Enemy):
    """Final boss. Critical strike on any roll >= 18 (2d6 + STR damage)."""

    def __init__(self):
        super().__init__(
            name="Dean of the Dead",
            health=50, strength=7, defense=15, xp_value=100
        )

    def attack(self, target):
        roll = roll_d20()
        if roll >= 18:
            damage = roll_dice(2, 6) + self.strength
            print(f"  \U0001f454 {self.name} roars 'YOUR TUITION IS DUE!' \u2014 CRITICAL STRIKE!")
            print(f"  \U0001f4a5 Double-dice damage! Deals {damage} damage!")
            target.take_damage(damage)
        else:
            print(f"  \U0001f454 {self.name} fumbles with budget reports, then attacks!")
            super().attack(target)


# =============================================================================
# Location Class
# =============================================================================

class Location:
    """A location in the game world."""

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.connections = {}  # {"north": Location, "south": Location, etc.}
        self.enemies = []      # List of enemies in this location
        self.items = []        # List of items in this location

    def describe(self):
        """Print a full description of the location."""
        print(f"\n{'='*50}")
        print(f"📍 {self.name}")
        print(f"{'='*50}")
        print(self.description)

        # Enemies
        alive = [e for e in self.enemies if e.is_alive()]
        if alive:
            print(f"\n  Enemies:")
            for e in alive:
                print(f"    - {e.name}  (HP: {e.health}/{e.max_health})")

        # Items — each on its own line so they're clearly visible
        if self.items:
            print(f"\n  Items you can pick up:")
            for item in self.items:
                print(f"    - {item.name}: {item.description}")
        else:
            print(f"\n  No items on the ground.")

        # Exits
        exits = self.get_exits()
        if exits:
            print(f"\n  Exits: {', '.join(exits)}")
        else:
            print(f"\n  Exits: none")

    def get_exits(self):
        """Return a list of available directions."""
        return list(self.connections.keys())

    def add_connection(self, direction, location):
        """Connect this location to another."""
        self.connections[direction] = location


# =============================================================================
# World Builder
# =============================================================================

def create_world():
    """
    Create and connect all 5 campus locations.
    Returns (starting_location, admin_building, rooftop).

    Map:
      [Dorm] --east--> [Quad] --south--> [Science Bldg]
                          |
                        north
                          |
                      [Library] --north--> [Admin Bldg] --up--> [Rooftop]
    """

    dorm = Location(
        "Student Dorm \u2014 Room 101",
        "  Your dorm room. Textbooks, empty energy cans, a laptop frozen on Zoom.\n"
        "  Distant groaning echoes from the hallway. There's a bat in the corner."
    )

    quad = Location(
        "The Quad",
        "  Overturned benches, scattered backpacks. A zombie in a graduation cap\n"
        "  shambles past a knocked-over coffee cart."
    )

    science_building = Location(
        "Science Building",
        "  Flickering fluorescent lights over toppled lab equipment.\n"
        "  A whiteboard still reads: 'Exam Friday \u2014 no excuses.'"
    )

    library = Location(
        "Campus Library",
        "  Eerie silence \u2014 interrupted by shuffling. Fallen bookshelves form a maze.\n"
        "  A handwritten sign: 'KEEP QUI\u2014 AAAGHHH.'"
    )

    admin_building = Location(
        "Administration Building",
        "  Mahogany desks, motivational posters, and one very undead Dean.\n"
        "  The rooftop stairwell door is behind his chair \u2014 locked until he falls."
    )

    rooftop = Location(
        "\U0001f681 Rooftop Helipad",
        "  Wind whips across the roof. A rescue helicopter idles on the pad!\n"
        "  The pilot waves you aboard \u2014 YOU MADE IT!"
    )
    rooftop.is_escape = True

    # Connect locations
    dorm.add_connection("east", quad)
    quad.add_connection("west", dorm)

    quad.add_connection("south", science_building)
    science_building.add_connection("north", quad)

    quad.add_connection("north", library)
    library.add_connection("south", quad)

    library.add_connection("north", admin_building)
    admin_building.add_connection("south", library)

    # Rooftop unlocked dynamically after defeating the Dean

    # Place enemies
    quad.enemies.append(Zombie())
    quad.enemies.append(Zombie())
    science_building.enemies.append(Zombie())
    science_building.enemies.append(ZombieProfessor())
    library.enemies.append(Zombie())
    library.enemies.append(Zombie())
    admin_building.enemies.append(ZombieDean())

    # Place items (max 5 per room)
    dorm.items    = [CoffeeMug(), BaseballBat(), EnergyDrink()]
    quad.items    = [HealthPotion(), EnergyDrink()]
    science_building.items = [EnergyDrink(), FirstAidKit()]
    library.items = [HealthPotion(), EnergyDrink(), FirstAidKit()]
    admin_building.items   = [HealthPotion()]

    return dorm, admin_building, rooftop


# =============================================================================
# Combat System
# =============================================================================

class Combat:
    """Manages turn-based combat between player and enemy."""

    # Combat states
    PLAYER_TURN = "player_turn"
    ENEMY_TURN = "enemy_turn"
    COMBAT_END = "combat_end"

    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.state = Combat.PLAYER_TURN
        self.combat_log = []

    def start(self):
        """Run combat until it ends. Returns 'victory', 'defeat', or 'fled'."""
        print(f"\n  {'=' * 50}")
        print(f"  COMBAT: {self.player.name}  vs  {self.enemy.name}")
        print(f"  {'=' * 50}")

        while self.state != Combat.COMBAT_END:
            if self.state == Combat.PLAYER_TURN:
                self.player_turn()
            elif self.state == Combat.ENEMY_TURN:
                self.enemy_turn()

        return self.get_result()

    def player_turn(self):
        """Handle player's turn: attack / use item / check inventory / run."""
        print(f"\n  {self.player}")
        print(f"  {self.enemy}")
        print("\n  Actions: attack  |  use [item]  |  inventory  |  run")
        action = input("  > ").lower().strip()
        parts = action.split()
        cmd = parts[0] if parts else ""

        if cmd == "attack":
            self.player.attack(self.enemy)
            if not self.enemy.is_alive():
                print(f"\n  {self.enemy.name} has been defeated!")
                self.state = Combat.COMBAT_END
            else:
                self.state = Combat.ENEMY_TURN

        elif cmd == "use" and len(parts) > 1:
            self.player.use_item(" ".join(parts[1:]))
            self.state = Combat.ENEMY_TURN  # using an item costs your turn

        elif cmd in ["inventory", "i"]:
            self.player.show_inventory()  # peeking is free

        elif cmd == "run":
            if random.random() < 0.5:
                print("  You manage to escape!")
                self.state = Combat.COMBAT_END
            else:
                print("  Blocked! Couldn't escape!")
                self.state = Combat.ENEMY_TURN

        else:
            print("  Unknown action. Try 'attack', 'use [item]', or 'run'.")

    def enemy_turn(self):
        """Enemy attacks the player automatically."""
        print(f"\n  {self.enemy.name}'s turn...")
        self.enemy.attack(self.player)

        if not self.player.is_alive():
            print()
            print("  ╔══════════════════════════════╗")
            print("  ║        Y O U  D I E D !      ║")
            print("  ╚══════════════════════════════╝")
            self.state = Combat.COMBAT_END
        else:
            self.state = Combat.PLAYER_TURN

    def get_result(self):
        """Return 'victory', 'defeat', or 'fled'."""
        if not self.enemy.is_alive():
            return "victory"
        elif not self.player.is_alive():
            return "defeat"
        else:
            return "fled"


# =============================================================================
# Main Game Class
# =============================================================================

class Game:
    """Main game controller — manages state, world, and player loop."""

    # Game states
    EXPLORING = "exploring"
    GAME_OVER  = "game_over"
    VICTORY    = "victory"

    def __init__(self):
        self.player           = None
        self.current_location = None
        self.admin_building   = None   # stored so we can unlock the exit later
        self.rooftop          = None   # win location
        self.state            = Game.EXPLORING
        self.game_running     = True

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def start(self):
        """Initialize and run the game."""
        self.show_intro()
        self.create_player()
        start_loc, self.admin_building, self.rooftop = create_world()
        self.current_location = start_loc
        self.current_location.describe()

        while self.game_running:
            if self.state == Game.EXPLORING:
                self.exploration_loop()
            elif self.state == Game.GAME_OVER:
                self.show_game_over()
                break
            elif self.state == Game.VICTORY:
                self.show_victory()
                break

    def show_intro(self):
        """Print the opening screen."""
        print("\n" + "=" * 60)
        print("      D E A D   C R E D I T S")
        print("       A Campus Zombie Survival")
        print("=" * 60)
        print("\nThe semester was already brutal — now the faculty have turned.")
        print("Groaning professors stalk the hallways. The Dean himself has")
        print("become something unspeakable.")
        print("\nYour only hope: fight through campus, defeat the Dean of the")
        print("Dead, and reach the rooftop where a rescue helicopter waits.")
        print("\nGood luck. You'll need every credit.")
        print("=" * 60)

    def create_player(self):
        """Prompt for a name and create the player."""
        print("\nWhat's your name, survivor?")
        name = input("  > ").strip() or "Student"
        self.player = Player(name)
        print(f"\nAlright, {name}. Let's try to survive this semester.")
        self.show_help()

    # ------------------------------------------------------------------
    # Exploration
    # ------------------------------------------------------------------

    def exploration_loop(self):
        """Read and dispatch one exploration command."""
        print("\nWhat do you do?  (type 'help' for commands)")
        command = input("  > ").lower().strip()
        parts   = command.split()
        if not parts:
            return
        action = parts[0]

        if action == "help":
            self.show_help()

        elif action == "look":
            self.current_location.describe()

        elif action == "go" and len(parts) > 1:
            self.move(parts[1])

        elif action in ["north", "south", "east", "west", "up", "down"]:
            self.move(action)

        elif action in ["fight", "attack"]:
            self.initiate_combat()

        elif action in ["get", "take", "pick"] and len(parts) > 1:
            self.pick_up_item(" ".join(parts[1:]))

        elif action in ["use"] and len(parts) > 1:
            self.player.use_item(" ".join(parts[1:]))

        elif action in ["inventory", "i"]:
            self.player.show_inventory()

        elif action == "status":
            print(f"\n  {self.player}")

        elif action == "quit":
            print("\n  Giving up already?  Goodbye.")
            self.game_running = False

        else:
            print("  Unknown command. Type 'help' for options.")

    def move(self, direction):
        """Move the player; auto-fight if enemies present; check win room."""
        exits = self.current_location.get_exits()
        if direction not in exits:
            print(f"  You can't go {direction} from here.")
            return

        next_loc = self.current_location.connections[direction]

        # Block the 'up' exit until it is unlocked by the Game
        if next_loc == self.rooftop and "up" not in self.current_location.connections:
            print("  The roof door is locked tight. There must be a way to open it...")
            return

        self.current_location = next_loc
        print(f"\n  You move {direction}...")
        self.current_location.describe()

        # Victory room check
        if self.current_location == self.rooftop:
            self.state = Game.VICTORY
            return

        # Auto-initiate combat if enemies are present
        if self.current_location.enemies:
            print("\n  Enemies are here! You'll have to fight your way through.")
            self.initiate_combat()

    def pick_up_item(self, item_name):
        """Pick up a named item from the current location (inventory cap 5)."""
        if len(self.player.inventory) >= 5:
            print("  Your inventory is full (max 5 items). Use or drop something first.")
            return
        item_name_lower = item_name.lower()
        for item in self.current_location.items:
            if item_name_lower in item.name.lower():
                self.player.pick_up(item)
                self.current_location.items.remove(item)
                return
        print(f"  There's no '{item_name}' here to pick up.")

    def initiate_combat(self):
        """Fight the first living enemy in this room."""
        alive = [e for e in self.current_location.enemies if e.is_alive()]
        if not alive:
            print("  There's nothing left to fight here.")
            return

        enemy  = alive[0]
        battle = Combat(self.player, enemy)
        result = battle.start()

        if result == "victory":
            self.current_location.enemies.remove(enemy)
            self.player.gain_xp(enemy.xp_value)
            print(f"  XP gained: {enemy.xp_value}  |  Total XP: {self.player.xp}")

            # Drop loot into room (respect 5-item cap)
            for loot_item in enemy.loot:
                if len(self.current_location.items) < 5:
                    self.current_location.items.append(loot_item)
                    print(f"  {enemy.name} dropped: {loot_item.name}")

            # Boss check — ZombieDean unlocks the rooftop escape route
            if isinstance(enemy, ZombieDean):
                print("\n  With the Dean gone, the emergency roof door clicks open.")
                self.admin_building.add_connection("up", self.rooftop)

            # Offer XP upgrades
            self.xp_upgrade_prompt()

            # Showcase items in the room
            if self.current_location.items:
                print(f"\n  --- Items in this room ---")
                for item in self.current_location.items:
                    print(f"    - {item.name}: {item.description}")
                print("  (use 'get [item]' to pick one up)")

        elif result == "defeat":
            self.state = Game.GAME_OVER

    # ------------------------------------------------------------------
    # XP Upgrade System
    # ------------------------------------------------------------------

    def xp_upgrade_prompt(self):
        """
        After a combat victory, let the player spend XP on permanent upgrades.
        Caps: +8 bonus STR total, +8 bonus max HP total.
        """
        p = self.player
        print(f"\n  ~~~ SPEND XP ~~~  (available: {p.xp} XP)")
        while True:
            str_left = Player.MAX_BONUS - p.str_bonus
            hp_left  = Player.MAX_BONUS - p.hp_bonus
            print(f"\n  [1] +1 STR          ({Player.STR_UPGRADE_COST} XP)  "
                  f"— current STR: {p.strength}  |  bonus left: {str_left}/{Player.MAX_BONUS}")
            print(f"  [2] +1 Max HP       ({Player.HP_UPGRADE_COST} XP)  "
                  f"— current max HP: {p.max_health}  |  bonus left: {hp_left}/{Player.MAX_BONUS}")
            print(f"  [3] Recover 10 HP   ({Player.HEAL_COST} XP)  "
                  f"— current HP: {p.health}/{p.max_health}")
            print(f"  [0] Done            (XP remaining: {p.xp})")
            choice = input("  > ").strip()

            if choice == "1":
                if p.xp < Player.STR_UPGRADE_COST:
                    print(f"  Not enough XP (need {Player.STR_UPGRADE_COST}).")
                elif str_left <= 0:
                    print(f"  STR is maxed out (cap: +{Player.MAX_BONUS}).")
                else:
                    p.xp        -= Player.STR_UPGRADE_COST
                    p.strength  += 1
                    p.str_bonus += 1
                    print(f"  STR increased to {p.strength}!  (XP remaining: {p.xp})")

            elif choice == "2":
                if p.xp < Player.HP_UPGRADE_COST:
                    print(f"  Not enough XP (need {Player.HP_UPGRADE_COST}).")
                elif hp_left <= 0:
                    print(f"  Max HP is maxed out (cap: +{Player.MAX_BONUS}).")
                else:
                    p.xp         -= Player.HP_UPGRADE_COST
                    p.max_health += 1
                    p.health      = min(p.health + 1, p.max_health)
                    p.hp_bonus   += 1
                    print(f"  Max HP increased to {p.max_health}!  (XP remaining: {p.xp})")

            elif choice == "3":
                if p.xp < Player.HEAL_COST:
                    print(f"  Not enough XP (need {Player.HEAL_COST}).")
                else:
                    heal   = min(10, p.max_health - p.health)
                    p.xp  -= Player.HEAL_COST
                    p.health += heal
                    print(f"  Recovered {heal} HP!  ({p.health}/{p.max_health})  (XP remaining: {p.xp})")

            elif choice == "0":
                break
            else:
                print("  Enter 1, 2, 3, or 0.")

    # ------------------------------------------------------------------
    # Help / End screens
    # ------------------------------------------------------------------

    def show_help(self):
        """Print the command reference."""
        print("\n  COMMANDS")
        print("  --------")
        print("  go [dir] / [dir]  -- Move (north south east west up down)")
        print("  look              -- Describe current location")
        print("  fight             -- Attack an enemy here")
        print("  get [item]        -- Pick up an item")
        print("  use [item]        -- Use an item from inventory")
        print("  inventory / i     -- List carried items")
        print("  status            -- Show HP and stats")
        print("  help              -- Show this list")
        print("  quit              -- Exit the game")

    def show_game_over(self):
        """Print the defeat screen."""
        print("\n" + "=" * 60)
        print("              F A I L E D   C O U R S E")
        print("=" * 60)
        if self.player:
            print(f"\n  {self.player.name} fell to the undead.")
            print(f"  XP earned: {self.player.xp}")
        print("\n  The zombies were too many. The campus is lost.")
        print("  Better luck next enrollment period...")
        print("=" * 60)

    def show_victory(self):
        """Print the win screen."""
        print("\n" + "=" * 60)
        print("         D E G R E E   C O N F E R R E D")
        print("=" * 60)
        if self.player:
            xp = self.player.xp
            print(f"\n  {self.player.name} bursts through the roof door.")
        print("\n  The helicopter drops from the clouds. You made it.")
        print("  Behind you, the campus fades into the smoke.")
        print("\n  The Dean of the Dead has been expelled. For good.")
        if self.player:
            print(f"\n  Final XP: {xp}")
        print("=" * 60)
        print("\n       Congratulations — you survived Dead Credits.\n")


# =============================================================================
# Run the Game
# =============================================================================

if __name__ == "__main__":
    game = Game()
    game.start()
