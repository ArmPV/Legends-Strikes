from dataclasses import dataclass
from typing import Optional 
from game.utils import Point 
from game.effects import Effect


@dataclass
class Creature:
    hp: int
    speed: float
    cost: int
    position: Point
    maxHP: int
    effect: Optional[Effect] = None  # 0..1 effect

    def apply_effect(self, effect: Effect):
        self.effect = effect

    def update(self):
        pass
