from typing import List
from game.creatures import Creature
from game.effects import Effect


class Wave:
    def __init__(self):
        self.creatures: List[Creature] = []
        self.bonuses: List[Effect] = []
        self.active_bonuses: List[str] = []

    def add_creature(self, creature: Creature):
        self.creatures.append(creature)

    def add_bonus(self, bonus: Effect):
        self.bonuses.append(bonus)

    def get_total_cost(self) -> int:
        return sum(c.cost for c in self.creatures)

    def get_creature_count(self) -> int:
        return len(self.creatures)
def apply_default_bonus(self):
    for creature in self.creatures:
        creature.hp += 10