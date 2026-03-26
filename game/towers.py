from dataclasses import dataclass
from typing import Optional, List
from game.utils import Point
from game.effects import Effect
from game.creatures import Creature


@dataclass
class Tower:
    damage: int
    range: float
    level: int
    cost: int
    position: Point
    effect: Optional[Effect] = None  # 0..1 effect

    def apply_effect(self, effect: Effect):
        self.effect = effect

    def upgrade(self):
        self.level += 1
        self.damage = int(self.damage * 1.3)
        self.range = self.range * 1.1

    def attack(self, creatures: List[Creature]):
        # Trouver les créatures dans la portée
        cibles = []
        for c in creatures:
            dx = c.position.x - self.position.x
            dy = c.position.y - self.position.y
            distance = (dx*dx + dy*dy) ** 0.5

            if distance <= self.range:
                cibles.append(c)

        if not cibles:
            return

        # Ciblage simple : première créature
        cible = cibles[0]

        # Infliger les dégâts
        cible.hp -= self.damage

        if cible.hp <= 0:
            cible.alive = False

        # Appliquer un effet si présent
        if self.effect:
            self.effect.apply(cible)
