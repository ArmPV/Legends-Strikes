from dataclasses import dataclass
from typing import Optional, List # Ajout de List pour les types de données
from game.utils import Point # Import de Point pour la position des tours
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

    def attack(self, creatures: List[Creature]):
        pass
