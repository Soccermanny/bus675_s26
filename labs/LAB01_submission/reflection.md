# Reflection: OOP Design Decisions

## Why I Structured the Classes This Way

The core of the game rests on a `Character` base class that captures everything
shared by the player and every enemy: a name, hit points, strength, and defense.
Putting those attributes, and the d20 `attack()` logic, in one place means I
never have to re-write the same combat math for each creature type. Both `Player`
and `Enemy` inherit `Character` and only add what makes them distinct. `Player`
gets an inventory and experience points; `Enemy` gets an `xp_value` and a loot
list.

## Where Method Overriding Earned Its Keep

The clearest payoff came with `ZombieDean`. Every enemy uses `Character.attack()`,
but the Dean needed critical-strike behavior — a roll of 18 or higher on the d20
pays out double dice. Rather than adding an `if isinstance(enemy, ZombieDean)`
branch inside `Combat`, I overrode `attack()` directly on the `ZombieDean` class.
The Combat loop calls `enemy.attack(player)` without knowing anything about what
kind of enemy it is; Python's dynamic dispatch routes the call to the right
method automatically. The same pattern applies to the flavor-text each zombie
type prints when it attacks, override once, forget about it everywhere else.

## The Challenge of Cross-Object State

The trickiest design problem was the rooftop exit. The win condition requires the
`Game` object to add a connection to `admin_building` after the `ZombieDean` is
defeated inside `Combat`. That means `Game` must hold references to both
`admin_building` and `rooftop` from the moment `create_world()` returns, so that
`initiate_combat()` can reach in and call `admin_building.add_connection()`.
Managing those cross-object references and deciding which object *owns* which piece
of state, is one of the genuine design challenges. If I had more time
